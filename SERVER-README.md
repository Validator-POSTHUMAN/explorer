# explorer (ping.pub fork) — posthuman

Live at: **https://explorer.posthuman.digital/**

A multi-chain Cosmos explorer (Vue 3 + Vite SPA), fork of `github.com/ping-pub/explorer`.
Serves 27 chains (Cosmos hub, Osmosis, Celestia + Celestia Testnet (Mocha),
Babylon, Injective, etc.). Testnets shown in the main list live in
`chains/mainnet/` — the `chains/testnet/` dir is only loaded when the
hostname contains "testnet", which never matches this domain.

## How it's deployed

**Static build served by nginx — no Node process at runtime.**

```
/srv/data/apps/explorer/dist/         ← built SPA (Vite output)
/etc/nginx/sites-available/explorer.posthuman.digital  ← nginx config
```

nginx config: `root /srv/data/apps/explorer/dist; index index.html;` with SPA
fallback (`try_files $uri $uri/ /index.html;`). Hashed `/assets/*` cached for
1 year; `index.html` `no-cache` so deploys propagate immediately. Dotfiles
denied at nginx level as defense-in-depth.

History: was served via `pm2` + `vite --host` (dev mode) → that exposed the
repo root (`.git/`, `vite.config.ts`, `src/`) publicly. Switched to static
`dist/` serving on 2026-05-14.

## Deploy / rebuild

After any change in `chains/`, `src/`, or `public/`:

```bash
cd /srv/data/apps/explorer
yarn build-only          # vite build → dist/ (fast path, skips type-check)
                         # `yarn build` (with vue-tsc) also works since the
                         # group types fix — use either
```

nginx auto-picks up the new `dist/` — no reload needed (hashed asset
filenames invalidate browser caches automatically).

If you ever need to undo a deploy: rebuild from prior commit
(`git checkout <prev-sha> && yarn build-only`). `dist/` is regenerated.

## Git layout

- **Remote:** `git@github.com:Validator-POSTHUMAN/explorer.git`
- **Branches of interest:**
  - `posthuman-prod` ← **what's deployed.** Branched from `1f98c1b` (April
    2025); contains posthuman customizations + endpoint refresh on top.
  - `dev-redesign` ← the upstream-merged + posthuman-redesign branch (was
    `master` locally). Has ~250 commits ahead of `1f98c1b` including the
    redesign that we tried and rolled back due to performance/UI
    regressions. Kept for ad-hoc testing.
    - Old `master`/`redesign`/`new-navbar`/etc. branches on GitHub were
    deleted 2026-05-15 — the only branches on origin now are the four
    above (two prod + two dev-redesign).
- The two server checkouts (`explorer/` and `explorer2/`) share this
  remote. To keep branch names unambiguous, explorer2 uses the suffix
  `-celestia` (e.g., `posthuman-prod-celestia`).

## Updating chain endpoints

RPC/LCD endpoints rot quickly. To refresh from `cosmos/chain-registry`:

```bash
python3 scripts/update_endpoints.py /srv/data/apps/explorer/chains/mainnet
```

The script merges local + chain-registry endpoints, probes each for
liveness (`/cosmos/staking/v1beta1/pool` for REST, `/status` for RPC),
keeps only working ones. Safe — if all probes fail, keeps original list.

After refresh: `yarn build-only` to bake new endpoints into the bundle.

## SSL

Cert managed by Certbot (`/etc/letsencrypt/live/explorer.posthuman.digital/`),
auto-renews via systemd timer when <30 days left.

## Known issues

- 284 vulns reported by `yarn audit` — almost all in dev tree, not bundled.
- `bostrom` was removed 2026-07-03 — zero live public endpoints anywhere
  (local lists, chain-registry, publicnode all dead).
- `fuel` (Fuel Sequencer, seq-mainnet-1) is NOT in cosmos/chain-registry —
  endpoint source of truth is FuelLabs/fuel-sequencer-deployments on GitHub.
  Using Simply Staking + Cumulo (probed alive 2026-07-03). Polkachu's
  fuel-api answers with different pool numbers (wrong network?) — avoided.
- `rpc.babylon.posthuman.digital` / `rest-api.babylon.posthuman.digital`
  (95.217.229.104, another posthuman host) answer 404 — proxy up, node gone.
  Removed from babylon-testnet.json (replaced with Nodes.Guru + Polkachu,
  bbn-test-5); re-add once the node is fixed.
- nginx CVE-2026-42945 (Rift, heap overflow in `ngx_http_rewrite_module`):
  installed `nginx 1.18.0-6.1+deb11u2` is in affected range, but no
  `rewrite`/`set $var` directives in any config → trigger path unreachable.
  Apply Debian DSA when it lands.

## Other operational notes

- `/srv/data/apps/explorer-preview/` is a `git worktree` from
  `dev-redesign` for ad-hoc preview testing. `yarn dev` there binds to
  `127.0.0.1:5180` only; access via SSH tunnel:
  ```
  ssh -L 5180:127.0.0.1:5180 valoper@65.21.7.184
  ```
  Not auto-started; run `yarn dev` manually when needed.
- Old nginx site files (`test.claim`, `next`, `explorer2`/atomone-explorer)
  and their certbot certs were removed 2026-05-15 — fully purged from
  `sites-available/`, `sites-enabled/`, and `/etc/letsencrypt/live/`.
