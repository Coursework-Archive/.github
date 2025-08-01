import requests
from datetime import datetime, timezone
from dateutil.parser import parse as parse_date

ORG = "Coursework-Archive"
REPOS = [
    "python-coursework",
    "sql-fundamentals",
    "java-core-fundamentals",
    "java-testing-labs",
    "build-tool-fundamentals",
    "web-dev-coursework"
]

now = datetime.now(timezone.utc)

def get_last_commit(repo):
    url = f"https://api.github.com/repos/{ORG}/{repo}/commits?per_page=1"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    commit = response.json()[0]
    commit_date = parse_date(commit["commit"]["committer"]["date"])
    days_ago = (now - commit_date).days
    short_date = commit_date.strftime("%b %d, %Y")
    return days_ago, short_date

def build_table():
    lines = []
    lines.append("| Repository | Last Activity |")
    lines.append("|------------|---------------|")
    for repo in REPOS:
        result = get_last_commit(repo)
        if result:
            days_ago, short_date = result
            if days_ago <= 6:
                display = f"🌿 {days_ago} days ago"
            elif days_ago <= 14:
                display = f"🍁 {days_ago} days ago"
            elif days_ago <= 30:
                display = f"🍂 {days_ago} days ago"
            else:
                display = f"🕸️ {short_date}"
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
update_readme("README.md")
