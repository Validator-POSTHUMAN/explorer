# explorer (ping.pub fork) — posthuman

Live at: **https://explorer.posthuman.digital/**

A multi-chain Cosmos explorer (Vue 3 + Vite SPA), fork of `github.com/ping-pub/explorer`.
Serves 27 mainnet chains (Cosmos hub, Osmosis, Celestia, Babylon, Injective, etc.).

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
yarn build-only          # vite build → dist/
                         # (don't use `yarn build` — type-check fails on
                         #  untracked src/libs/api/registry.ts; non-blocking
                         #  for runtime)
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
  - `master` ← tracks upstream `ping-pub/explorer` master + earlier
    posthuman merges. Has the redesign (~250 commits ahead of `1f98c1b`)
    that we tried and rolled back due to performance/UI regressions.
- **Untracked:** `SERVER-README.md` (this file — kept local on purpose).

## Updating chain endpoints

RPC/LCD endpoints rot quickly. To refresh from `cosmos/chain-registry`:

```bash
python3 /tmp/update_endpoints.py /srv/data/apps/explorer/chains/mainnet
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
- `src/libs/api/` is committed (api customization layer) but has TS errors
  in `registry.ts` that block `yarn build` (full type-check). Cosmetic —
  `yarn build-only` skips vue-tsc and produces a working bundle. Real fix
  is on `master` (the missing `src/types/group.ts`) but blocked by other
  master regressions.
- nginx CVE-2026-42945 (Rift, heap overflow in `ngx_http_rewrite_module`):
  installed `nginx 1.18.0-6.1+deb11u2` is in affected range, but no
  `rewrite`/`set $var` directives in any config → trigger path unreachable.
  Apply Debian DSA when it lands.

## Other operational notes

- `/srv/data/apps/explorer-preview/` is a `git worktree` from `master` for
  ad-hoc preview testing. `yarn dev` there binds to `127.0.0.1:5180` only;
  access via SSH tunnel:
  ```
  ssh -L 5180:127.0.0.1:5180 valoper@65.21.7.184
  ```
  Not auto-started; run `yarn dev` manually when needed.
- Old nginx site files (`test.claim`, `next`, `explorer2`/atomone-explorer)
  moved to `/etc/nginx/sites-available/_disabled/` on 2026-05-14 — kept
  recoverable.
