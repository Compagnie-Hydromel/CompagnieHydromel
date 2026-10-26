# Docker deployment

The root `Dockerfile` builds the React application and installs Python dependencies
in separate stages. The final image runs as UID/GID **10001:10001**, contains the
bots and compiled web interface, and defaults to `python3 bot.py webserver`.
Python 3.13 and Node 22 are used. Supported image platform: `linux/amd64`.

## 1. Configuration

Run these commands from the repository root:

```bash
cp docs/docker/.env.example docs/docker/.env
```

Edit `docs/docker/.env` with all three Discord bot tokens, the public `APP_URL`, a
random `SESSION_SECRET_KEY` and distinct `BUS_WEBSERVER_TOKEN`, `BUS_BARMAN_TOKEN`,
`BUS_MENESTREL_TOKEN`, `BUS_ARCHIVEUSE_TOKEN` values (`openssl rand -hex 32` for each).
Music streams directly with yt-dlp and FFmpeg (included in the image), without
Lavalink or saved audio files. All components communicate through the shared
WebSocket bus at `ws://webserver:8000/api/internal/bus`; there is no music-specific
listener or port 8001. Do not expose `/api/internal/bus` through your public reverse
proxy; keep it on a private network, or use WSS and scoped tokens for remote components.
See [communication.md](../communication.md). Docker Discord connections need
outbound HTTPS/WebSocket access (and UDP when using voice).

The webserver defaults to the Barman token with commands disabled. Enable the
required Discord privileged intents for your bots in the Developer Portal.

## 2. Build and start (SQLite)

```bash
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml up -d --build
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml logs -f
```

Open <http://localhost:8000>. Use `/web` in Discord for the login link.
The sample binds the web port to host loopback. For remote access, place it behind
an HTTPS reverse proxy and set `APP_URL` accordingly; or explicitly change
`WEB_BIND_ADDRESS` if you intend to expose the HTTP listener.

The one-shot `migrate` service must succeed before the four application services
start. Services use the same image but run separate commands, so Docker can stop
and restart each process independently. Their shared named `hydromel-data` volume
contains SQLite, uploaded images, attachments, caches and SQL logs. Application
`log.txt` stays in each container's writable layer; `docker compose logs` also
captures application output. Back up the data volume; stop writers before backing
up SQLite. Do not run multiple replicas with this SQLite example; use MariaDB for
busier deployments. Uploaded files must remain shared with all bots and webservers.

## MariaDB example

Set distinct strong `DB_PASSWORD` and `MARIADB_ROOT_PASSWORD` in `.env`, then start
with the override **from the first deployment**:

```bash
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml -f docs/docker/compose.mariadb.yml up -d --build
```

MariaDB is internal to the Compose network and starts before migrations. Its
database is stored in `mariadb-data`; uploads stay in `hydromel-data`. Changing
database backend does **not** migrate existing SQLite data. Keep both Compose
files in subsequent commands when using MariaDB. Credentials initialize MariaDB
only when its data volume is empty; editing `.env` does not rotate existing users.

## Published images and updates

CI publishes `ghcr.io/<owner>/<repository>` (lowercase) using `GITHUB_TOKEN`:

- push to `main`: `latest` and `sha-<commit>`;
- push a Git tag, e.g. `v1.2.3`: `v1.2.3` and `sha-<commit>`; tags do not replace `latest`;
- pull requests: build only, no login or publication;
- manual run: publish a commit image; `latest` only when run on `main`.

Set `HYDROMEL_IMAGE` to the correct repository and desired tag in `.env`. The
example defaults to `ghcr.io/compagnie-hydromel/compagniehydromel:latest`. Prefer a
release tag or digest in production. Repository Actions must have permission to
write packages. Set package visibility to public for unauthenticated pulls, or
run `docker login ghcr.io` with credentials authorized to read the package.

For a fresh deployment using the prebuilt image instead of building:

```bash
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml pull
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml up -d --no-build
```

For an update, back up your data, stop the application, pull, and recreate services
so migrations run with the new image before the bots start:

```bash
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml down
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml pull
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml up -d --no-build
```

`down` without `-v` preserves data. **Do not use `down -v` unless you intend to
delete the database and uploads.** Pin/back up before upgrading; migrations may
change your database schema. Git-based Python dependencies currently follow the
refs in `requirements.txt`, including MIWOS `main`, so rebuilding an old source
revision is not guaranteed to reproduce identical dependencies.

## Administration commands

```bash
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml run --rm --no-deps webserver superadmin add 123456789012345678
docker compose --env-file docs/docker/.env -f docs/docker/compose.yml run --rm --no-deps webserver superadmin list
```

Any `bot.py` subcommand can replace `superadmin ...` (for example `migrate`). Never
run database migrations concurrently with live writers. If using bind mounts
instead of named volumes, pre-create and make the storage directory writable by
UID/GID 10001:10001. The image excludes `.env`, local databases, uploads, virtual
environments and `node_modules` from its build context. Runtime configuration and
tokens belong in `.env`, never in the image or Git repository.

## CI validation

The workflow validates both Compose examples with
`HYDROMEL_ENV_FILE=.env.example`, which selects the committed example for the
services' `env_file` as well as the CLI's interpolation file. No real `.env` or
Discord credentials are needed for validation. Normal deployments still default
to the required `.env` file. This avoids relying on `--no-env-resolution`, whose
handling of missing service env files differs between Compose versions.
