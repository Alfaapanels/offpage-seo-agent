import anthropic
import json
import os
from anthropic import beta_tool
from datetime import date

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "solar panels aluminum composite panels building facade materials"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "3acm.com",
    "alpolic.com",
    "vitrabond.com",
]
DAILY_LOG_FILE = "backlink_activity_log.json"

client = anthropic.Anthropic()


def load_daily_log() -> dict:
    if os.path.exists(DAILY_LOG_FILE):
        with open(DAILY_LOG_FILE) as f:
            return json.load(f)
    return {}


def save_daily_log(log: dict):
    with open(DAILY_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def get_today_key() -> str:
    return str(date.today())


def get_completed_today(log: dict) -> list:
    return log.get(get_today_key(), [])


def record_activity(log: dict, activity: str):
    today = get_today_key()
    if today not in log:
        log[today] = []
    if activity not in log[today]:
        log[today].append(activity)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    exact_match_keywords = ["click here", "website", "here", "link"]
    if anchor_text.lower() in exact_match_keywords:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra"]):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {'Monitor' if has_link else 'Reach out to add your link'}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "suppliers"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Prospect Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\nI have a comprehensive guide at {your_content_url} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\n[Your Name]\nAlfa Panels",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post about aluminum composite panels, solar panels, or building facade solutions. I represent {your_site}, a leading supplier of high-quality panels.\n\nWould you be open to a collaboration?\n\nBest,\n[Your Name]\nAlfa Panels",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is great! I created {your_content_url} which covers aluminum composite panels and facade solutions that might help your readers.\n\nWould you take a look?\n\nBest,\n[Your Name]\nAlfa Panels",
        "mention": f"Subject: You mentioned {your_site} - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning {your_site} in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url} to give your readers a direct reference?\n\nThanks,\n[Your Name]\nAlfa Panels",
        "directory": f"Subject: Listing request for {prospect_site}\n\nHi {prospect_name},\n\nI'd like to submit {your_site} - Alfa Panels - for inclusion in your {their_page_topic} directory.\n\nAlfa Panels specializes in aluminum composite panels, facade cladding, and building materials used in construction projects worldwide.\n\nPlease let me know the submission process.\n\nBest,\n[Your Name]\nAlfa Panels",
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink is an opportunity for you.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to competitor.
    """
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Find what content earned {competitor_domain} this link\n2. Create better/comparable content on the same topic for {your_domain}\n3. Reach out to the linking page with your resource\n4. Emphasize Alfa Panels' unique product range and quality certifications"


@beta_tool
def log_backlink_activity(activity_description: str, target_url: str, activity_type: str) -> str:
    """Log a completed backlink building activity to avoid duplicates.

    Args:
        activity_description: Brief description of what was done.
        target_url: URL where the backlink was built or outreach was sent.
        activity_type: Type: 'directory_submission', 'forum_post', 'qa_answer', 'outreach_sent', 'guest_post_pitch'.
    """
    log = load_daily_log()
    activity_key = f"{activity_type}:{target_url}"
    completed = get_completed_today(log)

    if activity_key in completed:
        return f"SKIPPED - Already completed today: {activity_description} at {target_url}"

    record_activity(log, activity_key)
    save_daily_log(log)
    return f"LOGGED: {activity_type} - {activity_description}\nURL: {target_url}\nDate: {get_today_key()}"


def build_completed_context(log: dict) -> str:
    completed = get_completed_today(log)
    if not completed:
        return "No activities completed today yet."
    lines = [f"- {a}" for a in completed]
    return "Already completed today:\n" + "\n".join(lines)


def run_daily_backlink_builder():
    print(f"\nDaily Backlink Builder for: {DOMAIN}")
    print(f"Date: {get_today_key()}")
    print("=" * 60)

    log = load_daily_log()
    completed_context = build_completed_context(log)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_backlink_activity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist executing daily backlink building for {DOMAIN}.

Domain: {DOMAIN}
Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}
Today's date: {get_today_key()}

{completed_context}

Your mission today: BUILD ACTUAL BACKLINKS. Don't just analyze — execute and log every action.

TASK 1 — Directory & Resource Submissions
Search for relevant directories in the construction/building materials/solar panels industry:
- "aluminum composite panel suppliers directory"
- "building materials manufacturers directory site:*.org OR site:*.net"
- "construction materials supplier listings"
Find 3-5 real directory pages. Score each with score_link_prospect. For the top ones, generate outreach templates and log each with log_backlink_activity (type: directory_submission).

TASK 2 — Forum & Community Participation
Search for active forums and Q&A about:
- "aluminum composite panels forum questions"
- "facade cladding materials site:reddit.com OR site:quora.com OR site:stackexchange.com"
- "solar panels building integration questions"
Find threads where {BRAND_NAME} can add value. Fetch the top 2-3 pages. Draft helpful answers that naturally mention {DOMAIN} as a resource. Log each with log_backlink_activity (type: forum_post or qa_answer).

TASK 3 — Unlinked Brand Mentions
Search: "{BRAND_NAME}" -site:{DOMAIN}
Also search: "alfaapanels" -site:{DOMAIN}
For any mentions found, categorize with categorize_brand_mention and generate outreach templates (type: mention). Log each as outreach_sent.

TASK 4 — Competitor Backlink Gap Analysis
For 2 competitors from the list, search:
- "link:alucobond.com building materials"
- sites linking to competitors but not to {DOMAIN}
Identify the top 2 gap opportunities with identify_link_gap_opportunity. Score the linking pages. Generate outreach templates (type: resource or guest_post). Log as outreach_sent.

TASK 5 — Guest Post Opportunities
Search: "write for us" "aluminum composite panels" OR "building facade" OR "construction materials"
Also: "guest post" "solar panels cladding" OR "architectural cladding"
Find 2-3 real guest post opportunities. Score them. Generate pitches with generate_outreach_template (type: guest_post). Log as guest_post_pitch.

TASK 6 — Daily Summary Report
After completing all tasks, produce a concise summary:
- Total activities logged today
- Top 3 backlink opportunities found (with URLs)
- Estimated link value of each
- Actions the team should manually follow up on

Use the log_backlink_activity tool for every action you take. Be specific with URLs you find."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{get_today_key()}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report: {DOMAIN}\n")
        f.write(f"Date: {get_today_key()}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")


if __name__ == "__main__":
    run_daily_backlink_builder()
