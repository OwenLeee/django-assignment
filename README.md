# Django Assignment

## Before you start

Choose one route:

- **Local development:** install uv; it manages Python and the project dependencies.
- **Docker review:** install and start Docker with Compose; Python and uv are provided inside the image.

Both routes open the app at http://127.0.0.1:8000/admin/. Run only one server on
port 8000 at a time. This project currently provides the Django scaffold and admin;
catalog features and demo data are not implemented yet.

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

```sh
uv --version
uv python install
uv sync --locked --dev
uv run --locked python manage.py migrate
uv run --locked python manage.py createsuperuser
uv run --locked python manage.py runserver
```

Follow the prompts to create your own admin username and password. Password input
is not displayed in the terminal. Log in at http://127.0.0.1:8000/admin/.

Python 3.14.7 is pinned in `.python-version`; dependencies are locked in `uv.lock`.
The local database is `db.sqlite3` in the repository directory.

### Start again next time

```sh
uv run --locked python manage.py runserver
```

Stop with **Ctrl+C**. Your database and admin account remain available; you do not
need to repeat installation or `createsuperuser` each time.

### After pulling project updates

Stop the server, update your checkout, then sync dependencies and apply any new
migrations before restarting:

```sh
git pull --ff-only
uv python install
uv sync --locked --dev
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
Stop any local Django server using port 8000, then run:

```sh
docker compose build
docker compose run --rm web python manage.py migrate
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

The image contains a copy of the code; local edits are not live-mounted. Rebuild
after changing code or dependencies. For updates that can include migrations:

```sh
git pull --ff-only
docker compose down
docker compose build
docker compose run --rm web python manage.py migrate
docker compose up -d
```

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

## Checks

```sh
uv run --locked python manage.py check
uv run --locked python manage.py makemigrations --check --dry-run
uv run --locked python manage.py test
uv run --locked ruff check .
uv run --locked ruff format --check .
```

CI runs on pull requests targeting `main`. It also validates the Compose
configuration and builds the Docker image.
Feature tests will be added alongside implementation; currently there are no tests.

## Verification status

Local uv development and Docker via OrbStack were exercised on macOS with Apple
silicon. GitHub Actions passed on Ubuntu. The Windows instructions follow the
linked official installation guides but have not been tested on a Windows machine;
Docker Desktop on macOS has not been separately verified.
