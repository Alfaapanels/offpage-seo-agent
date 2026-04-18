import json
import os
from datetime import datetime
import anthropic
from anthropic import beta_tool

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "IPTV panel reseller streaming control panel hosting"
COMPETITORS = ["iptvpanel.com", "xtreamcodes.com", "flussonic.com"]
DAILY_TARGET = 5

STATE_FILE = "backlink_state.json"
DAILY_REPORTS_DIR = "daily_reports"


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"found_urls": [], "daily_logs": []}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


@beta_tool
def log_backlink_opportunity(url: str, link_type: str, priority: str, action: str) -> str:
    """Log a discovered backlink opportunity, skipping already-tracked URLs.

    Args:
        url: The URL where a backlink can be obtained.
        link_type: One of: directory, forum, blog, resource, guest_post, broken_link.
        priority: HIGH, MEDIUM, or LOW.
        action: Specific steps to acquire the backlink from this URL.
    """
    state = load_state()
    if url in state["found_urls"]:
        return f"Already tracked: {url}"
    state["found_urls"].append(url)
    state["daily_logs"].append({
        "date": datetime.now().isoformat(),
        "url": url,
        "type": link_type,
        "priority": priority,
        "action": action,
        "status": "found",
    })
    save_state(state)
    return f"Logged [{priority}] {link_type}: {url}"


@beta_tool
def get_tracked_urls() -> str:
    """Return all previously tracked URLs as a JSON array to avoid duplicates."""
    return json.dumps(load_state()["found_urls"])


def build_daily_backlinks() -> str:
    client = anthropic.Anthropic()
    today = datetime.now().strftime("%Y-%m-%d")
    state = load_state()

    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {today}")
    print(f"Domain      : {DOMAIN}")
    print(f"Tracked URLs: {len(state['found_urls'])}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=8000,
        tools=[
            log_backlink_opportunity,
            get_tracked_urls,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are a daily backlink builder for {DOMAIN} ({BRAND_NAME}).

Today: {today}
Goal : Find {DAILY_TARGET} NEW, high-quality backlink opportunities — quality over quantity.

Step 1 — call get_tracked_urls() and note every URL in the result. Never log a URL that already appears in that list.

Step 2 — search for NEW opportunities in each category below, then call log_backlink_opportunity() for each valid find:

1. DIRECTORIES
   Search: "{NICHE} directory" "submit your site" OR "add your site"
   Goal  : Find 1-2 niche-relevant directories that accept free or paid listings.

2. FORUMS & COMMUNITIES
   Search: "{NICHE} forum" OR "{NICHE} community" site:reddit.com OR site:quora.com
   Goal  : Find active threads/communities where {DOMAIN} can contribute and earn a contextual link.

3. RESOURCE PAGES
   Search: intitle:"best IPTV panels" OR "IPTV reseller tools" "resources" -site:{DOMAIN}
   Goal  : Find curated resource lists that could include {DOMAIN}.

4. GUEST POST OPPORTUNITIES
   Search: "{NICHE}" "write for us" OR "guest post guidelines" OR "contribute"
   Goal  : Find blogs accepting guest contributions on streaming/IPTV/panel topics.

5. BROKEN LINK OPPORTUNITIES
   Search: "{NICHE}" "useful links" OR "recommended tools" inurl:resources
   Fetch pages and look for dead external links that {DOMAIN} could replace.

For each opportunity:
- Confirm the site is live, legitimate, and topically relevant.
- Call log_backlink_opportunity() with a clear action plan.

End with a plain-text Daily Summary:
- How many new opportunities were logged today.
- Top 3 highest-priority links and exact next steps.
- Estimated time to acquire each top-priority link.""",
        }],
    )

    output_blocks = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                output_blocks.append(block.text)

    os.makedirs(DAILY_REPORTS_DIR, exist_ok=True)
    report_path = os.path.join(DAILY_REPORTS_DIR, f"backlinks_{today}.md")
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report — {today}\n")
        f.write(f"**Domain:** {DOMAIN}  \n")
        f.write(f"**Total tracked (cumulative):** {len(load_state()['found_urls'])}\n\n")
        f.write("\n\n".join(output_blocks))

    print(f"\nReport saved: {report_path}")
    return report_path


if __name__ == "__main__":
    build_daily_backlinks()
