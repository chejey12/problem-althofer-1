"""
import sys
sys.set_int_max_str_digits(100000)
althofer-1: 存在奇數 X>=5 與奇起點 n0 使 n(t+1)=odd(X*n(t)+1) 發散?
這是「證明或反證」的存在性題 — 找到一個 (X, n0) 發散 witness 就贏一半 (disproof of non-divergence)。

已知理論: X=3 時是經典 Collatz 猜想 (未解)。X=5,7,9,... 時乘數更大,
直覺上 log X - 2 log 2 = log(X/4) > 0 當 X > 4 → 期望漂移為正 → 應該容易發散!
X=5: log(5/4) > 0 → 大部分軌道應發散。搜尋應該很快找到。

本實驗: 對 X in {5,7,9,...,51}, 測試大量奇起點, 找發散軌道 (bounded steps)。
"""
import json
from datetime import datetime, timezone

MAX_STEPS = 50000
X_LIST = [5, 7, 9, 11, 13, 15]


def odd_part(m: int) -> int:
    return m >> ((m & -m).bit_length() - 1)


def try_diverge(x: int, n0: int, max_steps: int = MAX_STEPS):
    """回傳 (diverged, steps, max_n)"""
    n = n0
    max_n = n
    for s in range(max_steps):
        n = odd_part(x * n + 1)
        max_n = max(max_n, n)
        if n == 1:
            return False, s, max_n
        if n > max_n:
            max_n = n
    return True, max_steps, max_n


def main():
    results = []
    witnesses = []
    for x in X_LIST:
        found = None
        # 從小奇數往上試
        for n0 in range(3, 200000, 2):
            div, steps, max_n = try_diverge(x, n0, max_steps=20000)
            if div:
                found = (n0, steps, max_n)
                witnesses.append({'x': x, 'n0': n0, 'steps_to_exceed': steps, 'max_n_bits': max_n.bit_length()})
                break
        results.append({'x': x, 'found_divergent': found is not None, 'witness': {'n0': found[0], 'steps': found[1], 'max_n_bits': found[2].bit_length()} if found else None})
        print(f"X={x}: {'FOUND' if found else 'none in range'} -> found_divergent={found is not None} n0={found[0] if found else None}")
    summary = {
        'experiment': 'althofer-1 divergence witness search',
        'max_steps_budget': 20000,
        'search_range_n0': '3..199999 odd',
        'x_list': X_LIST,
        'results': results,
        'witnesses': witnesses,
        'note': ('For X>=5, expected log-drift log(X/4)>0, so divergence is expected; '
                 'a verified witness (trajectory certificate) constitutes a disproof witness candidate. '
                 'Divergence within a step budget is bounded evidence, not an infinite-orbit proof; '
                 'a full certificate requires showing the trajectory is unbounded (e.g. escape pattern).'),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'claim_status': 'candidate_numeric_check_only',
    }
    import json as j
    out = j.dumps(summary, ensure_ascii=False, indent=1)
    with open('althofer1_witness.json', 'w') as f:
        f.write(out)
    print()
    print(out[:800])
main()
