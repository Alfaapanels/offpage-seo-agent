import anthropic
from anthropic import beta_tool
import sqlite3
import logging
import sys
from datetime import datetime, date
from apscheduler.schedulers.blocking import BlockingScheduler

DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "alfa panels solar panels electrical control panels energy solutions home improvement"
COMPETITORS = [
    "enphase.com",
    "solaredge.com",
    "canadiansolar.com",
    "sunpower.com",
]

DB_PATH = "backlinks.db"
LOG_FILE = "seo_agent.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

client = anthropic.Anthropic()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS backlinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL,
            source_url TEXT,
            anchor_text TEXT,
            link_type TEXT,
            status TEXT DEFAULT 'opportunity',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL,
            prospect_site TEXT,
            link_type TEXT,
            email_template TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    toxic_signals = ["spam", "casino", "viagra", "adult", "pharma"]
    if any(word in backlink_url.lower() for word in toxic_signals):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority_signals):
        quality_signals.append("High-authority TLD - strong link value")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and determine sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "reliable", "quality"]
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
    action = "Monitor" if has_link else "Reach out to request a link to alfaapanels.com"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
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
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "review", "comparison", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority TLD (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(f"  - {r}" for r in reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email for link building.

    Args:
        prospect_name: Name of the website owner or editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your {their_page_topic} page on {prospect_site} and noticed a broken link.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would be a perfect replacement "
            f"and give your readers the information they need.\n\n"
            f"Would you consider swapping the broken link for mine?\n\nBest regards,\n[Your Name] | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Collaboration for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s coverage of {their_page_topic} and think your audience "
            f"would benefit from a piece I can write for you.\n\n"
            f"I'm the team behind {your_site}, a trusted resource in the panels and solar energy space. "
            f"I'd love to contribute a high-quality, original article.\n\n"
            f"Would you be open to a guest post collaboration?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "resource": (
            f"Subject: Great addition for your {their_page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your {their_page_topic} resource page on {prospect_site} is one of the best I've found!\n\n"
            f"I recently published {your_content_url} which covers [specific angle]. "
            f"I think it would make a valuable addition for your readers.\n\n"
            f"Would you take a look?\n\nBest,\n[Your Name] | {your_site}"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I came across your article on {their_page_topic} and noticed you mentioned {your_site} — thank you!\n\n"
            f"Would you consider linking directly to {your_content_url}? "
            f"It would help your readers find the resource more easily.\n\nThanks,\n[Your Name] | {your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify if a competitor backlink represents an opportunity for alfaapanels.com.

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
        f"Action plan:\n"
        f"1. Study what content on {competitor_domain} earned this backlink\n"
        f"2. Create a better or more comprehensive version of that content for {your_domain}\n"
        f"3. Reach out to the linking page with your improved resource as an alternative"
    )


@beta_tool
def log_backlink_opportunity(
    source_url: str,
    link_type: str,
    anchor_text: str,
    notes: str,
    status: str = "opportunity",
) -> str:
    """Save a discovered backlink opportunity or acquired backlink to the tracking database.

    Args:
        source_url: The URL where the backlink will be or was placed.
        link_type: Type: 'directory', 'forum', 'qa', 'guest_post', 'resource', 'broken_link', 'mention', 'social'.
        anchor_text: The anchor text used or suggested for the link.
        notes: Context, strategy notes, or action taken for this opportunity.
        status: Current status: 'opportunity', 'outreach_sent', 'acquired', 'rejected'.
    """
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO backlinks (run_date, source_url, anchor_text, link_type, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (today, source_url, anchor_text, link_type, status, notes),
    )
    conn.commit()
    row_id = c.lastrowid
    conn.close()
    return f"Logged #{row_id}: [{link_type}] {source_url} | anchor: '{anchor_text}' | status: {status}"


@beta_tool
def log_outreach(prospect_site: str, link_type: str, email_template: str) -> str:
    """Save a generated outreach email to the outreach tracking database.

    Args:
        prospect_site: The website being contacted for a backlink.
        link_type: Type of link being requested.
        email_template: The full outreach email text ready to send.
    """
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO outreach (run_date, prospect_site, link_type, email_template) VALUES (?, ?, ?, ?)",
        (today, prospect_site, link_type, email_template),
    )
    conn.commit()
    row_id = c.lastrowid
    conn.close()
    return f"Saved outreach email #{row_id} for {prospect_site} ({link_type})"


@beta_tool
def get_todays_progress(domain: str = DOMAIN) -> str:
    """Get a summary of backlink building work logged today.

    Args:
        domain: The target domain being tracked (default: alfaapanels.com).
    """
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT link_type, status, COUNT(*) FROM backlinks WHERE run_date = ? GROUP BY link_type, status",
        (today,),
    )
    rows = c.fetchall()
    c.execute("SELECT COUNT(*) FROM outreach WHERE run_date = ?", (today,))
    outreach_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM backlinks", ())
    total_all_time = c.fetchone()[0]
    conn.close()

    if not rows:
        return f"No backlinks logged yet today ({today}).\nAll-time total in database: {total_all_time} entries."

    lines = [f"Today's progress ({today}) for {domain}:"]
    for link_type, status, count in rows:
        lines.append(f"  {link_type} [{status}]: {count}")
    lines.append(f"Outreach emails drafted today: {outreach_count}")
    lines.append(f"All-time total logged: {total_all_time}")
    return "\n".join(lines)


