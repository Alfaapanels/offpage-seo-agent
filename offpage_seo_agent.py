import json
import os
from datetime import date
import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

DOMAIN = "alfaapanels.com"
BRAND = "AlfaaPanels"
NICHE = "web hosting reseller panel software"
COMPETITORS = ["whmcs.com", "blesta.com", "clientexec.com", "hostbillapp.com"]
LOG_FILE = "backlink_log.json"


def _load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {}


def _save_log(data: dict):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic = ["click here", "website", "here", "link"]
    if anchor_text.lower() in generic:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(w in backlink_url.lower() for w in ["spam", "casino", "viagra"]):
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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
    pos = sum(1 for w in positive_words if w in mention_text.lower())
    neg = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
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
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "hosting", "panel"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide page - high link value (+30)")
    authority = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority):
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
    link_type: str,
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
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\nI have a comprehensive guide at {your_content_url} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\n[Your Name] from {your_site}",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post on web hosting panels and reseller solutions. I write for {your_site}.\n\nWould you be open to a collaboration?\n\nBest,\n[Your Name]",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is great! I created {your_content_url} which covers web hosting reseller panels and might help your readers.\n\nWould you take a look?\n\nBest,\n[Your Name] from {your_site}",
        "mention": f"Subject: You mentioned {your_site} - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning {your_site} in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url}?\n\nThanks,\n[Your Name]",
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
        f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\nActions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource"
    )


@beta_tool
def find_daily_backlink_targets(niche: str, domain: str, strategy: str) -> str:
    """Return a list of site types and search queries to find backlink targets for today's strategy.

    Args:
        niche: Your website's niche (e.g. 'web hosting reseller panel').
        domain: Your domain name.
        strategy: Today's strategy: 'directories', 'forums', 'qa_sites', 'resource_pages', 'guest_posts', 'social_bookmarks'.
    """
    strategies = {
        "directories": {
            "description": "Business and niche web directories",
            "targets": [
                "dmoz-style directories in hosting/software niche",
                "Capterra, G2, GetApp software directories",
                "AlternativeTo.net listing",
                "SoftwareSuggest directory",
                "SourceForge / similar open-source directories",
                "ProductHunt launch",
            ],
            "search_queries": [
                f"web hosting panel software directory submit",
                f"reseller hosting software listing site",
                f'"add your site" web hosting control panel directory',
            ],
        },
        "forums": {
            "description": "Niche forums and community boards",
            "targets": [
                "WebHostingTalk.com forum threads",
                "WHT (Web Hosting Talk) product reviews",
                "HostingDiscussion.com",
                "NamePros hosting section",
                "Reddit r/webhosting, r/selfhosted, r/sysadmin",
            ],
            "search_queries": [
                f'"web hosting" forum "control panel" recommendations',
                f"site:webhostingtalk.com reseller panel software",
                f"site:reddit.com web hosting reseller panel recommendations",
            ],
        },
        "qa_sites": {
            "description": "Q&A and help platforms",
            "targets": [
                "Quora questions about web hosting panels",
                "Stack Overflow / Server Fault hosting questions",
                "Reddit AMAs and Q&A threads",
                "Yahoo Answers alternatives",
                "Spiceworks community",
            ],
            "search_queries": [
                f'site:quora.com "best web hosting panel" OR "reseller hosting software"',
                f'site:reddit.com "what hosting panel" OR "recommend control panel"',
                f"web hosting reseller panel comparison question site:stackexchange.com",
            ],
        },
        "resource_pages": {
            "description": "Curated resource and tools pages",
            "targets": [
                "Hosting comparison and review sites",
                '"best web hosting panel" roundup articles',
                "Web developer tools and resources pages",
                "Sysadmin tool lists",
                "SaaS resource roundups",
            ],
            "search_queries": [
                f'"web hosting panel" "recommended tools" OR "resources"',
                f'"best hosting control panel" inurl:resources OR inurl:tools',
                f'"reseller hosting software" "top" OR "best" -site:{domain}',
            ],
        },
        "guest_posts": {
            "description": "Guest posting on relevant blogs",
            "targets": [
                "Web hosting blogs accepting guest posts",
                "SaaS and B2B tech blogs",
                "DevOps and sysadmin blogs",
                "Startup and entrepreneur blogs covering hosting",
                "Domain and hosting review sites",
            ],
            "search_queries": [
                f'"web hosting" "write for us" OR "guest post"',
                f'"hosting software" "contribute" OR "submit article"',
                f'"sysadmin" OR "devops" blog "guest post guidelines"',
            ],
        },
        "social_bookmarks": {
            "description": "Social bookmarking and content aggregators",
            "targets": [
                "Reddit relevant subreddits",
                "Hacker News Show HN",
                "Mix.com",
                "Digg",
                "Flipboard",
                "LinkedIn articles and posts",
                "Medium publications about hosting/SaaS",
            ],
            "search_queries": [
                f"social bookmarking sites hosting software niche",
                f"Medium publication web hosting technology submit",
            ],
        },
    }
    s = strategies.get(strategy, strategies["directories"])
    targets_str = "\n".join(f"  - {t}" for t in s["targets"])
    queries_str = "\n".join(f"  - {q}" for q in s["search_queries"])
    return (
        f"DAILY BACKLINK STRATEGY: {strategy.upper()}\n"
        f"Description: {s['description']}\n\n"
        f"Target site types:\n{targets_str}\n\n"
        f"Search queries to find prospects:\n{queries_str}\n\n"
        f"Action: Use web_search with the queries above, score each result with score_link_prospect, "
        f"then generate outreach templates for HIGH PRIORITY prospects."
    )


