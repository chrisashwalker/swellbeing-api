# Swellbeing API

## Notes

- This is a Flask application, with `uv` as the preferred package/project manager. To run scripts using the venv, you'll probably want to insert `uv run` at the start of commands.

- I have installed `ruff` for linting and formatting. I have installed `pytest` for testing. I have installed `gunicorn` as the web server. 

- `flask-sqlalchemy` is used for ORM. `flask-migrate` handles database migrations.

- The repository is kept up-to-date using `Renovate`. Renovate PRs are configured to be raised in Draft, to make it easier to exclude them from automated workflow/pipeline runs, until they are deemed ready to review.

- There is a CI workflow to run lint and format checks, and run tests. The workflow must pass before a PR can be merged.

- There is a workflow to build and publish a Docker image when the main branch is updated. A two-stage build starts with a builder image, with build dependencies installed, but the final runtime image is leaner.

## Database migrations

With the `DATABASE_*` environment variables configured, run
`flask --app swellbeing_api.app db upgrade` before starting the production server.
Application startup only creates tables automatically when `TESTING=true`.

Create future migrations with `flask --app swellbeing_api.app db migrate -m "Description"`
and review the generated migration before applying it.
