# Catalog System Design

Status: Design in progress. The requirements below describe my intended behavior;
implementation and verification are still in progress.

## 1. Purpose and scope

I am building a small material catalog to demonstrate Django models,
relationships, querysets, and views. Visitors can search and filter products,
and administrators maintain catalog data through Django admin.

I distinguish the assignment's explicit requirements from my own decisions
below. Where the assignment leaves behavior unspecified, I explain the behavior
I chose and why. I keep the application focused on catalog maintenance and
search rather than adding commerce features or production infrastructure.

## 2. Functional requirements

### Requirements from the assignment

| ID | Requirement |
| --- | --- |
| FR-01 | Model products, categories, and tags with appropriate relationships. |
| FR-02 | Populate sample data through Django admin: at least 5 categories, 10 tags, and 20 products. |
| FR-03 | Provide an HTML page that allows searching products by description. |
| FR-04 | Allow products to be filtered by category and tags. |
| FR-05 | Allow users to combine search and filter options. |

### My decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| FR-06 | I require each product to belong to exactly one category and allow zero or more tags. | I use categories for a primary classification and tags for optional, overlapping attributes. This keeps classification consistent without requiring every product to have tags. |
| FR-07 | I use an explicit GET search form and retain criteria in the URL and form controls. | Search URLs can be bookmarked or shared, and ordinary browser navigation works without custom JavaScript. |
| FR-08 | I combine description, category, and the tag predicate with AND. Within tags, I support all/any matching, defaulting to all. | Each filter narrows the result set. The tag toggle lets visitors choose whether every selected attribute is required or any one is sufficient. |
| FR-09 | I return each product once, order by name then ID, and display 10 products per page. | Deduplication prevents misleading results from tag joins. The ID breaks name ties, and pagination keeps pages manageable. |
| FR-10 | I display product name, full description, category, and all tags, plus the result count and an empty state. | Visitors can assess matches directly on the results page without a separate detail page. |
| FR-11 | I provide Clear filters, preserve criteria during pagination, and reset to page 1 for a new search. | Visitors can navigate or restart a search without manually reconstructing their criteria. |
| FR-12 | I return HTTP 400 with field errors and no results for invalid filters, retaining input for correction. I redirect invalid single page values to page 1 and oversized page values to the last page. | Invalid filters should not silently broaden a search. Page correction provides a usable destination when a page value is invalid or no longer available. |
| FR-13 | I use native Django admin for catalog maintenance and prevent deletion of a category that still has products. | Django admin provides the required data-entry workflow. Protected category deletion avoids accidentally removing products or leaving them unclassified. |

## 3. Non-functional requirements

### NFR based on requirements

I derived these quality targets from the assignment's requirements and evaluation
criteria. The assignment provides the basis; the implementation choices and
verification methods are mine. It does not prescribe these exact checks.

| ID | Quality target | Assignment basis | My decision and rationale | How I will verify it |
| --- | --- | --- | --- | --- |
| NFR-01 | Reproducible setup | The README must explain setup, execution, assumptions, and frontend build steps where applicable. | I document first-time setup and daily startup, commit dependency lockfiles, and export admin-entered demo data as a fixture so a reviewer can reproduce the catalog. | Follow the README from a fresh checkout, apply migrations, load the fixture, and start the app. Record which environments I actually tested. |
| NFR-02 | Data integrity | Models and relationships must be correct. | I enforce required values, trimming and length rules, case-insensitive category/tag name uniqueness, unique product–tag pairs, and protected category deletion to keep the catalog consistent. Invalid admin edits must not leave partial changes. | Test validation boundaries, duplicates, relationships, deletion, and failed admin submissions; inspect the generated constraints. |
| NFR-03 | Avoid N+1 queries when loading relationships | Query proficiency is an evaluation criterion; no specific query-count limit is given. | I aim to prevent the N+1 query problem in both the public catalog and admin: loading a product list must not trigger separate category and tag queries for every displayed product. | I will check that displaying more products does not trigger a separate category or tag query for each product. |
| NFR-06 | Maintainable code and repeatable checks | Code must be clean, readable, and well organized, with clear documentation and comments. | I separate model definitions and group search code by feature so related changes are easy to locate. I use Ruff, focused tests, and CI to catch formatting issues and regressions consistently. | Review module responsibilities and run lint, formatting, Django, migration, test, CSS-build, and Docker-build checks. |

### NFR by my assumptions

I assume this is a small catalog reviewed and run locally, with public read
access and restricted administrative writes. The following targets are my
additional choices, not explicit assignment requirements.

| ID | Quality target | My assumption and decision | Rationale | How I will verify it |
| --- | --- | --- | --- | --- |
| NFR-04 | Protected maintenance and safe text rendering | I allow browsing without an account, require native admin authentication and permissions for maintenance, and render product descriptions as escaped plain text. | Visitors only need read access; catalog editing must be restricted, and descriptions should be displayed as content rather than interpreted as HTML. | Check unauthorized admin access and render descriptions containing HTML-like text. |
| NFR-05 | Basic usability | I expect the search form to be usable by keyboard and at desktop and mobile widths, with visible labels and focus indicators. | A simple interface should remain understandable and operable without relying on a mouse or a wide screen. | Manually check labels, focus, search submission, Clear, pagination, and horizontal overflow. I do not claim formal accessibility certification. |
| NFR-07 | Persistent local Docker data | I store SQLite data in a named volume and expect normal container recreation to preserve it. | Rebuilding the application should not require re-entering the catalog. | Create data, recreate the service without deleting the volume, and confirm the data remains. This is not a backup guarantee. |

I do not set an availability SLA, concurrent-user capacity, or response-time
guarantee for this local assignment because I have no production workload or
hosting requirement against which to validate those targets.

## 4. Technical choices and boundaries

| My choice | Rationale |
| --- | --- |
| Django templates and full-page GET responses | I can implement the required interactions directly in Django and keep the frontend small. |
| SQLite | I avoid requiring a separate database service for a small, locally reviewed catalog. |
| Local uv development and a Docker setup | I use uv for my development workflow and provide a containerized way to run the project. |
| Compiled Tailwind CSS | I keep styling consistent while shipping a generated stylesheet without a frontend application runtime. |
| One catalog app, split model files, and a search feature package | I keep one domain and migration owner while making model definitions and search behavior easy to find. |
| 5 categories, 12 tags, and 20 products entered through admin | I meet the sample-data minimum and use overlapping tags to demonstrate different all/any search results. |

I exclude public registration, carts, orders, inventory management, product
detail pages, an independent REST API, asynchronous search, and production
deployment to keep the work focused on the assignment's core behavior.

## 5. Data flow and ERD

### High-level data flow

I separate public product searches from administrative catalog changes. Both
flows use the same Django application and SQLite database. The browser sends
requests to Django; Django reads or writes data and returns the response.

![Public catalog search and administrative catalog maintenance data flows](data-flow.svg)

### Entity relationship diagram

I use a required category relationship for each product and a many-to-many
relationship for tags. The generated junction table stores the product–tag
pairs; its combined unique constraint prevents duplicate associations.

![Catalog ERD showing Category, Product, Tag, and the Product–Tag junction table](erd.svg)

This is my proposed schema using Django field types. I will verify constraints
and generated field types against migrations. Trimming, non-blank values, and
length validation require explicit implementation; NOT NULL alone does not
enforce those rules. Django handles protected category deletion and junction
cleanup; the diagram does not claim database-level ON DELETE behavior.

Editable source: [draw.io diagrams](catalog-design.drawio).

Before submission, I will update these diagrams to match the final models and migrations before submission.
