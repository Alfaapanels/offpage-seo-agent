import anthropic
import os
from datetime import datetime
from anthropic import beta_tool


def _get_auth_token() -> str | None:
    """Read OAuth token from Claude Code session token file if present."""
    token_file = os.environ.get(
        "CLAUDE_SESSION_INGRESS_TOKEN_FILE",
        "/home/claude/.claude/remote/.session_ingress_token",
    )
    if token_file and os.path.isfile(token_file):
        try:
            token = open(token_file).read().strip()
            if token:
                return token
        except OSError:
            pass
    return None


def _make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    auth_token = _get_auth_token()
    if auth_token:
        return anthropic.Anthropic(auth_token=auth_token)
    return anthropic.Anthropic()  # let the SDK raise its own error


client = _make_client()

# ── Alfaa Panels configuration ────────────────────────────────────────────────
TARGET_DOMAIN  = "alfaapanels.com"
BRAND_NAME     = "Alfaa Panels"
NICHE          = (
    "sandwich panel manufacturer insulated panels PUF PIR rockwool cold room "
    "clean room panels building construction India"
)
COMPETITORS    = [
    "thermocoolpanels.com",
    "isopanels.in",
    "metalspan.in",
    "rockwoolpanels.com",
    "enviropanels.com",
]
# ─────────────────────────────────────────────────────────────────────────────


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        quality_signals.append("Warning: Generic anchor text – low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(w in backlink_url.lower() for w in ["spam", "casino", "viagra", "adult"]):
        quality_signals.append("TOXIC link – disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and analyse sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing",
                      "quality", "reliable", "trusted", "certified", "leading"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos = sum(1 for w in positive_words if w in mention_text.lower())
    neg = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return (
        f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\n"
        f"Action: {'Monitor' if has_link else 'Reach out to convert to a link'}"
    )


@beta_tool
def score_link_prospect(
    page_url: str, page_title: str, page_content_snippet: str, your_niche: str
) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche/topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to panels/construction niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory",
                  "supplier", "manufacturer", "industry"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/directory/guide page – high link value (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High authority domain (+30)")
    elif any(s in page_url for s in [".in", "india"]):
        score += 20
        reasons.append("India-relevant domain – geo match (+20)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return f"Prospect Score: {score}/100 – {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: 'guest_post' | 'broken_link' | 'resource' | 'mention' | 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"Alfaa Panels has a detailed guide at {your_content_url} that would be a perfect replacement – "
            f"we're India's leading sandwich panel manufacturer with 30+ years of experience and BIS certification.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\nTeam Alfaa Panels\nalfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest article idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love the content on {prospect_site} about {their_page_topic}.\n\n"
            f"I'd like to contribute an expert article on insulated sandwich panels, cold room construction, "
            f"or clean room panel standards – topics your audience would value. "
            f"I write for Alfaa Panels (alfaapanels.com), India's only panel manufacturer with plants across all four corners of the country.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\nTeam Alfaa Panels"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent! "
            f"I thought {your_content_url} from Alfaa Panels might add real value for your readers – "
            f"we cover everything from PUF and PIR panels to cold room and clean room solutions, "
            f"backed by 30 years of manufacturing expertise and a 15-year product warranty.\n\n"
            f"Would you take a look?\n\nBest regards,\nTeam Alfaa Panels\nalfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfaa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfaa Panels in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It would help your readers find the full product information.\n\n"
            f"Thanks,\nTeam Alfaa Panels\nalfaapanels.com"
        ),
        "directory": (
            f"Subject: Add Alfaa Panels to your {their_page_topic} directory\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed your {their_page_topic} directory on {prospect_site} lists suppliers in our space.\n\n"
            f"Alfaa Panels (alfaapanels.com) is India's leading sandwich panel manufacturer – "
            f"PUF, PIR, rockwool, cold room, and clean room panels – BIS certified, 30+ years, 5 plants across India.\n\n"
            f"Could you add our listing?\n\nBest regards,\nTeam Alfaa Panels"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str, your_domain: str, linking_page_topic: str
) -> str:
    """Identify whether a competitor backlink is an opportunity for your site.

    Args:
        competitor_domain: Competitor's domain.
        your_domain: Your domain.
        linking_page_topic: Topic of the page linking to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Identify which page on {competitor_domain} earned this link\n"
        f"2. Create stronger, more comprehensive content on the same topic for {your_domain}\n"
        f"3. Pitch your resource to the linking page owner with a clear value proposition\n"
        f"4. Highlight Alfaa Panels' unique strengths: BIS cert, 15-yr warranty, pan-India manufacturing"
    )


@beta_tool
def find_directory_submission_targets(niche: str, location: str) -> str:
    """Find relevant business directories and trade portals to submit the site to.

    Args:
        niche: Industry niche (e.g. 'sandwich panels manufacturer India').
        location: Target geography (e.g. 'India').
    """
    targets = [
        ("IndiaMART", "indiamart.com", "B2B marketplace – high DA, free listing"),
        ("TradeIndia", "tradeindia.com", "B2B directory – construction/manufacturing niche"),
        ("ExportersIndia", "exportersindia.com", "Manufacturer directory"),
        ("Justdial", "justdial.com", "Local business directory – India"),
        ("Sulekha", "sulekha.com", "Service/product directory – India"),
        ("BizVibe", "bizvibe.com", "Global B2B directory – manufacturing"),
        ("Kompass", "kompass.com", "International trade directory"),
        ("Yellow Pages India", "yellowpages.co.in", "General business directory"),
        ("Go4WorldBusiness", "go4worldbusiness.com", "B2B trade portal"),
        ("BuildoTrade", "buildotrade.com", "Construction-specific trade directory"),
    ]
    result_lines = [f"DIRECTORY SUBMISSION TARGETS for '{niche}' in {location}:\n"]
    for name, domain, note in targets:
        result_lines.append(f"• {name} ({domain}) – {note}")
    result_lines.append(
        "\nAction: Submit alfaapanels.com profile with consistent NAP "
        "(Name, Address, Phone), product categories, and website URL to each directory."
    )
    return "\n".join(result_lines)


def run_offpage_seo_agent(
    your_domain: str = TARGET_DOMAIN,
    brand_name: str = BRAND_NAME,
    niche: str = NICHE,
    competitors: list = None,
):
    if competitors is None:
        competitors = COMPETITORS

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*60}")
    print(f"Off-Page SEO Agent – {brand_name}")
    print(f"Domain : {your_domain}")
    print(f"Date   : {today}")
    print(f"{'='*60}\n")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            find_directory_submission_targets,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist specialising in B2B manufacturing companies in India.

Perform today's daily backlink-building session for:

Domain      : {your_domain}
Brand       : {brand_name}
Niche       : {niche}
Competitors : {', '.join(competitors)}
Date        : {today}

Complete ALL six tasks below. Use the provided tools plus web_search and web_fetch to find real, current URLs.

──────────────────────────────────────────────────────────────
TASK 1 – BRAND MENTION AUDIT
Search for unlinked "{brand_name}" mentions across the web.
Query examples:
  "{brand_name}" -site:{your_domain}
  "Alfaa Panels" cold room panels review
For each unlinked mention found: use categorize_brand_mention and generate a 'mention' outreach email.

──────────────────────────────────────────────────────────────
TASK 2 – COMPETITOR BACKLINK GAPS
For each competitor, search:
  link:[competitor-domain] OR "[competitor-domain] sandwich panels"
Find pages linking to competitors but NOT to {your_domain}.
For each gap: use identify_link_gap_opportunity and score the prospect with score_link_prospect.

──────────────────────────────────────────────────────────────
TASK 3 – DIRECTORY & TRADE PORTAL SUBMISSIONS
Call find_directory_submission_targets("sandwich panel manufacturer PUF PIR cold room India", "India").
Then web_search for any new India construction/manufacturing directories added in 2025-2026.
List the top 10 highest-value directories NOT yet submitted to (search {your_domain} on each to verify).
Provide ready-to-use submission details for each.

──────────────────────────────────────────────────────────────
TASK 4 – GUEST POST & RESOURCE PAGE OPPORTUNITIES
Search for:
  "write for us" construction panels insulation India
  "guest post" building materials cold storage India
  "resources" sandwich panels industrial construction
  intitle:"resources" cold room clean room pharmaceutical India
Score each prospect with score_link_prospect.
Generate a 'guest_post' or 'resource' outreach email for the top 3 HIGH PRIORITY prospects.

──────────────────────────────────────────────────────────────
TASK 5 – Q&A / FORUM BACKLINKS
Search for unanswered or thin-answer questions on:
  - Quora: sandwich panels PUF PIR India cold room construction
  - Reddit (r/construction, r/HVAC, r/IndiaBusinessHub): insulated panels manufacturer
  - IndiaMart forums, TradeIndia forums
List 5 specific threads/questions where a detailed expert answer (with a link to alfaapanels.com) would be valuable.
Draft a concise, helpful answer for the top question that naturally links to the most relevant page on {your_domain}.

──────────────────────────────────────────────────────────────
TASK 6 – DAILY ACTION PLAN & REPORT
Compile findings into a prioritised action list for today ({today}).
Format:
  🔴 DO TODAY (high-impact, quick wins)
  🟡 THIS WEEK (moderate effort)
  🟢 ONGOING (evergreen link building)

Include:
  - Exact URLs to contact / submit to
  - Ready-to-send outreach emails
  - Any backlink quality issues found (use analyze_backlink_quality if needed)
  - Estimated SEO value for each action

End with a one-paragraph executive summary suitable for a daily email update."""
        }],
    )

    full_report: list[str] = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = os.path.join(report_dir, f"backlink_report_{today}.md")
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report – {brand_name}\n")
        f.write(f"**Date:** {today}  |  **Domain:** {your_domain}\n\n---\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved → {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent()
