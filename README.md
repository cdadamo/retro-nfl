# Retro NFL

A 64×32 football scoreboard with team-colored panels, logos, scores, possession, remaining timeouts, quarter/clock, down-and-distance, field position, and pregame division standings.

Created by cdadamo with OpenAI Codex, based on an enthusiast's classic Tidbyt layout references. This is an independent community project, not an official OpenAI, NFL, ESPN, Tidbyt, or Tronbyt product.

## Defaults

- Favorite team: Philadelphia Eagles (all 32 teams supported)
- Game-time focus: on, when the companion is installed
- Touchdown celebrations: always enabled in the companion
- Celebrate: either team, with a **My team only** option
- Time zone: America/New_York; change this to your IANA time zone

## What gets installed

The app at `apps/retronfl` works by itself as a normal scoreboard. The separately installed companion provides immediate touchdown overlays and game-time focus. Installing the app alone does not install a background service, pin the display, or trigger touchdown celebrations. The settings explicitly identify the features requiring the companion.

The companion follows settings saved in the app. It pins the configured scoreboard during the favorite team's live game and releases only pins it acquired when the game ends or focus is disabled. Quarter breaks and halftime remain in focus. Other manually pinned apps and night mode take precedence.

## App installation

While awaiting catalog review, add the `apps/retronfl` folder as a custom app using your Tronbyt server's custom-app upload/repository support. Then install **Retro NFL** on each desired display.

Set the app's **Render Interval Minutes** to **0** if you want a fresh render on each display request (live network responses are cached for 10 seconds); the catalog recommendation is a conservative one minute. Leave the server's generic **Autopin** off—the companion controls pinning only during a live game. Keep the normal display time around 10 seconds.

## Companion setup (Docker on the existing Tronbyt server)

The companion currently targets Tronbyt server 2.4.x with its SQLite data directory. PostgreSQL or remote hosted servers are not supported. This release has automated tests; its generalized all-team companion still needs a beta installation test. The earlier Philadelphia-specific implementation has run on physical displays during a live game.

1. Install the app and note each device ID and Retro NFL installation ID from the app's URL. Only configure displays you want this companion to manage.
2. In `companion/`, copy `.env.example` to `.env`, and `devices.example.json` to `devices.json`.
3. Set the existing server URL, the host path of its data directory, and the UID/GID that can read that directory. Use the LAN URL if your server does not listen on localhost. The sample names are placeholders.
4. Create `state/` and give the configured UID/GID write access to that directory. The Tronbyt data mount is read-only. The service uses the existing scoped device API keys in that database, without creating new keys or logging them.
5. Run `docker compose up -d --build` from `companion/`.
6. Check `docker compose logs --tail 30` and `state/health.json`. Select your team, focus preference, and celebration preference in the app's settings.

This compose file uses host networking, suitable for Linux NAS/server deployments. Docker Desktop networking differs and is not currently documented as supported. No additional inbound port is opened. No external account or paid API key is required by this implementation.

To uninstall, turn **Game-time focus** off while the companion is running and wait for its owned pin to clear, then run `docker compose down`. If you stopped it first, manually unpin the app in Tronbyt. Keep or remove the local state directory as desired.

## Data and delivery behavior

ESPN public feeds can be delayed, unavailable, or changed; this project has no service guarantee or affiliation. The companion polls every 10 seconds while a configured team's game is active and every minute otherwise, then requires two consistent touchdown observations. It uses explicit touchdown records, including defensive scores, rather than assuming a score increase means a touchdown.

On startup or after a long gap, existing touchdowns are treated as already seen. A touchdown is marked consumed before network delivery; failed or ambiguous pushes are not retried. This favors avoiding duplicate/old celebrations over guaranteeing every delivery. A sleeping/offline display, another manual pin, or a stale scoreboard can cause a celebration to be skipped.

After the roughly 3.8-second animation, the most recent rendered scoreboard is restored. Data-feed delay and device request timing remain in addition to polling latency. Temporary render failures may still release a server pin or interrupt live coverage. Final/recent and future game views are distinct from live views.

## Development

- `pixlet format apps/retronfl/retro_nfl.star`
- `pixlet check apps/retronfl`
- `python3 -m unittest discover -s companion -p 'test_*.py'`

Animation source is `companion/animation.star`; assets contain the original pixel artwork rendered for each team. The reference game GIF is not included. Team logos are fetched from ESPN at render time; their respective owners retain their rights. This project's code license does not grant rights to third-party trademarks or logos.

## Feedback and status

This is a public beta. Report problems through [GitHub Issues](https://github.com/cdadamo/retro-nfl/issues), including your Tronbyt version, app settings (without secrets), and expected versus observed behavior. Do not attach API keys, your database, or private logs.

Catalog submission is pending maintainer review. The companion is installed separately; its portable Docker setup has not yet been tested on a clean second installation.
