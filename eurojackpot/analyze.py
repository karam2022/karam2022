#!/usr/bin/env python3
"""Eurojackpot draw analysis and ticket generator (for fun).

Usage:
  python3 analyze.py                 # stats over the last 2 years + suggested tickets
  python3 analyze.py --years 1       # different window
  python3 analyze.py --all           # whole history since 2012
  python3 analyze.py --check 4 6 7 17 45 7 12   # score a ticket against every draw in the window
  python3 analyze.py --add 2026-10-09 1 2 3 4 5 6 7   # append a new draw to draws.csv

Honest note: every draw is independent and uniform. Nothing here changes
your odds (1 in 139,838,160 for the jackpot). The chi-square test at the
bottom of the report shows how close to "pure noise" the data really is.
"""
import argparse, csv, datetime as dt, itertools, math, random, sys, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "draws.csv")

def load():
    rows = []
    with open(CSV) as f:
        for r in csv.DictReader(f):
            rows.append((dt.date.fromisoformat(r["date"]),
                         tuple(int(r[f"n{i}"]) for i in range(1, 6)),
                         (int(r["e1"]), int(r["e2"]))))
    rows.sort()
    return rows

def chi_square_uniform(counts, n_draws, picks, pool):
    exp = n_draws * picks / pool
    stat = sum((counts.get(k, 0) - exp) ** 2 / exp for k in range(1, pool + 1))
    df = pool - 1
    return stat, df, exp

def chi_p_value(stat, df):
    # survival function of chi-square via regularized upper incomplete gamma (series/continued fraction)
    a, x = df / 2.0, stat / 2.0
    if x <= 0: return 1.0
    def gammainc_lower_series(a, x):
        s = term = 1.0 / a; n = 1
        while abs(term) > 1e-15 * abs(s) and n < 10000:
            term *= x / (a + n); s += term; n += 1
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    def gammainc_upper_cf(a, x):
        b = x + 1 - a; c = 1e300; d = 1 / b; h = d
        for i in range(1, 10000):
            an = -i * (i - a); b += 2
            d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
            c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
            d = 1 / d; delta = d * c; h *= delta
            if abs(delta - 1) < 1e-15: break
        return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return gammainc_upper_cf(a, x) if x > a + 1 else 1 - gammainc_lower_series(a, x)

