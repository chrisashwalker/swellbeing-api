# Swellbeing API

## Notes

- This is a Flask application, with `uv` as the preferred package/project manager. 

- I have installed `ruff` for linting and formatting. I have installed `pytest` for testing. I have installed `gunicorn` as the web server.

- The repository is kept up-to-date using `Renovate`. Renovate PRs are configured to be raised in Draft, to make it easier to exclude them from automated workflow/pipeline runs, until they are deemed ready to review.

- There is a CI workflow to run lint and format checks, and run tests. The workflow must pass before a PR can be merged.

- There is a workflow to build and publish a Docker image when the main branch is updated. A two-stage build starts with a builder image, with build dependencies installed, but the final runtime image is leaner.
