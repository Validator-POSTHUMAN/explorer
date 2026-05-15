# explorer2 — celestia-only

Live at: **https://celestia.posthuman.digital/** (through Cloudflare)

Same ping.pub codebase as `explorer/`, but config curated to a single chain:
celestia mainnet + celestia testnet.

## How it's deployed

**Static build served by nginx; Cloudflare in front.**

```
/srv/data/apps/explorer2/dist/         ← built SPA
/etc/nginx/sites-available/nodes2.posthuman.digital  ← nginx config
                                       (filename misleading — server_name
                                        is celestia.posthuman.digital)
```

Cloudflare → origin (this server, IP 65.21.7.184) → nginx (port 443) →
`dist/`. Origin TLS cert is Let's Encrypt; expired (Cloudflare seems to
ignore origin cert validity in current mode). Not urgent — can migrate to
Cloudflare Origin Certificate (15-year) later.

History: was served via `pm2` + `vite --host` (dev mode), exposing the repo
root. Switched to static on 2026-05-14.

## Deploy / rebuild

```bash
cd /srv/data/apps/explorer2
yarn build-only
```

Cloudflare may cache `/assets/*` for a few minutes after deploy. Hashed
filenames mean browsers re-fetch automatically; the only stale-cache risk
is `index.html` itself. Manual cache purge from Cloudflare dashboard if
needed.

## Git layout

- **Remote:** `git@github.com:Validator-POSTHUMAN/explorer.git` (shares origin
  with `explorer/`)
- **Branch deployed:** `posthuman-prod` (single commit on top of `41a6e48`
  "add celestia"), authored by Web3 Forever.

## Other notes

- See `../explorer/SERVER-README.md` for shared notes (endpoint refresh
  script, nginx CVE status, etc.).
- DNS records for this domain go through Cloudflare; the previously-broken
  Let's Encrypt renewal config was removed.
