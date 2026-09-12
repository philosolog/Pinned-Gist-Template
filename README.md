# Pinned Gist Template 📌

**A starter template for updating a pinned GitHub Gist on a schedule.** Point
`get_content()` at any data source and this template handles the rest:
rate limiting, diff-checked gist updates, and the GitHub Actions schedule.

## What's reusable vs. what you replace

- Reusable: env var loading, rate limiting (`.last_update_time`), the
  `update_gist()` function (fetches current gist content, skips the API
  call if nothing changed), and the `.github/workflows/schedule.yml` cron job.
- Replace: `get_content()` in [main.py](main.py). It ships with a trivial
  example (a greeting + UTC timestamp) that proves the plumbing works.
  Swap it for a call to whatever API/data source your pinned gist should
  reflect.

## Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A GitHub account with a personal access token

### Installation

1. **Create a GitHub Gist**

   - Go to https://gist.github.com/
   - Create a new public gist (any starter content is fine)
   - Note the gist ID from the URL (e.g., `https://gist.github.com/username/{GIST_ID}`)

2. **Create a GitHub Personal Access Token**

   - Go to Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Generate a new token with **Gists: Read and write** permission
   - Copy the token

3. **Configure Repository Secrets**

   In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

   - `GIST_ID`: Your gist ID
   - `GH_TOKEN`: Your GitHub personal access token
   - `GIST_FILENAME`: The filename to write inside the gist (e.g. `📊 My Stats`)

4. **Enable the workflow**

   The schedule in [.github/workflows/schedule.yml](.github/workflows/schedule.yml)
   runs hourly and can also be triggered manually from the Actions tab
   (`workflow_dispatch`).

### Local testing

```bash
export GIST_ID=your_gist_id
export GH_TOKEN=your_github_token
export GIST_FILENAME="📊 My Stats"
uv run python main.py
```

Delete `.last_update_time` between manual runs if you want to bypass the
one-hour rate limit while testing.

## Adapting this template to a new project

1. Rename the project in `pyproject.toml` (`name`, `description`).
2. Replace the body of `get_content()` in [main.py](main.py) with a call
   to your data source, and return the string you want displayed in the gist.
3. Add any new required env vars to `REQUIRED_ENV_VARS` in [main.py](main.py),
   the `env:` block in [.github/workflows/schedule.yml](.github/workflows/schedule.yml),
   and the repository secrets.
4. Add any new dependencies with `uv add <package>`.
5. Update this README's setup section for your project's specific secrets.

## Development

```bash
uv sync
uv run ruff check .
uv run ruff format .
uv run mypy .
```
