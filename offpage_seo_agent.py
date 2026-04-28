import os
import anthropic
from anthropic import beta_tool
from datetime import date

client = anthropic.Anthropic()

TARGET_DOMAIN = os.getenv("TARGET_DOMAIN", "alfaapanels.com")
BRAND_NAME = os.getenv("BRAND_NAME", "Alfa Panels")
NICHE = os.getenv("NICHE", "aluminum composite panels and building materials")
COMPETITORS = os.getenv("COMPETITORS", "alucobond.com,reynobond.com,alpolic.com").split(",")


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link"]
    if anchor_text.lower() in generic_anchors:
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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "professional"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to request a link"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


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
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "supplier", "manufacturer"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/supplier page (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Prospect Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(f"  - {r}" for r in reasons)


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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link found on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"I have a comprehensive resource at {your_content_url} covering the same topic that could serve as a great replacement for your readers.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\n[Your Name]\n{your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'm a regular reader of {prospect_site} — your coverage of {their_page_topic} is excellent.\n\n"
            f"I represent {your_site} and would love to contribute a guest post to your audience. I can write a detailed, original piece on {their_page_topic} with practical insights your readers would find valuable.\n\n"
            f"Would you be open to a collaboration?\n\nBest regards,\n[Your Name]\n{your_site}"
        ),
        "resource": (
            f"Subject: Resource addition for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your {their_page_topic} resource page on {prospect_site} is very helpful!\n\n"
            f"I thought you might want to add {your_content_url} to your list — it covers {their_page_topic} in depth and has helped many professionals in the industry.\n\n"
            f"Happy to share more details if helpful.\n\nBest regards,\n[Your Name]\n{your_site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to turning that mention into a direct link to {your_content_url}? It would make it easier for your readers to find us.\n\n"
            f"Thanks so much!\n[Your Name]\n{your_site}"
        ),
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
    return (
        f"LINK GAP OPPORTUNITY\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action steps:\n"
        f"1. Identify what content on {competitor_domain} earned this link\n"
        f"2. Create superior content on {your_domain} covering the same topic\n"
        f"3. Reach out to the linking page owner with your better resource\n"
        f"4. Search query: site:{linking_page_topic.replace(' ', '+')} {competitor_domain}"
    )


@beta_tool
def find_directory_opportunity(niche: str, location: str = "global") -> str:
    """Find niche-relevant directory and listing opportunities.

    Args:
        niche: Your website's niche/topic.
        location: Target location ('global', 'local', or specific city/country).
    """
    queries = [
        f'"{niche}" directory',
        f'"{niche}" supplier list',
        f'"{niche}" manufacturer directory site:.org',
        f'"{niche}" industry association members',
        f'"best {niche} companies"',
        f'"{niche}" resource list site:.edu',
    ]
    if location != "global":
        queries.append(f'"{location}" "{niche}" directory')
        queries.append(f'"{niche}" suppliers {location}')

    return (
        f"DIRECTORY OPPORTUNITIES FOR: {niche.upper()}\n"
        f"Location: {location}\n\n"
        f"Search queries to find directories:\n" +
        "\n".join(f"  {i+1}. {q}" for i, q in enumerate(queries)) +
        "\n\nEvaluation criteria for each directory:\n"
        "  - Is it indexed by Google? (site:directory-url.com)\n"
        "  - Does it have real member/company listings?\n"
        "  - Is the listing free or paid?\n"
        "  - Is the domain authority > 20?\n"
        "  - Is it niche-relevant?\n\n"
        "Submit with consistent NAP (Name, Address, Phone) across all directories."
    )


