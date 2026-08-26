"""Reproduce the RugBuster-vs-GoPlus comparison for a fixed list of Solana
mints — no proprietary keys required. Uses the public Solana RPC (slower,
rate-limited — this is deliberately patient about it) and the free GoPlus API.

Input: mints.json (list of {"mint": ..., "creator": ..., "rb_verdict": ...})
Output: prints ground truth (creator dump status) + GoPlus verdict per token.

Usage:
    python reproduce.py mints.json
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

PUBLIC_SOLANA_RPC = "https://api.mainnet-beta.solana.com"
GOPLUS_SOL = "https://api.gopluslabs.io/api/v1/solana/token_security"


def _http(url, payload=None, tries=8):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3.0 * (i + 1))  # public RPC is stricter than Helius
                continue
            raise
        except Exception:
            time.sleep(1.5)
    raise RuntimeError(f"failed after {tries} tries: {url}")


def rpc(method, params):
    out = _http(PUBLIC_SOLANA_RPC, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    return out.get("result")


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
        time.sleep(0.5)
    return out


def creator_dump_status(creator: str, mint: str) -> dict:
    sigs = all_sigs(mint)
    if not sigs:
        return {"status": "no signatures found"}
    sigs = sorted(sigs, key=lambda s: s.get("slot", 0))
    step = max(1, len(sigs) // 40)  # lighter than the 60-sample internal version, public RPC is slower
    max_hold, end_hold = 0.0, None
    for s in sigs[::step]:
        tx = rpc("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}])
        if tx and tx.get("meta"):
            for b in tx["meta"].get("postTokenBalances") or []:
                if b.get("owner") == creator and b.get("mint") == mint:
                    amt = b["uiTokenAmount"].get("uiAmount") or 0
                    max_hold = max(max_hold, amt)
                    end_hold = amt
        time.sleep(0.5)
    if max_hold <= 0:
        return {"status": "creator holding never observed", "n_txs": len(sigs)}
    dumped = end_hold is not None and end_hold < max_hold * 0.05
    return {"status": "dumped" if dumped else "held", "n_txs": len(sigs), "max_hold": max_hold, "end_hold": end_hold}


def goplus_verdict(mint: str) -> tuple[str, list]:
    out = _http(GOPLUS_SOL + "?contract_addresses=" + mint)
    rec = (out.get("result") or {}).get(mint)
    if not rec:
        return "NO_DATA", []
    flags = []
    for field, label in [
        ("mintable", "mintable"), ("freezable", "freezable"), ("closable", "closable"),
        ("balance_mutable_authority", "balance_mutable_authority"),
        ("non_transferable", "non_transferable"),
    ]:
        v = rec.get(field)
        if isinstance(v, dict):
            v = v.get("status")
        if str(v) == "1":
            flags.append(label)
    return ("DANGER" if flags else "SAFE"), flags


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    tokens = json.load(open(sys.argv[1]))
    for t in tokens:
        print(f"\n=== {t['mint']} (RugBuster said: {t.get('rb_verdict','?')}) ===")
        gt = creator_dump_status(t["creator"], t["mint"])
        print("  on-chain (this run):", gt)
        verdict, flags = goplus_verdict(t["mint"])
        print(f"  GoPlus: {verdict} {flags}")
        time.sleep(1.0)


if __name__ == "__main__":
    main()
