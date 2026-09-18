# RugBuster vs GoPlus — Solana pump.fun benchmark

Date: 2026-08-24  
Chain: Solana  
Scope: pump.fun-style token launches  
Status: public benchmark artifact package

## Update 2026-09-18 — how big were these creators' positions?

A larger follow-up study labelled 9,170 launches by on-chain outcome
([rugbuster-solana-outcomes](https://github.com/rugbusteraipatrol/rugbuster-solana-outcomes)).
It counts a creator exit as a rug only when there were buyers and the creator
held at least 1% of supply. Applying that bar to this benchmark's 17 confirmed
dumps, read again from chain on 2026-09-18 (the API's `qa/2026-09-18-creator-position.txt`):

| creator's peak share of supply | confirmed dumps |
|---|---|
| under 1% | 13 |
| 1% – 5% | 2 |
| 5% or more | 2 |

This benchmark's ground truth was "the creator sold 95% or more of whatever they
held", with no minimum size. So "17 confirmed rugs" should be read as "17 tokens
whose creator sold out", and for 13 of them the creator's own wallet held under
1% of supply. The stake may have been held elsewhere (side wallets are not
traced), but we cannot show that here. The GoPlus comparison is unaffected:
GoPlus returned SAFE for all 17 on static checks either way.

Since scoring 2026.09.18 the public API reads the creator's position on every
live scan. Of these 17 it now returns DANGER for 2 (15.3% sold, and 13.0% still
held) and WARN for the other 15, still 17/17 not cleared as GOOD.

## Update 2026-09-17 — what the public API returns today

The `DANGER` labels in the tables below are what RugBuster's Solana collector
recorded on 2026-08-24. The public API's live path was rewritten between
2026-09-07 and 2026-09-10 (scoring version 2026.09.7 → 2026.09.9) so that it
never clears a token it has no basis to clear, and so that it says which kind of
answer it is giving (`verdict_basis`: FINDING, REFUSAL or GAP).

All 60 benchmark mints were re-run against the public API on 2026-09-17
(`data/rerun_2026-09-17.json`):

| Group | 2026-08-24 collector label | 2026-09-17 public API label |
|---|---|---|
| A — 30 suspected rugs (17 confirmed) | 30 × DANGER | 28 × WARN, 1 × DANGER, 1 × GOOD |
| B — 30 control tokens | 30 × GOOD | 30 × WARN |

- Of the 17 on-chain-confirmed dumps, **17 of 17 are still not cleared as GOOD**.
  16 return `WARN` with basis `REFUSAL` (`live_scan_cannot_clear_token`,
  `too_few_holders_to_clear`): the mint has almost no holders or liquidity left,
  so a low upstream score means only that there is nothing left to measure.
- The one Group A token now `GOOD` (`2SVgSUgfAd1P…`) is not one of the 17: its
  creator dump was **not** confirmed by the on-chain trace.
- The control group moving from GOOD to WARN is the same refusal applied evenly:
  these are dead July mints too, and the live path no longer calls a dead mint
  safe on upstream's word.

The defensible claim is therefore narrower than the August wording:

> RugBuster does not clear any of the 17 confirmed creator-dump tokens as safe
> (17/17 not cleared as GOOD); GoPlus's static token-security path returned
> SAFE for 17/17. Declining to clear a mint is not the same as identifying a rug.

Why the live path said WARN rather than DANGER: the deployer-history signal
(serial rugger / creator rug rate) that produced the August `DANGER` labels
lives in the collector's stored rows and, until the change below, was not
consulted when a stale row was refreshed. The API reported that gap explicitly
in `not_established` ("what this deployer's previous tokens did").

### Same day, after the fix (API commit `bae168a`, scoring 2026.09.10)

The API now carries the collector's deployer history across a refresh
(`deployer_history` in the response; `evidence.creator_history` reported as
collected). Re-run of the same 60 mints (`data/rerun_2026-09-17-after.json`):

| Set | Result after the fix |
|---|---|
| 17 on-chain-confirmed dumps | **10 × DANGER (basis FINDING: creator has earlier rugs on record), 7 × WARN (REFUSAL), 17/17 not cleared as GOOD** |
| Group A, all 30 | 14 × DANGER, 15 × WARN, 1 × GOOD (the unconfirmed one, as before) |
| Group B, 30 control tokens | 29 × WARN, **1 × DANGER** |

Two things to read honestly:

- The 7 confirmed dumps that stay at WARN have **zero earlier rugs on record**
  for their creator. The collector's August `DANGER` on them came from its
  funding-chain signal, whose threshold the API does not adopt. The collector
  also counted the scanned token itself in the creator's rug count when that
  token was DANGER; the API subtracts it, so a verdict cannot cite itself as
  its own history. That correction is why the number is 10, not 17.
- One control token (`9Dm4sMhcJBqP…`) is now `DANGER` because its creator has
  earlier rugs on record (`creator_history_of_rugged_tokens`,
  `creator_rug_rate_elevated`). The on-chain trace found **no** creator dump on
  this token. Under the token-dump metric that is a false positive; under the
  deployer-history claim it is exactly what the signal says — the creator, not
  this token, has the record. It is left in the table rather than explained away.

The supportable claim after the fix:

> Of 17 on-chain-confirmed creator-dump tokens, RugBuster's public API returns
> DANGER for 10 on the strength of the creator's recorded history and declines
> to clear the other 7 (17/17 not cleared as GOOD). GoPlus's static path
> returned SAFE for 17/17.

## Summary (as written 2026-08-24)

I benchmarked RugBuster against the public GoPlus Solana `token_security` response path on a small evidentiary set of Solana pump.fun tokens.

Headline result:

- 17 tokens were independently confirmed as rug/dump cases by tracing creator balances on-chain.
- RugBuster's collector labeled those 17 as `DANGER` on 2026-08-24 (the public API today returns `WARN`/REFUSAL for 16 of them — see the update above).
- GoPlus labeled 17/17 as `SAFE` with no flags in the tested response path.

This is not framed as "GoPlus is bad." The observed gap appears structural:

- GoPlus Solana token security primarily exposes static token-account properties such as mint/freeze/close authority.
- pump.fun tokens generally have those authorities revoked by the platform template whether they rug or not.
- A creator buy-then-dump pattern is behavioral, not a static mint-authority property.
- RugBuster's useful signal here is deployer-history / funding-hop clustering ("RugDNA"), not a better version of the same static check.

## Important negative finding about RugBuster

The same benchmark also found a problem in RugBuster's own Solana scoring path.

In a control sample of GOOD-labeled older Solana tokens, many resolved cases showed creator holdings going to near-zero at some point. A later review found that fresh pump.fun tokens could inherit a weak/early third-party RugCheck signal too strongly, allowing risky tokens to remain GOOD.

That issue was fixed and deployed before this benchmark is used publicly.

This benchmark should therefore be cited as:

> "A small benchmark found that deployer-history signals catch pump.fun-style rugs that static authority checks can miss. It also exposed and led to a RugBuster scoring correction."

It should **not** be cited as:

> "RugBuster is generally more accurate than GoPlus."

That broader claim is not established by this sample.

## Methodology

### Group A — suspected RugBuster DANGER tokens

- 30 Solana pump.fun tokens sampled from RugBuster DANGER rows.
- Chosen because RugBuster flagged serial-rugger or funding-hop/deployer-history signals.
- Ground truth was not taken from RugBuster's label.
- Creator holdings were independently traced on-chain.
- A token counted as confirmed rug/dump only if the creator's balance collapsed by at least 95% from the observed peak.

Resolved:

- 25/30 ground truth resolved.
- 17/25 confirmed creator dump.
- 8/25 not supported as dump by this metric.
- 5 unresolved.

### GoPlus comparison

For the 17 confirmed creator-dump cases:

- GoPlus caught: 0
- GoPlus missed / returned SAFE: 17
- GoPlus no-data: 0

### Timing verification

A creator balance going to zero is not always malicious; it can be ordinary profit-taking over time.

To address this, a timing pass checked 11 confirmed-dump cases:

- 3 strongest examples from the TOP3 set.
- 8 additional confirmed-dump tokens from Group A.

Result:

- 10/11 collapsed within seconds of token creation.
- 1/11 exited over 7.6 days and is not treated as a clear rug in the headline examples.

The public claim should therefore emphasize the timing-verified instant-exit subset when possible.

## Strongest examples

### 1. CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump

- Explorer: https://solscan.io/token/CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump
- Creator: `23tA8zYuz8Mx5mcAZkb7S3gCF1GpNaGToGo7rn5gpbTR`
- RugBuster: `DANGER`
- RugBuster module: funding-hop/deployer-history signal
- GoPlus: `SAFE`, no flags
- Observed behavior: creator balance peaked at roughly 385M tokens at creation and collapsed to near-zero about 4 seconds later.

### 2. BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump

- Explorer: https://solscan.io/token/BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump
- Creator: `25jZ7EwnKfZo2DZgHM27pbU5Tf54PYG8jc7qNL3gtkxG`
- RugBuster: `DANGER`
- RugBuster module: funding-hop/deployer-history signal
- GoPlus: `SAFE`, no flags
- Observed behavior: creator's roughly 153M-token peak holding collapsed to near-zero about 7 seconds after creation.

### 3. 3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump

- Explorer: https://solscan.io/token/3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump
- Creator: `22GHyTuKjTVwRDJYxbQiCyGJDFfveP78ye1i2HtKQHtG`
- RugBuster: `DANGER`
- RugBuster module: serial-rugger/deployer-history signal
- GoPlus: `SAFE`, no flags
- Observed behavior: creator's roughly 1.73B-token peak holding collapsed to near-zero about 18 seconds later.

## Full 17-token comparison table

| Mint | Ground truth | RugBuster | RugBuster signal | GoPlus |
|---|---|---|---|---|
| `23dxgqAtivdW9cZz7UDFAGXUtByz5sXhKRDENdbXpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `3FpBvhnAJAxjH25WqpYfoUuuB7Dy1UT72Aax4Na5pump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `3TByinjHpnNVZsH2miX9DwgTFB7JPm65yzDN2gSqpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `3n1Zy2pjN1WmKirKP31xvdZNC5QGEtisZpCP8taDpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `6ML7tXmHEyESa2Rtj9FzqvQVA5DhsjPh4wpAvGgLpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `6vpuYc1JzwsHvdf7gHQDby6o45mqsLe9QsJ5uDzgpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `74nxamVTxGkqH2P4UCK6qmfBRcTGyKRAUnsDtBKEpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `7p7ZMhihbDEoRmjTrriUMpM6jHE1jBhjXFG6iztPpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `AShmQtSBCXX7ygHs9kv1Gkrfw5dqkfAidc9hZpowpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `AyerU4udx5PF6ueZne2GuhgLDkqqQLuxzVPbS5sppump` | confirmed dump | DANGER | funding_hops | SAFE |
| `BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `CXRhJrBcCk1m83soxiGjY1AwiY6awAxhua6zPZMqpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `ETWVkgQHsqnDWTmYg3hkhEPSfN49K7S42BhGPVZXpump` | confirmed dump | DANGER | serial_rugger | SAFE |
| `HEoAb66vM87StCj3xyzDSCwVfPgx9ffp2yz1zqkgpump` | confirmed dump | DANGER | funding_hops | SAFE |
| `HoBvJJQxb9Dq2P2sePRkLEzAeZxvmG5QqKumy1PHpump` | confirmed dump | DANGER | serial_rugger | SAFE |

## Reproducibility files in this repository

The repository includes:

```text
SUMMARY.md
METHODOLOGY.md
TOP3.md
scripts/reproduce.py
scripts/check_dump_timing.py
data/benchmark.csv
data/benchmark_rows.json
data/confirmed_17.csv
data/confirmed_17.json
data/mints_17.json
```

Publishing checklist completed before public push:

- no API keys;
- no private RPC URLs;
- no local filesystem paths that should not be public;
- no private notes;
- no claim that RugBuster has general accuracy superiority.