DAILY_STRATEGIES = {
    0: (
        "MONDAY - Brand Mention Audit\n"
        "Search for 'Alfa Panels' and 'alfaapanels.com' across blogs, forums, review sites, and news. "
        "Identify unlinked mentions and convert them to backlink opportunities. "
        "Also search for unlinked mentions of panel-related products that alfaapanels.com could answer. "
        "Use categorize_brand_mention for each result."
    ),
    1: (
        "TUESDAY - Competitor Backlink Gap Analysis\n"
        "Research backlinks pointing to enphase.com, solaredge.com, canadiansolar.com, and sunpower.com. "
        "Identify sites in the solar, electrical, and home energy space that link to competitors but not to alfaapanels.com. "
        "Use identify_link_gap_opportunity for each gap found and log all opportunities."
    ),
    2: (
        "WEDNESDAY - Resource Page Link Building\n"
        "Find resource pages, 'best solar panels' lists, 'recommended electrical panel suppliers' roundups, "
        "and industry directories in the solar energy, home improvement, and electrical niches. "
        "Score each prospect with score_link_prospect and draft outreach for HIGH and MEDIUM priority pages."
    ),
    3: (
        "THURSDAY - Broken Link Building\n"
        "Search for pages in the solar panels, electrical panels, home energy, and renewable energy niches "
        "that have broken outbound links. Find dead resources and offer alfaapanels.com content as a replacement. "
        "Fetch pages to verify broken links and generate broken_link outreach templates."
    ),
    4: (
        "FRIDAY - Guest Post Prospecting\n"
        "Find blogs, magazines, and publications in solar energy, home improvement, electrical, sustainability, "
        "and green technology niches that accept guest posts. Look for 'write for us' pages. "
        "Score each site and generate personalized guest_post outreach pitches for the top prospects."
    ),
    5: (
        "SATURDAY - Q&A and Forum Authority Building\n"
        "Find high-traffic questions on Quora, Reddit (r/solar, r/homeimprovement, r/electricians, r/DIY), "
        "and niche forums about solar panels, electrical panels, and home energy. "
        "Identify threads where linking to alfaapanels.com would genuinely help. Log these as 'qa' opportunities."
    ),
    6: (
        "SUNDAY - Directory and Citation Building\n"
        "Find business directories, local citation sites, solar energy associations, electrical contractor "
        "directories, and green energy registries where alfaapanels.com is not yet listed. "
        "Log each directory as an opportunity with submission instructions in the notes."
    ),
}


def run_daily_backlink_agent():
    today = date.today()
    day_name = today.strftime("%A")
    strategy = DAILY_STRATEGIES[today.weekday()]

    logger.info(f"=== Daily backlink agent starting: {today} ({day_name}) ===")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_backlink_opportunity,
            log_outreach,
            get_todays_progress,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist building high-quality, relevant backlinks for alfaapanels.com every day.

**Target website:** {DOMAIN}
**Brand name:** {BRAND_NAME}
**Niche:** {NICHE}
**Main competitors:** {', '.join(COMPETITORS)}
**Today:** {today.isoformat()} ({day_name})

---

**TODAY'S FOCUS:**
{strategy}

---

**EXECUTION INSTRUCTIONS:**
1. Use `web_search` to find real, specific backlink opportunities for today's focus area
2. Use `web_fetch` to examine promising pages and verify details
3. Use `score_link_prospect` on every prospect — only pursue MEDIUM (40+) and HIGH (70+) priority
4. Use `log_backlink_opportunity` to save EVERY opportunity found, even LOW priority ones
5. For HIGH and MEDIUM prospects, use `generate_outreach_template` to create a personalized email
6. Use `log_outreach` to save every outreach email you draft
7. For brand mentions, use `categorize_brand_mention` to classify them
8. For competitor links, use `identify_link_gap_opportunity` to document the gap
9. Call `get_todays_progress` at the end to summarize the session

**QUALITY GUIDELINES:**
- Only pursue backlinks from sites relevant to: solar energy, electrical panels, home improvement, energy efficiency, construction, sustainability, or green technology
- Target real sites with actual content — no link farms or PBNs
- Vary anchor text naturally: use "Alfa Panels", "alfaapanels.com", "solar panels supplier", "electrical panel solutions", "panel installation", and contextual phrases
- Log a minimum of 10 opportunities per session
- Draft outreach for at least 5 MEDIUM or HIGH priority prospects
- Prioritize .edu, .gov, .org, and high-DA industry sites

**START NOW.** Work systematically through today's focus. Search broadly, evaluate rigorously, and log everything.""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                logger.info(block.text[:300] + "..." if len(block.text) > 300 else block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{today.isoformat()}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Building Report — {DOMAIN}\n\n")
        f.write(f"**Date:** {today.isoformat()} ({day_name})\n\n")
        f.write(f"**Focus:**\n{strategy}\n\n")
        f.write("---\n\n")
        f.write("\n\n".join(full_report))

    logger.info(f"Report saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    init_db()

    if "--schedule" in sys.argv:
        run_daily_backlink_agent()
        scheduler = BlockingScheduler()
        scheduler.add_job(run_daily_backlink_agent, "cron", hour=9, minute=0)
        logger.info("Scheduler active — will run daily at 09:00 AM")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")
    else:
        run_daily_backlink_agent()
