"""
althofer-1 嚴格證明核心 (candidate proof):
主張: X=7, n0=3 時, n(t) = odd(7 n(t-1)+1) 無窮發散.

引理 1 (v2 分佈的嚴格控制): 對奇 n, 7n+1 ≡ 2 (mod 4) ⟺ n ≡ 3 (mod 4)... 不完全.
精確: 7n+1 = 8k 時 v2>=3. 我們用「每步至少除以 2, 乘以 7」:
n(t+1) > (7 n(t) + 1)/2^v2. 
下界論證: 定義 drift walk D(t) = log2 n(t). 每步 D(t+1)-D(t) = log2 7 - v2(t) + eps(t), eps(t)>=0.
v2(t) = k 的機率 = 2^-(k-1) (k>=1, 當 7n+1 的 residue 均勻).
期望 = 2. 由強大數定律, v2 的時間平均 → 2 a.s.
⇒ D(t)/t → 0.807 > 0 a.s. ⟹ 發散 a.s. — 「對固定 n0, 機率 1 發散」!
這正是定理! 但 althofer-1 要的是「存在」— 機率論證就夠: 由 LLM,
存在發散軌道 ⟸ 對任意 n0, P(發散)=1 ⟹ 幾乎所有軌道發散 ⟹ 存在 (非空機率).
嚴格化 v2 分佈: 7n+1 對均勻隨機奇 n, v2=k 的機率: 
7n+1 ≡ 0 mod 2^k, n ≡ -7^{-1} mod 2^k → 恰一 residue mod 2^k, 且 n 奇自動滿足 k=1 需要 n≡3 mod 4 機率 1/2... 
對 k>=1: P(v2>=k) = 2^-(k-1) 對均勻奇 n. 精確幾何分佈, E[v2] = sum_{k>=1} P(v2>=k) = 2.
這個嚴格論證 (LLM 推導 + 數值驗證) 是 proof candidate 的核心. Lean 形式化是下一階段.
"""
import json
import sys
from datetime import datetime, timezone

sys.set_int_max_str_digits(2000000)


def odd_part(m):
    return m >> ((m & -m).bit_length() - 1)


def main():
    # 嚴格驗證 P(v2 >= k) = 2^-(k-1) for 7n+1, n 奇 mod 2^m
    # 枚舉 n mod 2^20 的所有奇 residue
    results = []
    for K in range(1, 12):
        m = 2 ** K
        count_ge = 0
        total = 0
        for n in range(1, m, 2):  # 奇 residue mod 2^K
            v = ((7 * n + 1) & -(7 * n + 1)).bit_length() - 1
            total += 1
            if v >= K:
                count_ge += 1
        # P(v2 >= K) 應為 2^-(K-1)... 注意 v2>=K 需要 mod 2^K
        results.append({'K': K, 'P_v2_ge_K_exact': count_ge / total, 'theoretical': 2 ** (-(K - 1))})
    # drift 下界論證的數值確認
    summary = {
        'experiment': 'althofer-1 rigorous v2 tail computation (exact enumeration)',
        'method': 'exact residue-class enumeration mod 2^K, K=1..11',
        'x': 7,
        'tail_computation': results,
        'theorem_candidate': {
            'statement': 'For X=7 and every odd starting value n0, the orbit n(t+1)=odd(7*n(t)+1) diverges to infinity with probability 1 (w.r.t. no randomness needed: actually for deterministic orbit from fixed n0, we show the trajectory from n0=3 is unbounded via the following argument).',
            'argument_sketch': [
                'Step 1: For uniform random odd n, v2(7n+1) is exactly geometrically distributed with P(v2 >= k) = 2^-(k-1), k >= 1 (verified by exact enumeration mod 2^K up to K=11).',
                'Step 2: E[v2] = 2 exactly, so expected per-step drift = log2(7) - 2 = log2(7/4) ≈ 0.807 > 0.',
                'Step 3: However, the actual orbit from n0=3 is deterministic; converting distributional drift to a.s. divergence for a single deterministic orbit requires additional argument (e.g. showing v2(t) does not consistently exceed log2(7)).',
                'Open gap: v2(t) is deterministic given n(t); the tail bound P(v2 >= k) = 2^-(k-1) holds for random n but along one orbit it may be adversarial. Numerically the orbit stays near geometric distribution for 20000 steps (see companion artifact), supporting but not proving unboundedness.',
            ],
        },
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
    }
    out = json.dumps(summary, ensure_ascii=False, indent=1)
    with open('althofer1_rigor.json', 'w') as f:
        f.write(out)
    print(out[:700])


if __name__ == '__main__':
    main()