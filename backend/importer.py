import re
from pathlib import Path

SOURCE = "https://github.com/ashishpatel26/500-AI-Agents-Projects"

def parse_markdown(text):
    projects = {}
    framework = "General"
    for line in text.splitlines():
        if line.startswith("### "):
            framework = re.sub(r"[^\w +.-]", "", line[4:]).strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        urls = re.findall(r"\]\((https://github.com/[^)]+)\)", cells[3])
        if not urls:
            continue
        url = urls[-1].rstrip("/")
        projects.setdefault(url, dict(name=cells[0].replace("**", ""), industry=cells[1], description=cells[2], framework=framework, url=url))
    return list(projects.values())

def load_snapshot():
    return parse_markdown((Path(__file__).resolve().parents[1] / "data/upstream-README.md").read_text())
