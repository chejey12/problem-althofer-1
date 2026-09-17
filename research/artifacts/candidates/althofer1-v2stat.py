"""
althofer-1 關鍵躍進: 從 bounded evidence 到「無窮發散」的嚴格論證候選。
核心思路 (drift 論證):
n(t+1) = odd(X*n(t)+1) = (X*n(t)+1) / 2^v2(X*n+1)
log2 n(t+1) = log2 n(t) + log2 X - v2(t) * log2 2 + log2(1 + 1/(X n(t)))
對奇 n, X 奇: X*n+1 偶. v2(Xn+1) 的分佈依賴 n mod 2^k.
關鍵: X*n+1 ≡ X*n+1 (mod 8). 若 n ≡ n0 mod 2^k 保持某些 residue 類,
v2 有可能被證明總是 ≤ 2 (例如 X=7, n≡3 mod 4 → 7n+1 ≡ 22 ≡ 2 mod 4 → v2=1!)
驗證: 7*3+1 = 22 = 2·11, v2=1. 若 n(t) ≡ 3 (mod 4) 恆成立 → v2 恆 =1 →
每步嚴格乘以 7/2 = 3.5 → n(t) ≥ 3 * (7/2)^t → 發散! 完整證明!
檢查不變量: n ≡ 3 (mod 4) → 7n+1 ≡ 21+1=22 ≡ 2 (mod 4) → odd part = (7n+1)/2 ≡ 11 (mod 4)?
(7n+1)/2 mod 4: n=4a+3 → 7n+1=28a+22 → /2 = 14a+11 ≡ 2a+3 (mod 4).
當 a 偶: 14a+11 ≡ 11 ≡ 3 (mod 4) ✓; 當 a 奇: ≡ 1 (mod 4) ✗
所以 n≡3 (mod 4) 單步後不一定保持. 但 n≡3 (mod 8)?
n=8a+3: 7n+1 = 56a+22 = 2(28a+11), 28a+11 奇 → v2=1 恆!
odd part = 28a+11. 下一步仍要 ≡3 (mod 8): 28a+11 ≡ 4a+3 (mod 8).
a≡0 (mod 2) → 28a+11 ≡ 11 ≡ 3 (mod 8) ✓ 保持!
所以: n0 ≡ 3 (mod 8) 且 a=even 部分需要更精細. n=16b+3: 7n+1=112b+22=2(56b+11), 56b+11 奇 → v2=1.
56b+11 mod 16 = 8b+11 (mod 16). b 偶 → 11 ≡ 11 (mod 16)... 要 ≡ 3 (mod 16) 才保持.
看實際軌道: 3 → 22/2=11 → 78/2=39? 7*11+1=78=2·39, v2=1 → 39. 7*39+1=274=2·137 → 137.
7*137+1=960=2^6·15 → v2=6! 這裡 v2=6 大. 15: 7*15+1=106=2·53 → 53.
所以不是恆 v2=1. 實測 0.82 bits/step ≈ log2(7/4)=0.807 符合平均.
真正的證明需要處理 v2 的隨機性 — 這是 Martingale/drift 論證, 較深.
本實驗: 精確統計 v2 序列分佈 + 驗證大數定律下的正漂移, 以及 submartingale 下界論證的檢查.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone

sys.set_int_max_str_digits(2000000)


def odd_part(m: int) -> int:
    return m >> ((m & -m).bit_length() - 1)


def main():
    x, n0, steps = 7, 3, 20000
    n = n0
    v2_seq = []
    bits = []
    for s in range(steps):
        m = x * n + 1
        v = (m & -m).bit_length() - 1
        v2_seq.append(v)
        n = m >> v
        bits.append(n.bit_length())
    c = Counter(v2_seq)
    total = sum(c.values())
    v2_dist = {k: c.get(k, 0) for k in range(0, 8)}
    # 每 1000 步的 bits 增量 → 實測 drift
    drifts = []
    for i in range(0, steps - 1000, 1000):
        drifts.append(bits[i + 999] - bits[i] if i == 0 else bits[i + 999] - bits[i])
    summary = {
        'experiment': 'althofer-1 v2 sequence statistics X=7 n0=3 20000 steps',
        'x': x, 'n0': n0,
        'v2_distribution': v2_dist,
        'E_v2_observed': round(sum(k * v for k, v in c.items()) / total, 4),
        'P_v2_ge_3': round(sum(v for k, v in c.items() if k >= 3) / total, 4),
        'mean_bits_growth_per_step': round(bits[-1] / steps, 4),
        'theoretical_drift_bits': 'log2(7) - E[v2] = 2.807 - 2.0 = 0.807',
        'window_drifts_1000step': drifts[:8],
        'monotone_growth': all(b2 >= b1 for b1, b2 in zip(bits[::100], bits[100::100])),
        'note': ('v2 distribution for 7n+1 with the observed orbit stays near geometric mean 2, '
                 'giving positive drift 0.807 bits/step. A rigorous unboundedness proof would need '
                 'a lower bound on the running minimum of the drifted random walk (e.g. via '
                 'martingale concentration or a v2 tail bound), which remains the open gap.'),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
    }
    out = json.dumps(summary, ensure_ascii=False, indent=1)
    print(out[:1000])
    with open('althofer1_v2stat.json', 'w') as f:
        f.write(out)


if __name__ == '__main__':
    main()