@beta_tool
def log_completed_backlink(url: str, strategy: str, action_taken: str, status: str) -> str:
    """Log a completed backlink action to avoid duplicates in future runs.

    Args:
        url: The URL where the backlink was placed or outreach was sent.
        strategy: The strategy used (e.g. 'directories', 'forums').
        action_taken: Description of what was done.
        status: 'submitted', 'outreach_sent', 'live', 'pending_review'.
    """
    log = _load_log()
    today = str(date.today())
    if today not in log:
        log[today] = []
    entry = {"url": url, "strategy": strategy, "action": action_taken, "status": status}
    if not any(e["url"] == url for entries in log.values() for e in entries):
        log[today].append(entry)
        _save_log(log)
        return f"Logged: {url} [{status}] - will not duplicate in future runs."
    return f"Already logged: {url} - skipping to avoid duplicate submission."


def _get_todays_strategy() -> str:
    strategies = ["directories", "forums", "qa_sites", "resource_pages", "guest_posts", "social_bookmarks"]
    day_index = date.today().toordinal() % len(strategies)
    return strategies[day_index]


def _get_already_done() -> list[str]:
    log = _load_log()
    done = []
    for entries in log.values():
        done.extend(e["url"] for e in entries)
    return done


def run_offpage_seo_agent(
    your_domain: str = DOMAIN,
    brand_name: str = BRAND,
    niche: str = NICHE,
    competitors: list = None,
):
    if competitors is None:
        competitors = COMPETITORS

    today = str(date.today())
    strategy = _get_todays_strategy()
    already_done = _get_already_done()
    already_done_str = "\n".join(f"  - {u}" for u in already_done[:30]) if already_done else "  (none yet)"

    print(f"\nDaily Backlink Builder for: {your_domain}")
    print(f"Date: {today} | Strategy: {strategy.upper()}")
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
            find_daily_backlink_targets,
            log_completed_backlink,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO and link-building specialist.

TODAY'S MISSION: Build relevant, high-quality backlinks for {your_domain} ({brand_name}).
Date: {today}
Today's Strategy Focus: {strategy.upper()}
Niche: {niche}
Competitors: {', '.join(competitors)}

URLs already targeted (DO NOT duplicate these):
{already_done_str}

EXECUTE THESE TASKS IN ORDER:

TASK 1 - Find Today's Targets
Use find_daily_backlink_targets with strategy="{strategy}" for domain "{your_domain}" and niche "{niche}".
Then use the returned search queries with web_search to find 5-10 specific sites/pages to target today.

TASK 2 - Score Each Prospect
For every prospect found, use score_link_prospect to evaluate relevance and priority.
Only proceed with MEDIUM or HIGH PRIORITY prospects. Skip LOW priority.

TASK 3 - Research & Validate Prospects
Use web_fetch on the top 3-5 HIGH/MEDIUM priority prospects to confirm:
- They accept submissions, comments, or links
- The content is relevant to {niche}
- They have real traffic/authority

TASK 4 - Generate Outreach / Submission Content
For each validated prospect, use generate_outreach_template to create a personalized email or submission.
Tailor the message specifically to {brand_name} and {niche}.

TASK 5 - Brand Mention Opportunities
Search for "{brand_name}" -site:{your_domain} to find unlinked mentions.
Use categorize_brand_mention on any mentions found.

TASK 6 - Competitor Link Gap
Pick 2 competitors from [{', '.join(competitors)}].
Search: link:competitor.com hosting panel (or use Ahrefs/Moz style search queries).
Use identify_link_gap_opportunity for the best opportunities found.

TASK 7 - Log All Actions
For every site you've identified and action taken, use log_completed_backlink to record it.

TASK 8 - Daily Summary Report
Produce a clear markdown report with:
- Sites targeted today and why
- Outreach emails ready to send
- Link gap opportunities found
- Unlinked brand mentions to follow up
- Recommended actions for tomorrow
""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Report: {your_domain}\n")
        f.write(f"**Date:** {today} | **Strategy:** {strategy.upper()}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved: {report_filename}")


if __name__ == "__main__":
    run_offpage_seo_agent()
