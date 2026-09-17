"""
althofer-1 發散 witness 的嚴格性檢驗:
X=5, n0=5 的軌道沒有發散 (max_n_bits=7 表示在 20000 步內數值沒漲) — 假陽性 (可能進入循環).
X=7, n0=3: 20000 步內 max 值達 16396 bits — 這是真發散候選!
驗證: (a) 重放軌道確認每步 odd(7n+1); (b) 確認 n 單調趨勢與無循環; (c) 產生軌道摘要證書.
"""
import json
import sys
from datetime import datetime, timezone

sys.set_int_max_str_digits(2000000)


def odd_part(m: int) -> int:
    return m >> ((m & -m).bit_length() - 1)


def orbit_certificate(x: int, n0: int, steps: int):
    """重放軌道, 檢查: 奇性保持, 增長率, 週期檢測 (存 hash 環)."""
    n = n0
    seen = {}
    cycle_at = None
    trajectory_sample = []
    max_n = n
    grow_steps = 0
    for s in range(steps):
        n = odd_part(x * n + 1)
        if n in seen:
            cycle_at = (s, seen[n])
            break
        seen[n] = s
        max_n = max(max_n, n)
        if s % 1000 == 0:
            trajectory_sample.append({'step': s, 'bits': n.bit_length()})
        if s == steps - 1:
            cycle_at = None
    # 循環檢測用 dict 記憶體會爆 (20000 entries with huge ints) — 改用 bit-length 簽章近似
    return cycle_at, max_n, trajectory_sample


def main():
    x, n0, steps = 7, 3, 20000
    n = n0
    seen_hashes = set()
    orbit_hashes = []
    cycle = None
    max_bits = 0
    samples = []
    import hashlib
    for s in range(steps):
        n = odd_part(x * n + 1)
        bits = n.bit_length()
        max_bits = max(max_bits, bits)
        h = hash(n)  # Python hash of big int is deterministic
        if h in seen_hashes:
            # 需確認真碰撞 (hash 碰撞機率極低但非零) — 用精確 set 會耗記憶體, 用 hash 即可 + 記錄
            cycle = {'step': s, 'note': 'hash collision detected - possible cycle'}
            break
        seen_hashes.add(h)
        if s % 2500 == 0:
            samples.append({'step': s, 'n_bits': bits})
    summary = {
        'experiment': 'althofer-1 orbit certificate X=7 n0=3',
        'x': x, 'n0': n0, 'steps': steps,
        'no_cycle_detected_within_budget': cycle is None,
        'cycle': cycle,
        'max_n_bits': max_bits,
        'final_n_bits': bits,
        'growth_rate_bits_per_step': round(bits / steps, 3),
        'theoretical_expectation': 'log2(7/4) = 0.807 bits/step expected growth',
        'orbit_samples': samples,
        'note': ('Trajectory of odd(7n+1) from n0=3 grows ~0.8 bits/step for 20000 steps without '
                 'cycle detection (hash-based, collision negligible). This is bounded evidence of divergence; '
                 'a complete disproof witness needs a proof that growth continues unboundedly '
                 '(e.g. showing n(t) >= c * (7/4)^t for all t via v2 distribution argument).'),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
    }
    out = json.dumps(summary, ensure_ascii=False, indent=1)
    print(out[:900])
    with open('althofer1_cert.json', 'w') as f:
        f.write(out)


if __name__ == '__main__':
    main()