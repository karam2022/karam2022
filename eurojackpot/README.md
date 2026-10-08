# Eurojackpot tracker (just for fun)

`draws.csv` holds every Eurojackpot draw from 23 March 2012 to 6 October 2026
(996 draws). Columns: `date, n1..n5` (5 of 50, sorted), `e1, e2` (2 of 12, sorted).

Sources: draws through 8 Aug 2025 come from the `tsch-ej-numbers` npm package;
later draws were collected from euro-jackpot.net / lotterien1x1.de / lotto.net
archive listings and cross-checked (three overlapping draws matched exactly).

## Use

```bash
python3 analyze.py                      # stats for the last 2 years + 6 suggested tickets
python3 analyze.py --seed 7             # a different set of tickets
python3 analyze.py --all                # whole history
python3 analyze.py --check 4 6 7 17 45 7 12          # how a ticket would have scored
python3 analyze.py --add 2026-10-09 3 14 27 38 45 2 9 # log a new draw after each Tue/Fri
```

## The honest part

Each draw is independent and uniformly random, and the chi-square test in the
report confirms the last two years look exactly like noise. No ticket has better
odds than another (1 in 139,838,160 for the jackpot). The one choice that does
matter: unpopular combinations (numbers above 31, no obvious patterns) share a
jackpot with fewer people if they ever hit. That is what the "Anti-popular"
ticket is for.

Paper-trade: write down the six tickets after each run, log the real draw with
`--add`, and use `--check` to see how they would have done.
