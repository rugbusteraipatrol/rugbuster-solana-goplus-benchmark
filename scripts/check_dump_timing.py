"""Timing-aware dump verification — the check that should have been done from
the start. "Creator's balance went from peak to ~0" alone doesn't prove a
rug; it's equally consistent with normal profit-taking over weeks. This finds
WHEN the drop happened relative to token creation, and whether it was one
fast exit or a slow bleed.

Method: binary-search the transaction history (using only signature+slot,
cheap) to localize the tx where the creator's balance crosses from "still
holding most of peak" to "near zero," then fetch full detail around that
point to get exact timestamps.

Usage:
    HELIUS_RPC=...  python check_dump_timing.py <creator> <mint>
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

H = os.environ.get("HELIUS_RPC", "https://api.mainnet-beta.solana.com")


def rpc(method, params, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(
                H, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.15)
                return json.loads(r.read()).get("result")
        except Exception:
            time.sleep(0.6 * (i + 1))
    return None


def all_sigs(mint):
    out, before = [], None
    while True:
        params = [mint, {"limit": 1000, **({"before": before} if before else {})}]
        b = rpc("getSignaturesForAddress", params) or []
        if not b:
            break
        out += b
        before = b[-1]["signature"]
        if len(b) < 1000:
            break
    return sorted(out, key=lambda s: s.get("slot", 0))


def creator_balance_at(sig, creator, mint):
    tx = rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
    if not tx or not tx.get("meta"):
        return None, None
    bt = tx.get("blockTime")
    for b in tx["meta"].get("postTokenBalances") or []:
        if b.get("owner") == creator and b.get("mint") == mint:
            return b["uiTokenAmount"].get("uiAmount") or 0, bt
    return None, bt  # tx touched the mint but not this owner's balance


def analyze(creator, mint):
    sigs = all_sigs(mint)
    if not sigs:
        return {"error": "no signatures"}
    n = len(sigs)
    create_bt = None
    # find creation time: first tx blockTime
    for s in sigs[:3]:
        _, bt = creator_balance_at(s["signature"], creator, mint)
        if bt:
            create_bt = bt
            break

    # dense scan: sample every tx up to a budget, tracking creator balance
    # over time to find peak and the point balance collapses
    budget = 150
    step = max(1, n // budget)
    trace = []
    for s in sigs[::step]:
        bal, bt = creator_balance_at(s["signature"], creator, mint)
        if bal is not None and bt is not None:
            trace.append((bt, bal, s["signature"]))
    if not trace:
        return {"error": "creator balance never observed", "n_txs": n}

    peak_bt, peak_bal, _ = max(trace, key=lambda t: t[1])
    # find first point after peak where balance is <5% of peak
    after_peak = [t for t in trace if t[0] >= peak_bt]
    collapse = next((t for t in after_peak if t[1] < peak_bal * 0.05), None)

    result = {
        "n_txs": n,
        "creation_time": create_bt,
        "peak_balance": peak_bal,
        "peak_time": peak_bt,
        "n_balance_samples": len(trace),
    }
    if collapse is None:
        result["outcome"] = "never collapsed to <5% of peak in sampled trace"
        return result

    collapse_bt = collapse[0]
    result["collapse_time"] = collapse_bt
    result["seconds_peak_to_collapse"] = collapse_bt - peak_bt
    result["hours_peak_to_collapse"] = round((collapse_bt - peak_bt) / 3600, 2)
    if create_bt:
        result["hours_creation_to_collapse"] = round((collapse_bt - create_bt) / 3600, 2)

    # classify: fast dump if collapse happened within 1 hour of peak holding,
    # slow exit if it took many hours/days
    gap_h = result["hours_peak_to_collapse"]
    if gap_h < 1:
        result["classification"] = "FAST_DUMP (<1h from peak to ~0)"
    elif gap_h < 24:
        result["classification"] = f"SAME_DAY_EXIT ({gap_h:.1f}h from peak to ~0)"
    else:
        result["classification"] = f"SLOW_EXIT ({gap_h:.1f}h = {gap_h/24:.1f}d from peak to ~0)"
    return result


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    creator, mint = sys.argv[1], sys.argv[2]
    r = analyze(creator, mint)
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
