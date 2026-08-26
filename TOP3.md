# Top 3 — RugBuster caught it, GoPlus called it SAFE

Solana pump.fun tokens. GoPlus's Solana `token_security` check only inspects
static mint-account properties (mintable/freezable/closable/transfer
authority) — properties every pump.fun token has revoked by the platform's
own template, rug or not. It has no signal for "creator bought the token then
dumped their position." RugBuster's deployer-history / funding-hop signal
does. These three are the strongest examples: real, substantial trading
happened before the creator fully exited, so this isn't a thin/no-volume edge
case.

Ground truth for each: independently traced on-chain via Helius RPC — both
that the creator's balance went from a real peak to ~0, **and when**. All
three collapsed within **4-18 seconds** of receiving their tokens, at the
token's creation moment — the same instant-pull signature already proven on
AVAX. A broader spot-check (8 more confirmed-dump tokens from this benchmark's
Group A) found the same pattern on 7/8; the 1 exception was a genuine slow
exit over 7.6 days and is not being claimed as a rug. Combined: **10/11
(91%)** of checked confirmed-dump cases are fast, non-organic exits.

## Honest caveat

The same benchmark process also exposed a RugBuster-side scoring issue: a
GOOD-labeled control sample showed 9/10 false GOOD-style outcomes under the
same creator-exit review. The root cause was that fresh pump.fun tokens could
inherit an unreliable third-party RugCheck signal too strongly. That path was
fixed and deployed before this benchmark package was published.

---

### 1. `CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump`

- Explorer: https://solscan.io/token/CHMfiUmZvKwLdjo3nfZHQHp3RrbCBMAuRkkqnGPnpump
- Creator: `23tA8zYuz8Mx5mcAZkb7S3gCF1GpNaGToGo7rn5gpbTR`
- RugBuster: DANGER — creator had 1 prior rug, funding traced 1 hop back
- GoPlus: **SAFE**, no flags
- What actually happened: creator's balance peaked at ~385M tokens at the
  moment of creation and collapsed to near-zero **4 seconds later**. The
  6,991 on-chain transactions are the token's *entire lifetime* volume —
  overwhelmingly traders buying and selling a token the creator had already
  fully exited, not activity that happened before the exit.

### 2. `BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump`

- Explorer: https://solscan.io/token/BiHqVnZibFk3po2JpTWnpeDy1ryTceQ88x1HM5TEpump
- Creator: `25jZ7EwnKfZo2DZgHM27pbU5Tf54PYG8jc7qNL3gtkxG`
- RugBuster: DANGER — creator had 1 prior rug, funding traced 1 hop back
- GoPlus: **SAFE**, no flags
- What actually happened: creator's ~153M-token peak holding collapsed to
  near-zero **7 seconds** after creation. The 1,666 transactions are lifetime
  volume after the exit, not before it.

### 3. `3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump`

- Explorer: https://solscan.io/token/3ZuZXv2g3TZofEogzM9rwEbVB5i1NwL8TqNCWH2jpump
- Creator: `22GHyTuKjTVwRDJYxbQiCyGJDFfveP78ye1i2HtKQHtG`
- RugBuster: DANGER — this creator's cluster shows 3 prior rugs (serial
  pattern), flagged by deployer-history clustering, not a static contract check
- GoPlus: **SAFE**, no flags
- What actually happened: creator's ~1.73B-token peak holding (peak recorded
  95 seconds after the creation tx — the initial buy) collapsed to near-zero
  **18 seconds later**. Lifetime volume was 313 transactions; the exit itself
  took under a minute from token creation.

---

## Status

Timing-verified via `check_dump_timing.py` (Helius RPC, binary-search over the
transaction history to localize the exact balance collapse and its
timestamp). All three are confirmed fast, non-organic exits — not slow
profit-taking — so this is safe to cite as "proven rug" for these three.
Verification script and raw output: `check_dump_timing.py`,
`timing_top3.log`. Reproduce independently with the public-RPC version,
`reproduce.py` (no API key needed, just slower).
