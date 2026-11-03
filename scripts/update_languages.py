#!/usr/bin/env python3
"""Generate a text-only GitHub language breakdown, including private repos.

Uses a fine-grained personal access token with read-only Metadata access.
Does not clone code, reveal repository names or upload any files elsewhere.
"""

from collections import Counter
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ACCOUNT = "vuumanhhung"
README = Path(__file__).resolve().parent.parent / "README.md"
BEGIN = "<!-- LANGUAGE_STATS_START -->"
END = "<!-- LANGUAGE_STATS_END -->"


def github_json(path: str, token: str):
    req = Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "User-Agent": "vuumanhhung-profile-language-stats",
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as exc:
        # Do not include the URL, which could contain a private repository name.
        raise RuntimeError(
            f"GitHub API returned HTTP {exc.code}. Check PROFILE_STATS_TOKEN "
            "expiration, repository selection, and Metadata read permission."
        ) from None
    except URLError:
        raise RuntimeError("Could not connect to GitHub API.") from None


def collect_languages(token: str):
    totals = Counter()
    scanned = 0
    page = 1
    while True:
        repos = github_json(
            f"/user/repos?visibility=all&affiliation=owner&per_page=100&page={page}",
            token,
        )
        if not isinstance(repos, list):
            raise RuntimeError("Unexpected GitHub API response for repository list.")
        for repo in repos:
            # Only own code. Don't include forks, collaborator projects, or
            # the profile repository itself (whose README is mainly Markdown).
            if repo.get("owner", {}).get("login", "").lower() != ACCOUNT.lower():
                continue
            if repo.get("fork") or repo.get("name", "").lower() == ACCOUNT.lower():
                continue
            full_name = repo.get("full_name", "")
            if not full_name:
                continue
            # The API returns bytes per language as identified by GitHub Linguist.
            languages = github_json(
                f"/repos/{quote(full_name, safe='/')}/languages", token
            )
            if not isinstance(languages, dict):
                raise RuntimeError("Unexpected GitHub API response for languages.")
            for name, size in languages.items():
                if isinstance(size, int) and size > 0:
                    totals[name] += size
            scanned += 1
        if len(repos) < 100:
            break
        page += 1

    if scanned == 0:
        raise RuntimeError(
            "No owned repositories visible. Verify token belongs to @vuumanhhung "
            "and has access to all repositories."
        )
    return totals


def format_stats(totals: Counter) -> str:
    if not totals:
        return "*No languages detected in the accessible repositories.*"
    total_bytes = sum(totals.values())
    rows = [
        f"**{len(totals)} languages detected** across my GitHub projects.",
        "",
        "| Language | Share |",
        "| :--- | ---: |",
    ]
    for name, size in totals.most_common():
        safe_name = name.replace("|", r"\|")
        rows.append(f"| {safe_name} | {size / total_bytes:.1%} |")
    return "\n".join(rows)


def update_readme(table: str):
    old = README.read_text(encoding="utf-8")
    if old.count(BEGIN) != 1 or old.count(END) != 1:
        raise RuntimeError("README language-statistics markers are missing or duplicated.")
    prefix, remainder = old.split(BEGIN, 1)
    _, suffix = remainder.split(END, 1)
    new = prefix + BEGIN + "\n" + table + "\n" + END + suffix
    if new != old:
        README.write_text(new, encoding="utf-8")
    print(f"Language statistics generated: {table.split(' languages detected')[0].strip('*')} languages.")


def main():
    token = os.environ.get("PROFILE_STATS_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Missing PROFILE_STATS_TOKEN GitHub Actions secret. "
            "Create a fine-grained token and store it in repository Actions secrets."
        )
    update_readme(format_stats(collect_languages(token)))


if __name__ == "__main__":
    main()
