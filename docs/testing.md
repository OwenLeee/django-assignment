# Testing and expected results

Run automated checks using the [README](../README.md#test).
The 67 tests cover models/admin (41), search forms (19) and querysets (7).
Public view/pagination tests are not currently part of that suite.

## Manual demo

These URLs assume the committed fixture and a server at `http://127.0.0.1:8000`.
Clear filters before each independent form test. A changed control only takes
effect after Search or Enter.

| Case | URL | Expected |
| --- | --- | --- |
| Initial catalog | [/products/](http://127.0.0.1:8000/products/) | 20 total; showing 1–10; All selected |
| Description keyword | [?q=CoUpLiNg](http://127.0.0.1:8000/products/?q=CoUpLiNg) | 2: 1-inch Rigid Conduit Coupling; 3/4-inch EMT Coupling |
| Wire & Cable | [?category=1](http://127.0.0.1:8000/products/?category=1) | 4 products |
| Commercial + Indoor, All | [?tag=1&tag=3&tag_mode=all](http://127.0.0.1:8000/products/?tag=1&tag=3&tag_mode=all) | 5 products |
| Same tags, Any | [?tag=1&tag=3&tag_mode=any](http://127.0.0.1:8000/products/?tag=1&tag=3&tag_mode=any) | 14 total; no duplicates |
| Any, page 2 | [?tag=1&tag=3&tag_mode=any&page=2](http://127.0.0.1:8000/products/?tag=1&tag=3&tag_mode=any&page=2) | Showing 11–14; tags/Any retained; Next unavailable |
| Keyword + category + tags, Any | [?q=conduit&category=2&tag=1&tag=3&tag_mode=any](http://127.0.0.1:8000/products/?q=conduit&category=2&tag=1&tag=3&tag_mode=any) | 3: 1-inch EMT Conduit; 3/4-inch EMT Conduit; 3/4-inch PVC Conduit |
| Same combination, All | [?q=conduit&category=2&tag=1&tag=3&tag_mode=all](http://127.0.0.1:8000/products/?q=conduit&category=2&tag=1&tag=3&tag_mode=all) | 1: 3/4-inch EMT Conduit |
| Lighting + Copper | [?category=5&tag=5](http://127.0.0.1:8000/products/?category=5&tag=5) | 0; empty message; no pagination |
| Name-only keyword | [?q=THHN](http://127.0.0.1:8000/products/?q=THHN) | 0; THHN occurs in names, not descriptions |
| Invalid category | [?category=abc](http://127.0.0.1:8000/products/?category=abc) | HTTP 400; Invalid category selection.; no products |
| Duplicate keyword | [?q=conduit&q=copper](http://127.0.0.1:8000/products/?q=conduit&q=copper) | HTTP 400; Enter only one search query.; no products |

Also verify:

- Search from page 2 resets to page 1; Previous/Next preserve filters.
- Clear removes all filters and restores the 20-product listing.
- Refresh or reopen a copied URL: submitted filters/results remain, provided data is unchanged.
- Category IDs: 1 = Wire & Cable, 2 = Conduit, 5 = Lighting.
  Tag IDs: 1 = Commercial, 3 = Indoor, 5 = Copper.

## Verification record

Reviewed on **2026-09-22**. The 67-test suite was rerun successfully during
documentation review. The checks below record the earlier implementation verification.

Merged styling commit
[`803b877`](https://github.com/OwenLeee/django-assignment/commit/803b8778cd0e926a17de7ff47925626288369c83)
passed 67 local tests and the missing-migration check. Styling checks also passed
CSS build and Ruff; [PR #9 checks](https://github.com/OwenLeee/django-assignment/pull/9/checks)
passed, including Docker build. CI runs on PRs, not separately after merge to main.

Local Django view checks covered HTTP status, counts and visible product names
for the 12 cases above. Desktop browser checks included search,
All/Any selection, pagination, Clear and empty/error presentation. These desktop
manual checks are separate from automated regression coverage.

The fresh local SQLite restore matched the fixture's 37 catalog records and
62 tag associations.

I verified a fresh Docker setup using the isolated Compose project
`catalog-final-check`: image build, migrations, fixture loading and application
startup. I checked the styling, the README demo combinations and the catalog's
20 products with 10 per page. I then ran
`docker compose -p catalog-final-check down` followed by
`docker compose -p catalog-final-check up -d`. All 20 products remained without
reloading the fixture, confirming named-volume persistence.

I have not tested Windows setup. Earlier Docker checks used OrbStack on macOS
Apple silicon.
