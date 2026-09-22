# Material Catalog

A Django catalog for searching electrical materials by description, category and tags.

## Get the code

Requires [Git](https://git-scm.com/downloads).

```sh
git clone https://github.com/OwenLeee/django-assignment.git
cd django-assignment
```

Choose Docker or local setup below. Keep port **8000** available.

## Run with Docker

Requires a running [Docker engine with Compose](https://docs.docker.com/get-started/get-docker/).
Docker builds the Python environment and CSS; no host Python or Node installation is needed.

```sh
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py loaddata catalog/demo_catalog.json
docker compose up -d
```

Open **http://127.0.0.1:8000/products/**. Expected: **20 products**, 10 on the first page.
No login is required for search.

To edit data in [Django admin](http://127.0.0.1:8000/admin/), create your own account:

```sh
docker compose run --rm web python manage.py createsuperuser
```

Stop: `docker compose down`. Restart: `docker compose up -d`.
Rebuild after source changes: `docker compose up -d --build`.
If startup fails: `docker compose logs --tail=80 web`.

SQLite persists in a named volume. **`docker compose down -v` deletes its data.**
This is a local-review setup using Django's development server and `DEBUG=True`.

## Run locally

Requires [uv 0.12.17](https://docs.astral.sh/uv/getting-started/installation/)
and [Node.js 26.7.0](https://nodejs.org/en/download/archive/v26.7.0).
From the cloned repository:

```sh
uv python install
uv sync --locked --dev
npm ci
npm run build:css
uv run --locked python manage.py migrate
uv run --locked python manage.py loaddata catalog/demo_catalog.json
uv run --locked python manage.py runserver
```

Open the same catalog URL. Optional admin account:
`uv run --locked python manage.py createsuperuser`.
Stop with Ctrl+C; restart with the `runserver` command.
For CSS changes, run `npm run watch:css` in a second terminal.
Python is pinned to 3.14.7; Django to 6.1.1. Dependencies have lockfiles.

## Demo data

The setup commands load [catalog/demo_catalog.json](catalog/fixtures/catalog/demo_catalog.json):
**5 categories, 12 tags, 20 products and 62 product–tag associations**.
I entered the sample catalog through Django admin, then exported it using
`dumpdata` so reviewers can reproduce the same dataset.

Load once into a freshly migrated database. Reloading can overwrite records with
matching IDs; it is not needed on restart. The fixture contains no admin account.
Local SQLite and the Docker volume are separate databases.

## Features and design

- Case-insensitive **description-only** search, combined with category and tags.
- Match **all** or **any** selected tags; no duplicate products.
- Explicit GET submission, shareable URLs, Clear filters and 10 results per page.
- Validation errors, empty results, full descriptions and native Django admin.

See [system design](docs/system-design.md) for requirements, design decisions,
query behavior, data flow and ERD.

## Test

After local setup:

```sh
uv run --locked python manage.py test
uv run --locked python manage.py check
uv run --locked python manage.py makemigrations --check --dry-run
uv run --locked ruff check .
uv run --locked ruff format --check .
```

Expected: **67 tests pass**, no system-check issues or migration changes, and Ruff passes.
To run Django tests in Docker: `docker compose run --rm web python manage.py test`.
The Docker runtime image does not include Ruff.

With demo data loaded, use **Clear filters** before each case, enter the combination,
and press **Search**. “None selected” means leave the category unselected.

| Keyword | Category | Tags | Match | Expected |
| --- | --- | --- | --- | --- |
| `CoUpLiNg` | None selected | None | All | 2 products |
| Blank | None selected | Commercial + Indoor | All | 5 products |
| Blank | None selected | Commercial + Indoor | Any | 14 products; Next shows 11–14 |
| `conduit` | Conduit | Commercial + Indoor | All | 1: 3/4-inch EMT Conduit |
| Blank | Lighting | Copper | All | 0 products; empty state |

[More test URLs and expected results](docs/testing.md).
CI checks Django, migrations, tests, Ruff, CSS build, Compose and Docker build on PRs.

## AI assistance

I used Codex throughout development for planning, explanations, code assistance
and review. I defined the intended behavior, supplied project context and sample
data, and revised the work through feedback and verification.

- **Planning:** scope discussions and sample material research.
- **Models and model tests:** I implemented
  [`catalog/models/`](catalog/models/) and the model test cases in
  [`catalog/tests/models/`](catalog/tests/models/), using AI explanations and
  examples as learning references. I worked through the concepts and reasoning,
  then applied them to the project's requirements in my own implementation.
- **Search queries:** I wrote the complete
  [`search_products`](catalog/search/queries.py) function, then used AI review
  suggestions to revise it.
- **Query tests:** for [`test_queries.py`](catalog/tests/search/test_queries.py),
  I directed AI-assisted tests to use my sample catalog and existing test style.
- **Templates and styling:** initial template examples and styling assistance.
  I wrote the functional HTML skeleton before developing the styled interface.
- **Documentation and demos:** AI-written drafts based on my project context,
  decisions and revision feedback.

I remain responsible for the submitted code, its verification, and explaining
the implementation and trade-offs.
