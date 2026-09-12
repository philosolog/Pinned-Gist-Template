"""Pinned Gist Template - generic GitHub Gist content updater.

Fetches content via `get_content()` and pushes it into a pinned GitHub Gist,
skipping the update when nothing changed or the last run was too recent.

To adapt this template: replace the body of `get_content()` with a call to
whatever API/data source your pinned gist should reflect. Everything else
(env vars, rate limiting, diff-checked gist update) is reusable as-is.
"""

import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

REQUIRED_ENV_VARS = ("GIST_ID", "GH_TOKEN", "GIST_FILENAME")
missing_env_vars = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
if missing_env_vars:
    print(
        f"Error: Missing required environment variables: {', '.join(missing_env_vars)}",
        file=sys.stderr,
    )
    sys.exit(1)

GIST_ID = os.environ["GIST_ID"]
GITHUB_TOKEN = os.environ["GH_TOKEN"]
GIST_FILENAME = os.environ["GIST_FILENAME"]

RATE_LIMIT_FILE = Path(".last_update_time")
RATE_LIMIT_HOURS = 1


def check_rate_limit() -> bool:
    """Check if enough time has passed since the last update.

    Returns:
            True if update is allowed, False if rate limited.
    """
    if not RATE_LIMIT_FILE.exists():
        return True

    try:
        last_update = float(RATE_LIMIT_FILE.read_text().strip())
        time_since_update = time.time() - last_update
        hours_since_update = time_since_update / 3600

        if hours_since_update < RATE_LIMIT_HOURS:
            print(
                f"Rate limited: Last update was {hours_since_update:.2f} hours ago. "
                f"Minimum interval is {RATE_LIMIT_HOURS} hour(s)."
            )
            return False
    except (ValueError, OSError) as e:
        print(f"Warning: Could not read rate limit file: {e}")

    return True


def update_rate_limit_timestamp() -> None:
    """Update the timestamp of the last successful update."""
    try:
        RATE_LIMIT_FILE.write_text(str(time.time()))
    except OSError as e:
        print(f"Warning: Could not write rate limit file: {e}")


def update_gist(github_token: str, gist_id: str, filename: str, content: str) -> None:
    """Update the GitHub Gist with new content, skipping if unchanged.

    Args:
            github_token: GitHub personal access token with gist write access
            gist_id: ID of the gist to update
            filename: Name of the file within the gist to write
            content: Content to write to the file
    """
    get_resp = requests.get(
        url=f"https://api.github.com/gists/{gist_id}",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/json",
        },
        timeout=30,
    )

    try:
        get_resp.raise_for_status()
        current_gist = get_resp.json()
        current_files = current_gist.get("files", {})

        if filename in current_files:
            current_content = current_files[filename].get("content", "")
            if current_content == content:
                print("No changes detected in gist content. Skipping update.")
                return

        print("Changes detected. Updating gist...")
    except requests.exceptions.HTTPError as error_message:
        print(f"Warning: Could not fetch current gist content: {error_message}")
        print("Proceeding with update anyway...")

    resp = requests.patch(
        url=f"https://api.github.com/gists/{gist_id}",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/json",
        },
        json={"description": "", "files": {filename: {"content": content}}},
        timeout=30,
    )

    try:
        resp.raise_for_status()
        print(f"Successfully updated gist: {filename}")
        update_rate_limit_timestamp()
    except requests.exceptions.HTTPError as error_message:
        print(f"Error updating gist: {error_message}")
        sys.exit(1)


def get_content() -> str:
    """Build the text to display in the pinned gist.

    Replace this example with a call to whatever API/data source your
    pinned gist should reflect (a game stat, a habit tracker, a build
    status, etc).
    """
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    return f"👋 Hello from Pinned Gist Template!\nLast updated: {now}"


def main() -> None:
    if not check_rate_limit():
        print("Skipping update due to rate limit.")
        sys.exit(0)

    content = get_content()
    update_gist(GITHUB_TOKEN, GIST_ID, GIST_FILENAME, content)


if __name__ == "__main__":
    main()