@beta_tool
def create_daily_action_plan(opportunities_summary: str, today: str, domain: str) -> str:
    """Create a prioritized daily action plan for backlink building.

    Args:
        opportunities_summary: Summary of all discovered opportunities.
        today: Today's date in YYYY-MM-DD format.
        domain: Your target domain.
    """
    return (
        f"# DAILY BACKLINK ACTION PLAN\n"
        f"**Date:** {today}\n"
        f"**Domain:** {domain}\n\n"
        f"## Discovered Opportunities\n{opportunities_summary}\n\n"
        f"## Today's Actions (Prioritized)\n\n"
        f"### Quick Wins (30 minutes)\n"
        f"- Submit to 2-3 free directories identified above\n"
        f"- Respond to any unlinked brand mentions found\n"
        f"- Check and update any previously submitted directories\n\n"
        f"### Outreach (1 hour)\n"
        f"- Send personalized emails to top 3 prospects identified\n"
        f"- Follow up on previous outreach sent 7+ days ago\n"
        f"- Engage with prospect content on social media before emailing\n\n"
        f"### Content (This Week)\n"
        f"- Create content targeting identified link gap topics\n"
        f"- Update existing pages to be more linkable (add statistics, visuals)\n"
        f"- Publish one piece of link-worthy content\n\n"
        f"### Monitoring (Daily)\n"
        f"- Track new brand mentions\n"
        f"- Check competitors for new backlinks\n"
        f"- Monitor new directories and resource pages in niche\n\n"
        f"## Follow-up Schedule\n"
        f"- Log all outreach in CRM with follow-up date (+7 days)\n"
        f"- Record submitted directories with submission date\n"
        f"- Review results after 30 days and adjust strategy"
    )


def run_daily_backlink_agent(
    your_domain: str = TARGET_DOMAIN,
    brand_name: str = BRAND_NAME,
    niche: str = NICHE,
    competitors: list = None,
):
    if competitors is None:
        competitors = COMPETITORS

    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Daily Backlink Building — {your_domain}")
    print(f"Date: {today}")
    print("=" * 60)

    system_prompt = (
        f"You are an expert off-page SEO strategist and link builder for {your_domain} ({brand_name}).\n"
        f"Niche: {niche}\n"
        f"Your mission: find and document real, actionable backlink opportunities every single day.\n"
        f"Focus on quality over quantity. Every opportunity must include a specific URL or contact point.\n"
        f"Use web_search and web_fetch to find real pages, then score and prioritize them.\n"
        f"Today's date: {today}"
    )

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        system=[{
            "type": "text",
            "text": system_prompt,
            "cache_control": {"type": "ephemeral"},
        }],
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            find_directory_opportunity,
            create_daily_action_plan,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": (
                f"Build relevant backlinks for {your_domain} today ({today}).\n\n"
                f"Brand: {brand_name}\n"
                f"Niche: {niche}\n"
                f"Competitors: {', '.join(competitors)}\n\n"
                f"Execute all six tasks:\n\n"
                f"TASK 1 — Brand Mention Audit\n"
                f'Search: "{brand_name}" -site:{your_domain}\n'
                f'Also search: "{brand_name}" panels review\n'
                f"Use categorize_brand_mention for each result found.\n\n"
                f"TASK 2 — Competitor Backlink Research\n"
                f"For each competitor, search: link building sites that link to {competitors[0]}\n"
                f'Search: "{competitors[0]}" mentioned in resources\n'
                f"Use identify_link_gap_opportunity for 3-5 opportunities found.\n\n"
                f"TASK 3 — Link Building Prospects\n"
                f'Search: "{niche} resources" useful links\n'
                f'Search: "{niche} write for us" guest post\n'
                f'Search: "{niche} suppliers directory"\n'
                f"Use score_link_prospect for each candidate found.\n\n"
                f"TASK 4 — Outreach Templates\n"
                f"Generate personalized outreach for the top 3 prospects using generate_outreach_template.\n\n"
                f"TASK 5 — Directory Opportunities\n"
                f"Use find_directory_opportunity for '{niche}'.\n"
                f"Then search for the top 3 directories found and fetch their submission pages.\n\n"
                f"TASK 6 — Daily Action Plan\n"
                f"Use create_daily_action_plan to compile all findings into a prioritized plan.\n\n"
                f"Every opportunity must include a real, specific URL."
            ),
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = f"{report_dir}/backlinks_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {your_domain}\n\n")
        f.write(f"**Date:** {today}  \n")
        f.write(f"**Niche:** {niche}  \n")
        f.write(f"**Competitors monitored:** {', '.join(competitors)}\n\n")
        f.write("---\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_path}")
    return report_path


if __name__ == "__main__":
    run_daily_backlink_agent()
