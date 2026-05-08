import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "aluminum composite panels, ACM panels, building cladding, facade panels"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "alpolicusa.com",
    "3acomposites.com",
]


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Target URL receiving the link.
        backlink_url: The URL providing the link.
        anchor_text: Anchor text used in the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "read more", "learn more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text — low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor '{anchor_text}'")

    if any(w in backlink_url.lower() for w in ["spam", "casino", "adult", "pharma"]):
        signals.append("TOXIC — disavow recommended")
    else:
        signals.append("Domain appears clean")

    authority_tlds = [".edu", ".gov", ".org"]
    if any(t in backlink_url for t in authority_tlds):
        signals.append("High-authority TLD (.edu/.gov/.org)")

    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: Text containing the brand mention.
        brand_name: Brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "love", "quality", "durable", "professional"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]

    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"

    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to request a link"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
    your_niche: str,
) -> str:
    """Score a potential link building prospect out of 100.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short content snippet.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []

    niche_words = your_niche.lower().split(",")
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w.strip() in content_lower)
    if relevance >= 2:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")

    high_value = ["resource", "guide", "tools", "directory", "blog", "list", "best", "suppliers"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/directory page (+30)")

    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority TLD (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")

    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 — {priority} PRIORITY\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the site owner or editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_content_url: URL of your content to be linked.
        link_type: One of 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    site = TARGET_DOMAIN
    brand = BRAND_NAME
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"I have a comprehensive resource at {your_content_url} from {brand} ({site}) that would be a perfect replacement.\n\n"
            f"Would you be open to swapping it in?\n\nBest regards,\n[Your Name]\n{site}"
        ),
        "guest_post": (
            f"Subject: Guest post idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I really enjoy the content on {prospect_site}, especially your {their_page_topic} coverage.\n\n"
            f"I'm a contributor at {brand} ({site}) and would love to write a guest post for your audience.\n\n"
            f"I have an original article about aluminum composite panels that would fit your readers well.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\n[Your Name]\n{site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is fantastic! I noticed it lists tools for your readers.\n\n"
            f"We recently published {your_content_url} at {brand} — it covers [specific topic] and I think your readers would find it valuable.\n\n"
            f"Would you consider adding it?\n\nBest regards,\n[Your Name]\n{site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {brand}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {brand} in your article about {their_page_topic}!\n\n"
            f"Would you consider linking directly to {your_content_url} so your readers can find us easily?\n\n"
            f"Thanks,\n[Your Name]\n{site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str,
    linking_page_topic: str,
) -> str:
    """Identify a competitor backlink as an opportunity for alfaapanels.com.

    Args:
        competitor_domain: Competitor's domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {TARGET_DOMAIN}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action plan:\n"
        f"1. Find the specific content on {competitor_domain} that earned this link\n"
        f"2. Create a better or more up-to-date version for {TARGET_DOMAIN}\n"
        f"3. Reach out to the linking page with your improved resource\n"
        f"4. Target similar pages in the same niche"
    )


@beta_tool
def record_backlink_submission(
    platform: str,
    url_submitted_to: str,
    link_type: str,
    anchor_text: str,
    status: str,
    notes: str,
) -> str:
    """Record a backlink submission or opportunity in the daily log.

    Args:
        platform: Platform name (e.g. 'Quora', 'Reddit', 'directory').
        url_submitted_to: The URL where the link was placed or pitched.
        link_type: Type: 'directory', 'qa', 'forum', 'guest_post', 'outreach'.
        anchor_text: Anchor text used or proposed.
        status: 'submitted', 'pitched', 'live', 'pending'.
        notes: Any relevant notes.
    """
    return (
        f"RECORDED: {link_type.upper()} on {platform}\n"
        f"URL: {url_submitted_to}\n"
        f"Anchor: {anchor_text}\n"
        f"Status: {status}\n"
        f"Notes: {notes}"
    )


def run_daily_backlink_session(date_str: str) -> str:
    """Run one daily backlink building session for alfaapanels.com."""
    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {TARGET_DOMAIN}")
    print(f"Session date: {date_str}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            record_backlink_submission,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist executing the daily backlink building plan for {TARGET_DOMAIN}.

Brand: {BRAND_NAME}
Niche: {NICHE}
Competitors: {", ".join(COMPETITORS)}
Today's date: {date_str}

Execute ALL of the following tasks and use the provided tools throughout:

---

TASK 1 — BRAND MENTION AUDIT
Search for unlinked mentions of "{BRAND_NAME}" and "alfaapanels" across the web.
Query: "{BRAND_NAME}" -site:{TARGET_DOMAIN}
Query: "alfaapanels" -site:{TARGET_DOMAIN}
Use categorize_brand_mention() on each mention found.
Identify top 3 unlinked mentions to target for link conversion.

---

TASK 2 — DIRECTORY & CITATION SUBMISSIONS
Find 5 relevant business directories or niche directories for aluminum composite panels / building materials.
Search for: "aluminum composite panels directory" OR "building materials supplier directory"
Search for: "ACM panels suppliers list"
For each directory found, use record_backlink_submission() to log it.
Score each with score_link_prospect().

---

TASK 3 — Q&A & FORUM OPPORTUNITIES
Search Quora and Reddit for questions about:
- "aluminum composite panels"
- "ACM cladding suppliers"
- "best facade panels"
- "building cladding materials"
Find 3-5 unanswered or under-answered questions where {TARGET_DOMAIN} could be referenced.
Use record_backlink_submission() to log each opportunity with status 'pitched'.

---

TASK 4 — COMPETITOR BACKLINK GAP ANALYSIS
For each competitor in [{", ".join(COMPETITORS)}]:
- Search: "link:{competitor}" or "site:{competitor} resources"
- Find pages linking to competitors but not to {TARGET_DOMAIN}
- Use identify_link_gap_opportunity() on each gap found
- Target the top 2 gaps per competitor

---

TASK 5 — RESOURCE PAGE & GUEST POST PROSPECTING
Search for:
- "aluminum composite panels" + "resources" OR "useful links" OR "suppliers"
- "building materials blog" + "write for us" OR "guest post"
- "facade cladding" + "resource page"
Score each prospect with score_link_prospect().
Generate outreach emails for the top 3 prospects using generate_outreach_template().

---

TASK 6 — BROKEN LINK OPPORTUNITIES
Search for resource pages in the niche that may have broken links:
- "aluminum panels resources" site:.org OR site:.edu
- "cladding suppliers list" inurl:resources
For any promising pages found, note them for broken link outreach.
Use analyze_backlink_quality() to evaluate any existing links on those pages.

---

TASK 7 — DAILY SUMMARY REPORT
Produce a structured daily report with:
- Total backlink opportunities identified today
- Breakdown by type (directory, Q&A, guest post, gap, resource page)
- Top 5 highest-priority actions for tomorrow
- Estimated domain authority impact
- Running total estimate of links built this week

Record all submissions and opportunities using record_backlink_submission().
""",
        }],
    )

    report_chunks = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_chunks.append(block.text)

    return "\n\n".join(report_chunks)


if __name__ == "__main__":
    from datetime import date
    report = run_daily_backlink_session(date.today().isoformat())
    filename = f"seo_report_{date.today().isoformat()}.md"
    with open(filename, "w") as f:
        f.write(f"# Daily Backlink Report — {TARGET_DOMAIN}\n")
        f.write(f"**Date:** {date.today().isoformat()}\n\n")
        f.write(report)
    print(f"\nReport saved: {filename}")
