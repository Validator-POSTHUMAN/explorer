#!/usr/bin/env python3
"""
Merge local chain endpoints with cosmos/chain-registry,
probe liveness, keep only working ones. Operates on a directory of *.json.
"""
import json
import sys
import os
import urllib.request
import urllib.error
import ssl
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

CHAIN_REGISTRY = "https://raw.githubusercontent.com/cosmos/chain-registry/master"
TIMEOUT = 5
PROBE_REST = "/cosmos/staking/v1beta1/pool"
PROBE_RPC = "/status"
UA = "ping-pub-endpoint-refresher/1.0"

# Lax TLS for probing — some LCDs have weird intermediate certs but work
TLS_CTX = ssl.create_default_context()
TLS_CTX.check_hostname = False
TLS_CTX.verify_mode = ssl.CERT_NONE


def fetch_chain_registry(registry_name: str):
    url = f"{CHAIN_REGISTRY}/{registry_name}/chain.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10, context=TLS_CTX) as r:
            return json.loads(r.read())
    except Exception as e:
        return None


def probe(addr: str, path: str) -> bool:
    full = addr.rstrip("/") + path
    try:
        req = urllib.request.Request(full, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=TLS_CTX) as r:
            if r.status != 200:
                return False
            # body should be JSON
            r.read(2048)  # don't pull full body, but verify some bytes come back
            return True
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, ssl.SSLError, OSError):
        return False
    except Exception:
        return False


def normalize(item):
    """Accept either {address, provider} object or plain string."""
    if isinstance(item, str):
        return {"provider": "unknown", "address": item}
    if isinstance(item, dict) and item.get("address"):
        return {"provider": item.get("provider", "unknown"), "address": item["address"]}
    return None


def merge_dedupe(local: list, registry: list) -> list:
    """Merge two endpoint lists. Local wins on duplicate addr."""
    seen = {}
    for raw in (local or []) + (registry or []):
        item = normalize(raw)
        if not item:
            continue
        addr = item["address"].rstrip("/")
        if addr not in seen:
            seen[addr] = {"provider": item["provider"], "address": addr}
    return list(seen.values())


def probe_endpoints(endpoints: list, probe_path: str) -> list:
    """Probe each endpoint in parallel, return only the alive ones in order."""
    alive = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(probe, e["address"], probe_path): e for e in endpoints}
        for fut in as_completed(futures):
            e = futures[fut]
            try:
                if fut.result():
                    alive.append(e)
            except Exception:
                pass
    # preserve original order roughly: sort by index in endpoints
    order = {id(e): i for i, e in enumerate(endpoints)}
    alive.sort(key=lambda x: order.get(id(x), 999))
    return alive


def process_chain(json_path: str, dry_run: bool = False):
    with open(json_path) as f:
        local = json.load(f)

    chain_name = local.get("chain_name", os.path.basename(json_path))
    registry_name = local.get("registry_name") or chain_name

    cr = fetch_chain_registry(registry_name)

    cr_rest = (cr or {}).get("apis", {}).get("rest", []) if cr else []
    cr_rpc = (cr or {}).get("apis", {}).get("rpc", []) if cr else []

    local_api = local.get("api", []) or []
    local_rpc = local.get("rpc", []) or []

    merged_rest = merge_dedupe(local_api, cr_rest)
    merged_rpc = merge_dedupe(local_rpc, cr_rpc)

    alive_rest = probe_endpoints(merged_rest, PROBE_REST)
    alive_rpc = probe_endpoints(merged_rpc, PROBE_RPC)

    line = (
        f"  {chain_name:22s}  "
        f"rest: {len(local_api):2d}+{len(cr_rest):2d}→{len(alive_rest):2d}  "
        f"rpc: {len(local_rpc):2d}+{len(cr_rpc):2d}→{len(alive_rpc):2d}"
        f"  {'(no registry)' if cr is None else ''}"
    )
    print(line)

    if not dry_run and (alive_rest or alive_rpc):
        local["api"] = alive_rest if alive_rest else local_api  # don't wipe if all dead
        local["rpc"] = alive_rpc if alive_rpc else local_rpc
        with open(json_path, "w") as f:
            json.dump(local, f, indent=2)
            f.write("\n")

    return alive_rest, alive_rpc


def main():
    if len(sys.argv) < 2:
        print("usage: update_endpoints.py <chains_dir> [--dry-run]")
        sys.exit(1)

    chains_dir = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    files = sorted(
        os.path.join(chains_dir, f)
        for f in os.listdir(chains_dir)
        if f.endswith(".json")
    )

    print(f"{'DRY RUN' if dry_run else 'APPLY'}  ({len(files)} chains)")
    print("  format: chain_name  rest: local+registry→alive  rpc: local+registry→alive")
    print()

    for p in files:
        try:
            process_chain(p, dry_run=dry_run)
        except Exception as e:
            print(f"  ERROR {os.path.basename(p)}: {e}")


if __name__ == "__main__":
    main()
