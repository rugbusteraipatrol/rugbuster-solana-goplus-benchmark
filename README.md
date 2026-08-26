# RugBuster Solana GoPlus benchmark artifacts

Public benchmark package for the RugBuster vs GoPlus Solana pump.fun comparison.

Start here:

- [SUMMARY.md](SUMMARY.md) — short public write-up and headline result.
- [METHODOLOGY.md](METHODOLOGY.md) — longer methodology notes from the benchmark run.
- [TOP3.md](TOP3.md) — three strongest timing-verified examples.
- [data/confirmed_17.csv](data/confirmed_17.csv) and [data/confirmed_17.json](data/confirmed_17.json) — filtered headline set: Group A rows where creator dump was independently confirmed.
- [data/benchmark.csv](data/benchmark.csv) and [data/benchmark_rows.json](data/benchmark_rows.json) — broader raw benchmark output, including unresolved and control rows.
- [scripts/reproduce.py](scripts/reproduce.py) — public-RPC reproduction script for a fixed mint/creator list.
- [data/mints_17.json](data/mints_17.json) — input list for `scripts/reproduce.py`.

## Reproduce

```bash
python scripts/reproduce.py data/mints_17.json
```

The script uses public Solana RPC and the public GoPlus endpoint. It does not require RugBuster credentials, a private database, Helius, or any API key. Public RPC can be slow/rate-limited; failures should be retried rather than treated as a changed result.

If you want a quick sanity check, start with a smaller input file containing 1-3 rows from `data/mints_17.json`. Running the full 17-token set, and especially extending it to the broader benchmark/control rows, can take a while because every token requires public RPC transaction-history calls plus a GoPlus request.

## Important scope limits

This is a small evidentiary benchmark, not a universal accuracy claim.

The defensible claim is:

> In this sample, deployer-history / funding-hop signals caught pump.fun-style creator dump cases that static Solana token-authority checks returned as SAFE.

Do not cite this as "RugBuster is generally more accurate than GoPlus." That broader claim is not established here.

The same benchmark process also exposed a RugBuster scoring weakness on fresh pump.fun tokens, which was fixed before publication. That negative finding is included in the summary on purpose.
