"""Update the "People Who Follow Me" section of README.md with the
current list of GitHub followers. Run by .github/workflows/update-followers.yml
on a schedule so the profile README stays live without manual edits.

This intentionally only reads public follower data (people who chose to
follow this account) via GitHub's REST API. GitHub does not expose, and
this script does not attempt to discover, anonymous profile visitors --
that information does not exist anywhere, for anyone.
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

USERNAME = "GopiDO"
README_PATH = "README.md"
AVATAR_SIZE = 60


def fetch_followers():
    followers = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/followers?per_page=100&page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": USERNAME})
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.loads(resp.read().decode())
        if not batch:
            break
        followers.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return followers


def build_block(followers):
    if not followers:
        avatars = "_No followers yet — be the first!_"
    else:
        cells = []
        for f in followers:
            login = f["login"]
            avatar = f"{f['avatar_url']}&s={AVATAR_SIZE * 2}"
            cells.append(
                f'<a href="{f["html_url"]}" title="{login}">'
                f'<img src="{avatar}" width="{AVATAR_SIZE}" height="{AVATAR_SIZE}" '
                f'style="border-radius:50%;margin:2px;" alt="{login}"/></a>'
            )
        avatars = " ".join(cells)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"{avatars}\n\n<sub>Last updated: {now} · {len(followers)} follower(s)</sub>"


def main():
    followers = fetch_followers()
    block = build_block(followers)

    with open(README_PATH, "r", encoding="utf-8") as fh:
        content = fh.read()

    new_section = "<!--FOLLOWERS:START-->\n" + block + "\n<!--FOLLOWERS:END-->"
    new_content, count = re.subn(
        r"<!--FOLLOWERS:START-->.*?<!--FOLLOWERS:END-->",
        lambda _m: new_section,
        content,
        flags=re.DOTALL,
    )

    if count == 0:
        print("No FOLLOWERS markers found in README.md — nothing to update.", file=sys.stderr)
        sys.exit(1)

    if new_content != content:
        with open(README_PATH, "w", encoding="utf-8") as fh:
            fh.write(new_content)
        print(f"README updated with {len(followers)} follower(s).")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
