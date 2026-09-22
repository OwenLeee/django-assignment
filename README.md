# Django Assignment

## Before you start

Choose one route:

- **Local development:** install uv for Python dependencies and Node/npm for the Tailwind CSS build.
- **Docker review:** install and start Docker with Compose; Python and uv are provided inside the image.

Both routes open the app at http://127.0.0.1:8000/admin/. Run only one server on
port 8000 at a time. Catalog models, native admin management and a demo fixture
are available. The public product search page is not implemented yet.

### Get the project (first time only)

Install [Git](https://git-scm.com/downloads) if needed, then run:

```sh
git clone https://github.com/OwenLeee/django-assignment.git
cd django-assignment
```

All commands below run from this repository directory. In a new terminal, return
to your checkout with `cd` before running them. The common commands work in macOS
Terminal and Windows PowerShell; platform-specific installation steps are below.

## Local development

### First-time setup

Install **uv 0.12.17**, the version used by CI and Docker. If it is already
installed, check `uv --version` first.

macOS Terminal:

```sh
curl -LsSf https://astral.sh/uv/0.12.17/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.12.17/install.ps1 | iex"
```

These are the [official uv installer commands](https://docs.astral.sh/uv/getting-started/installation/).
Reopen your terminal after installation so it can find `uv`, then return to the
repository directory. You do not need to install Python separately.

Install [Node.js 26.7.0](https://nodejs.org/en/download/archive/v26.7.0), matching
the Docker frontend build stage. Its distribution includes npm 11.19.0. On macOS,
use the `.pkg` installer; on Windows, use the `.msi` installer for your machine's
architecture. If Node is already managed by a version manager, select 26.7.0 there.
Reopen the terminal after installation and check `node --version` and `npm --version`.
On Windows PowerShell, if an execution-policy error blocks `npm.ps1`, use `npm.cmd`
in place of `npm` in the commands below.

```sh
uv --version
uv python install
uv sync --locked --dev
npm ci
npm run build:css
uv run --locked python manage.py migrate
uv run --locked python manage.py loaddata catalog/demo_catalog.json
uv run --locked python manage.py createsuperuser
uv run --locked python manage.py runserver
```

Follow the prompts to create your own admin username and password. Password input
is not displayed in the terminal. Log in at http://127.0.0.1:8000/admin/.

Python 3.14.7 is pinned in `.python-version`; dependencies are locked in `uv.lock`.
The local database is `db.sqlite3` in the repository directory.

The `loaddata` step loads the sample catalog described under [Demo data](#demo-data).
Skip it if you want an empty catalog; create your admin account separately either way.

### Start again next time

```sh
uv run --locked python manage.py runserver
```

Stop with **Ctrl+C**. Your database and admin account remain available; you do not
need to repeat installation or `createsuperuser` each time.

When editing templates or CSS, open a second terminal in the repository and run:

```sh
npm run watch:css
```

Keep it running alongside Django to rebuild CSS as source files change. Refresh
the browser to see the changes; stop the watcher with Ctrl+C. For a one-off build,
use `npm run build:css`. An unchanged checkout with existing compiled CSS only needs
the Django server; if `static/css/app.css` is missing, rebuild it first.

### After pulling project updates

Stop the server, update your checkout, then sync dependencies and apply any new
migrations before restarting:

```sh
git pull --ff-only
uv python install
uv sync --locked --dev
npm ci
npm run build:css
uv run --locked python manage.py migrate
uv run --locked python manage.py runserver
```

### VS Code on macOS and Windows

Open the repository folder and install the recommended Python and Ruff extensions.
Run **Python: Select Interpreter** and select this project's environment:

- macOS: `.venv/bin/python`
- Windows: `.venv\Scripts\python.exe`

The committed VS Code settings enable Ruff formatting on save. Terminal commands
use `uv run`, so manually activating `.venv` is unnecessary on either platform.

## Docker

### First-time setup

Install Docker Desktop for your platform, following its prerequisites:

- [macOS](https://docs.docker.com/desktop/setup/install/mac-install/): choose the
  Apple silicon or Intel installer for your Mac. An existing OrbStack installation
  with Docker/Compose support can also run this project.
- [Windows](https://docs.docker.com/desktop/setup/install/windows-install/): follow
  the WSL 2 backend setup and use **Linux containers** for this image.

Start Docker Desktop (or OrbStack on macOS), wait for its engine to be ready, then
verify it from your terminal:

```sh
docker info
docker compose version
```

Python, uv and Node are not required on the host for the current Docker setup.
The Dockerfile uses a Node build stage to run `npm ci` and `npm run build:css`,
then copies the resulting CSS into the Python image. Only the Django web service
runs; there is no separate frontend service or Node server.
Stop any local Django server using port 8000, then run:

```sh
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py loaddata catalog/demo_catalog.json
docker compose run --rm web python manage.py createsuperuser
docker compose up -d
```

Create your own admin account at the prompt, then log in at
http://127.0.0.1:8000/admin/. The same Compose commands work on macOS and Windows
PowerShell. This setup uses Django's development server for local review.

### Start again next time

Start your Docker engine, then run:

```sh
docker compose up -d
```

You do not need to rebuild or create another admin account for an unchanged project.

Stop and remove this project's containers with:

```sh
docker compose down
```

SQLite is stored at `/data/db.sqlite3` inside the container, backed by the
`sqlite_data` named volume. Ordinary `docker compose down` preserves it.
**`docker compose down -v` deletes the volume, including your database and admin account.**
Local and Docker databases are separate; an account created locally is not
automatically available in Docker.

### After pulling project updates

The image contains a copy of the code and compiled CSS; local edits are not
live-mounted. Rebuild after changing code, templates, CSS or dependencies. For
updates that can include migrations:

```sh
git pull --ff-only
docker compose down
docker compose build
docker compose run --rm web python manage.py migrate
docker compose up -d
```

For local template/CSS edits without database changes, use
`docker compose up -d --build`. No host-side `npm` command is required for Docker.

### Troubleshooting startup

```sh
docker compose ps -a
docker compose logs --tail=80 web
```

If port 8000 is occupied, stop the other server first. If Docker reports a
credential-helper error on macOS, check the Keychain prompt for Docker's credential
helper and retry the build after allowing the expected request.

During development, OrbStack port forwarding once returned connection resets while
Django worked inside the container. Updating and restarting OrbStack restored
access. This is a troubleshooting observation, not a required setup step; restarting
the engine affects its other running containers too.

## Demo data

I entered the demo catalog through Django admin and exported it with Django's
`dumpdata` command to `catalog/fixtures/catalog/demo_catalog.json`. It contains:

- 5 categories, 12 tags and 20 products.
- 62 product/tag associations and each product's category.
- The original creation and update timestamps.

The fixture includes only catalog records, with no users, credentials, sessions or
admin history. `migrate` creates the schema; it does not load demo records.
`loaddata` restores the records and their original timestamps. Create your own
admin account with `createsuperuser` as shown in the setup instructions.

If you already completed setup with an empty catalog, load the fixture explicitly:

```sh
# Local database
uv run --locked python manage.py loaddata catalog/demo_catalog.json

# Or the separate Docker database (rebuild first if the image predates the fixture)
docker compose run --rm web python manage.py loaddata catalog/demo_catalog.json
```

Use the command for your chosen setup route. After loading, open `/admin/` and
check the Categories, Tags and Products lists. Local and Docker databases do not
share data.

Load the fixture into a freshly migrated, empty catalog for the expected counts.
Do not reload it on every startup or project update: it can overwrite fields and
tag selections for records with matching primary keys, and it does not remove
unrelated records. It is a demo restoration step, not a general merge/import tool.
Back up an existing database before intentionally reloading it.

## Checks

Build the CSS before Django checks on a fresh checkout:

```sh
npm ci
npm run build:css
uv run --locked python manage.py findstatic css/app.css
uv run --locked python manage.py check
uv run --locked python manage.py makemigrations --check --dry-run
uv run --locked python manage.py test
uv run --locked ruff check .
uv run --locked ruff format --check .
```

CI runs on pull requests targeting `main`. It installs Node.js 26.7.0, runs
`npm ci` and builds CSS before the Django checks. It also validates the Compose
configuration and builds the Docker image.
The current 41 tests cover models and two focused admin workflows: product creation
with category/tags and stable product-list query counts as product count increases.

## CSS source and output

- `assets/css/input.css`: Tailwind entry stylesheet.
- `templates/`: Django templates whose class names are scanned during the build.
- `static/css/app.css`: generated CSS, excluded from Git and the Docker build context.
- `package.json` and `package-lock.json`: committed build scripts and locked frontend dependencies.

Django serves the compiled file at `/static/css/app.css` during local development.
`templates/base.html` links to it, but no catalog view renders that template yet;
the built-in admin retains its own styles. Use `findstatic` above to check discovery
and open http://127.0.0.1:8000/static/css/app.css with the server running to inspect
the served file.

## Verification status

The demo fixture was loaded into a fresh local SQLite database after applying all
migrations. All 37 records and 62 product/tag associations were verified, including
an exact comparison of exported fields, IDs, relationships and timestamps. The
local database was also rebuilt using this workflow. Fixture restoration inside
Docker has not yet been verified.

Local uv development and Docker via OrbStack were exercised on macOS with Apple
silicon. The Tailwind changes passed a local locked npm install, CSS build, Ruff
and Django checks, plus a Docker build and CSS discovery/HTTP check (200).
The initial backend/Docker CI passed on Ubuntu; the updated CSS workflow still
needs a GitHub Actions run. The Windows instructions follow the
linked official installation guides but have not been tested on a Windows machine;
Docker Desktop on macOS has not been separately verified.
