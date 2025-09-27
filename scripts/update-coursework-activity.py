from datetime import datetime, timezone, timedelta
import requests
from dateutil.parser import parse as parse_date

ORG = "Coursework-Archive"
REPOS = [
    "python-coursework",
    "sql-fundamentals",
    "java-core-fundamentals",
    "java-testing-labs",
    "build-tool-fundamentals",
    "web-dev-coursework",
    "js-ts-testing-labs"
]

now = datetime.now(timezone.utc)

def get_last_commit(repo):
    url = f"https://api.github.com/repos/{ORG}/{repo}/commits?per_page=1"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None
    commit = resp.json()[0]
    commit_date = parse_date(commit["commit"]["committer"]["date"])
    days_ago = (now - commit_date).days
    short_date = commit_date.strftime("%b %d, %Y")
    return days_ago, short_date


def get_commit_count_last_week(repo):
    week_ago = now - timedelta(days=7)
    url = (
        f"https://api.github.com/repos/{ORG}/{repo}/commits"
        f"?since={week_ago.isoformat()}&per_page=100"
    )
    resp = requests.get(url)
    if resp.status_code != 200:
        return 0
    return len(resp.json())
    

def build_table():
    lines = [
        "| Repository | Activity |",
        "|------------|----------|",
    ]
    for repo in REPOS:
        last = get_last_commit(repo)
        if not last:
            continue
        days_ago, short_date = last

        # Step 1: frequency in past week
        count = get_commit_count_last_week(repo)
        if count >= 3:
            display = f"🌳 {short_date}"
        elif count == 2:
            display = f"🌿 {short_date}"
        elif count == 1:
            display = f"🌱 {short_date}"
        else:
            # Step 2: fallback to recency buckets
            if days_ago > 90:
                display = f"🌊 {days_ago} days ago"     # > 3 months
            elif days_ago > 60:
                display = f"🍂 {days_ago} days ago"     # > 2 months
            elif days_ago > 30:
                display = f"🍁 {days_ago} days ago"     # > 1 month
            else:
                # no commits this week, but last commit within 30 days
                display = f"🍃 {days_ago} days ago"

        lines.append(f"| [{repo}](https://github.com/{ORG}/{repo}) | {display} |")

    return "\n".join(lines)

def update_readme(path="README.md"):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    new_section = build_table()

    updated = replace_section(
        content,
        marker="ACTIVITY-TABLE",
        new_text=new_section
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print("[SUCCESS] README.md updated.")

def replace_section(content, marker, new_text):
    start_marker = f"<!-- {marker}:START -->"
    end_marker = f"<!-- {marker}:END -->"

    start = content.find(start_marker)
    end = content.find(end_marker)

    if start == -1 or end == -1:
        raise ValueError("Could not find section markers in README.")

    return (
        content[: start + len(start_marker)] + "\n" +
        new_text + "\n" +
        content[end:]
    )

# === Run update
update_readme("profile/README.md")
