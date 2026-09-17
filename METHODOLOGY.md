# RugBuster vs GoPlus — Solana evidentiary benchmark
Run date: 2026-08-24. Chain: Solana only (see methodology note on why AVAX was dropped).
## Headline result
> Note (2026-09-17): RugBuster labels in this document are the collector's labels
> from 2026-08-24. The public API's live path now returns `WARN` (basis REFUSAL)
> for 16 of the 17 confirmed rugs; 17/17 remain not cleared as GOOD. See the
> update at the top of SUMMARY.md and `data/rerun_2026-09-17.json`.

On **17 independently-confirmed real rug tokens** (creator bought then dumped ≥95% of peak holding, traced on-chain via Helius — not our own DB label), **GoPlus flagged 0/17 as DANGER and marked 17/17 SAFE**.
This is not a close result, and it is not really about GoPlus being worse at catching rugs — it's structural. GoPlus's Solana `token_security` endpoint only reports **static mint-account properties** (mintable, freezable, closable, transfer-authority flags). Every pump.fun token has these revoked by the platform's own token-creation template, rug or not — so GoPlus's Solana check cannot fire DANGER on a bonding-curve dump-style rug **on any pump.fun token, period**, independent of whether it actually rugged. RugBuster's edge here is a different kind of signal entirely (deployer history / funding-hop clustering), not a better version of the same check.
## Methodology notes (read before citing this)

- **AVAX was excluded.** `avax_scans` turned out to be a mint-time training
  dataset — 100% of 11,291 records (GOOD/WARN/DANGER alike) show `Holders: 0`,
  and the sampled tokens have no DEX pair at all. No real investor could ever
  have bought them, so a GoPlus comparison there would prove nothing. Only
  Solana data reflects real post-launch trading.
- **GoPlus's Solana endpoint does not batch.** Passing multiple comma-separated
  addresses (even just 2) silently returns data for only the first one — no
  error. This was caught mid-run (first pass showed near-total `NO_DATA`) and
  fixed to one call per address. Flagging this because it's an easy trap for
  anyone else scripting against this API.
- **DexScreener has poor coverage of pump.fun-only tokens.** An early version
  used DexScreener to confirm "still alive" for the control group; a spot
  check found 0/8 had any indexed pair. Switched Group B to the same Helius
  on-chain method as Group A (real tx activity + creator did not dump) for a
  fair, symmetric ground truth instead.
- **Ground truth was initially binary "dumped y/n," which is not enough —
  fixed after a direct challenge on this.** "Balance went to ~0" alone doesn't
  prove a rug; it's equally consistent with normal profit-taking over weeks.
  A follow-up pass (`check_dump_timing.py`) binary-searches each token's tx
  history to find exactly *when* the creator's balance collapsed relative to
  receiving it. On an 11-token sample from Group A's confirmed-dump set
  (the 3 TOP3 cases + 8 more), **10/11 (91%) collapsed within seconds of
  token creation** — genuine instant exits, the same signature already proven
  on AVAX. The 1 exception took 7.6 days and is not counted as a rug. This
  timing check was **not** run against Group B's "creator dumped" rows (9
  tokens, see below) — those numbers remain an unresolved lower bound, not a
  confirmed finding, and should not be cited as proof of a RugBuster
  false-negative rate until timed the same way.
- Sample: 30 Group A (distinct creators, DANGER + serial-rugger/funding-hop
  signal), 30 Group B (random 30 of a >20-day-old GOOD pool of 400), seed=2026.
## Group A — claimed rugs, GoPlus comparison
- Sample: 30. Ground truth resolved: 25.
- **Confirmed real rug (creator dumped ≥95%): 17/25**
- Confirmed NOT a dump by this metric (RugBuster DANGER label not supported here): 8/25
- Unresolved (creator holding never observed in sampled txs): 5
- **Of the confirmed rugs: GoPlus caught 0, missed 17, no data 0.**
## Group B — claimed legit (GOOD, >20 days old)
- Sample: 30. Ground truth resolved: 17.
- **Confirmed legit (real trading + creator did not exit): 4/17**
- Confirmed NOT legit by this metric: 13/17
  - of which: creator fully exited (see timing caveat above) = 8, essentially untraded = 5
- Unresolved: 13
**Honest flag, not swept under the rug:** among the GOOD-labeled tokens where we could observe creator holding at all, a majority showed the creator's position going to ~0 at some point. Whether that's malicious (undetected rug) or ordinary profit-taking on a token that found real volume needs a timing-aware follow-up before drawing a conclusion about RugBuster's false-negative rate on Solana GOOD labels. Recording this as an open question, not a resolved finding, per instruction not to bury bad news.
## Differences table
| mint | ground truth | RugBuster | RugBuster module | GoPlus | GoPlus flags |
|---|---|---|---|---|---|
| `23dxgqAtivdW9cZz7UDFAGXUtByz5sXhKRDENdbXpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `3FpBvhnAJAxjH25WqpYfoUuuB7Dy1UT72Aax4Na5pump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `3TByinjHpnNVZsH2miX9DwgTFB7JPm65yzDN2gSqpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `3n1Zy2pjN1WmKirKP31xvdZNC5QGEtisZpCP8taDpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `6ML7tXmHEyESa2Rtj9FzqvQVA5DhsjPh4wpAvGgLpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `6vpuYc1JzwsHvdf7gHQDby6o45mqsLe9QsJ5uDzgpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `74nxamVTxGkqH2P4UCK6qmfBRcTGyKRAUnsDtBKEpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `7p7ZMhihbDEoRmjTrriUMpM6jHE1jBhjXFG6iztPpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `AShmQtSBCXX7ygHs9kv1Gkrfw5dqkfAidc9hZpowpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `AyerU4udx5PF6ueZne2GuhgLDkqqQLuxzVPbS5sppump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `CXRhJrBcCk1m83soxiGjY1AwiY6awAxhua6zPZMqpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `ETWVkgQHsqnDWTmYg3hkhEPSfN49K7S42BhGPVZXpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |
| `HEoAb66vM87StCj3xyzDSCwVfPgx9ffp2yz1zqkgpump` | rug (confirmed) | DANGER | funding_hops | SAFE | — |
| `HoBvJJQxb9Dq2P2sePRkLEzAeZxvmG5QqKumy1PHpump` | rug (confirmed) | DANGER | serial_rugger | SAFE | — |

Full row-level data: `results/benchmark.csv`, `results/benchmark_rows.json`.