def report(draws, label):
    n = len(draws)
    main = Counter(x for _, m, _ in draws for x in m)
    euro = Counter(x for _, _, e in draws for x in e)
    last_seen_main = {k: next(i for i, (_, m, _) in enumerate(reversed(draws)) if k in m) if main[k] else n for k in range(1, 51)}
    last_seen_euro = {k: next(i for i, (_, _, e) in enumerate(reversed(draws)) if k in e) if euro[k] else n for k in range(1, 13)}

    print(f"=== {label}: {n} draws, {draws[0][0]} to {draws[-1][0]} ===\n")
    exp_m = n * 5 / 50; exp_e = n * 2 / 12
    print(f"Expected hits per main number: {exp_m:.1f}   per euro number: {exp_e:.1f}\n")

    hot = main.most_common()
    print("Main numbers, hottest 12:   " + ", ".join(f"{k}({v})" for k, v in hot[:12]))
    print("Main numbers, coldest 12:   " + ", ".join(f"{k}({v})" for k, v in sorted(hot, key=lambda kv: (kv[1], kv[0]))[:12]))
    od = sorted(last_seen_main.items(), key=lambda kv: -kv[1])
    print("Most overdue main (draws since last hit): " + ", ".join(f"{k}({v})" for k, v in od[:10]))
    eh = euro.most_common()
    print("\nEuro numbers hot -> cold:   " + ", ".join(f"{k}({v})" for k, v in eh))
    oe = sorted(last_seen_euro.items(), key=lambda kv: -kv[1])
    print("Most overdue euro:          " + ", ".join(f"{k}({v})" for k, v in oe[:5]))

    pairs = Counter(p for _, m, _ in draws for p in itertools.combinations(m, 2))
    print("\nMost frequent main-number pairs: " + ", ".join(f"{a}-{b}({c})" for (a, b), c in pairs.most_common(10)))
    epairs = Counter(e for _, _, e in draws)
    print("Most frequent euro pairs:        " + ", ".join(f"{a}-{b}({c})" for (a, b), c in epairs.most_common(6)))

    sums = [sum(m) for _, m, _ in draws]
    print(f"\nSum of 5 main numbers: mean {sum(sums)/n:.1f}, median {sorted(sums)[n//2]}, "
          f"middle 50% between {sorted(sums)[n//4]} and {sorted(sums)[3*n//4]} (theoretical mean 127.5)")
    odd = Counter(sum(1 for x in m if x % 2) for _, m, _ in draws)
    print("Odd count distribution (odd:draws): " + ", ".join(f"{k}:{odd[k]}" for k in range(6)))
    low = Counter(sum(1 for x in m if x <= 25) for _, m, _ in draws)
    print("Low(1-25) count distribution:       " + ", ".join(f"{k}:{low[k]}" for k in range(6)))
    consec = sum(1 for _, m, _ in draws if any(b - a == 1 for a, b in zip(m, m[1:])))
    print(f"Draws containing at least one consecutive pair: {consec} of {n} ({100*consec/n:.0f}%, theory ~{100*(1-math.comb(46,5)/math.comb(50,5)):.0f}%)")
    dec = Counter((x - 1) // 10 for _, m, _ in draws for x in m)
    print("Hits per decade 1-10/11-20/21-30/31-40/41-50: " + "/".join(str(dec[i]) for i in range(5)))

    stat, df, _ = chi_square_uniform(main, n, 5, 50)
    p = chi_p_value(stat, df)
    stat2, df2, _ = chi_square_uniform(euro, n, 2, 12)
    p2 = chi_p_value(stat2, df2)
    print(f"\nChi-square vs. uniform: main numbers stat={stat:.1f} (df={df}) p={p:.2f}; euro numbers stat={stat2:.1f} (df={df2}) p={p2:.2f}")
    print("  (p well above 0.05 = the hot/cold differences look exactly like random noise)")
    return main, euro, last_seen_main, last_seen_euro, pairs

def tickets(main, euro, lsm, lse, pairs, seed):
    rnd = random.Random(seed)
    def pick_weighted(weights, k, pool):
        items = list(range(1, pool + 1)); chosen = []
        w = [max(weights.get(i, 0), 1e-9) for i in items]
        while len(chosen) < k:
            c = rnd.choices(items, w)[0]
            if c not in chosen: chosen.append(c)
        return tuple(sorted(chosen))
    out = []
    hot_m = [k for k, _ in main.most_common(12)]; hot_e = [k for k, _ in euro.most_common(4)]
    out.append(("Hot (most frequent)", tuple(sorted(rnd.sample(hot_m, 5))), tuple(sorted(rnd.sample(hot_e, 2)))))
    od_m = [k for k, _ in sorted(lsm.items(), key=lambda kv: -kv[1])[:12]]; od_e = [k for k, _ in sorted(lse.items(), key=lambda kv: -kv[1])[:4]]
    out.append(("Overdue (longest absent)", tuple(sorted(rnd.sample(od_m, 5))), tuple(sorted(rnd.sample(od_e, 2)))))
    out.append(("Frequency-weighted", pick_weighted(main, 5, 50), pick_weighted(euro, 2, 12)))
    # Balanced: 2-3 odd, 2-3 low, sum in 100-155, one number per decade-ish, no consecutive
    while True:
        m = tuple(sorted(rnd.sample(range(1, 51), 5)))
        if 2 <= sum(x % 2 for x in m) <= 3 and 2 <= sum(x <= 25 for x in m) <= 3 and 100 <= sum(m) <= 155 \
           and not any(b - a == 1 for a, b in zip(m, m[1:])) and len({(x - 1) // 10 for x in m}) >= 4:
            break
    out.append(("Balanced shape", m, tuple(sorted(rnd.sample(range(1, 13), 2)))))
    # Anti-popular: the only strategy with a real effect. Birthdays (1-31) and patterns are over-played,
    # so a ticket heavy on 32-50 shares the jackpot with fewer people if it ever hits.
    while True:
        m = tuple(sorted(rnd.sample(range(1, 51), 5)))
        if sum(x > 31 for x in m) >= 3 and not any(b - a == 1 for a, b in zip(m, m[1:])):
            break
    out.append(("Anti-popular (fewer co-winners)", m, tuple(sorted(rnd.sample(range(1, 13), 2)))))
    # Top pair + fill
    (a, b), _ = pairs.most_common(1)[0]
    fill = tuple(sorted({a, b} | set(rnd.sample([x for x in range(1, 51) if x not in (a, b)], 3))))
    out.append(("Top pair + random fill", fill, tuple(sorted(rnd.sample(range(1, 13), 2)))))
    return out

def personal(phrase, n):
    """Lines seeded by a phrase only you know. Nobody else asking an AI gets these.
    Filters: at least 3 numbers above 31, no consecutive pair, not all same parity,
    sum between 100 and 175, no two numbers sharing the same last digit pattern (e.g. 7,17,27)."""
    import hashlib
    rnd = random.Random(int(hashlib.sha256(phrase.encode()).hexdigest(), 16))
    print(f"Personal lines for phrase of length {len(phrase)} (keep the phrase secret; same phrase = same lines):")
    made = 0
    while made < n:
        m = tuple(sorted(rnd.sample(range(1, 51), 5)))
        e = tuple(sorted(rnd.sample(range(1, 13), 2)))
        if sum(x > 31 for x in m) < 3: continue
        if any(b - a == 1 for a, b in zip(m, m[1:])): continue
        if sum(x % 2 for x in m) in (0, 5): continue
        if not 100 <= sum(m) <= 175: continue
        if len({x % 10 for x in m}) < 4: continue
        made += 1
        print(f"  line {made}: {' '.join(f'{x:2d}' for x in m)}  |  {e[0]:2d} {e[1]:2d}")

def check(draws, nums):
    m = set(nums[:5]); e = set(nums[5:7])
    score = Counter()
    for d, dm, de in draws:
        score[(len(m & set(dm)), len(e & set(de)))] += 1
    print(f"Ticket {sorted(m)} + {sorted(e)} against {len(draws)} draws:")
    for k in sorted(score, reverse=True):
        print(f"  {k[0]} main + {k[1]} euro: {score[k]} draws")
    best = max(score, key=lambda k: (k[0], k[1]))
    print(f"Best match: {best[0]} main + {best[1]} euro")

def main_cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=float, default=2.0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--check", nargs=7, type=int, metavar="N")
    ap.add_argument("--add", nargs=8, metavar="X", help="date n1 n2 n3 n4 n5 e1 e2")
    ap.add_argument("--personal", metavar="PHRASE", help="generate N unique anti-popular lines from a secret phrase")
    ap.add_argument("--lines", type=int, default=4)
    a = ap.parse_args()
    if a.personal:
        personal(a.personal, a.lines); return
    if a.add:
        d = dt.date.fromisoformat(a.add[0]); m = sorted(int(x) for x in a.add[1:6]); e = sorted(int(x) for x in a.add[6:8])
        assert len(set(m)) == 5 and all(1 <= x <= 50 for x in m) and len(set(e)) == 2 and all(1 <= x <= 12 for x in e)
        if any(r[0] == d for r in load()): sys.exit(f"{d} already in draws.csv")
        with open(CSV, "a", newline="") as f: csv.writer(f).writerow([d.isoformat(), *m, *e])
        print(f"added {d}: {m} | {e}"); return
    draws = load()
    if not a.all:
        cutoff = draws[-1][0] - dt.timedelta(days=int(365.25 * a.years))
        draws = [r for r in draws if r[0] > cutoff]
        label = f"Last {a.years:g} year(s)"
    else:
        label = "All draws since 2012"
    if a.check:
        check(draws, a.check); return
    main, euro, lsm, lse, pairs = report(draws, label)
    seed = a.seed if a.seed is not None else int(draws[-1][0].strftime("%Y%m%d"))
    print(f"\n=== Suggested tickets (seed {seed}; pass --seed N for a different set) ===")
    for name, m, e in tickets(main, euro, lsm, lse, pairs, seed):
        print(f"  {name:34s} {' '.join(f'{x:2d}' for x in m)}  |  {e[0]:2d} {e[1]:2d}")
    print("\nRemember: odds are identical for every ticket. Have fun, keep it on paper.")

if __name__ == "__main__":
    main_cli()
