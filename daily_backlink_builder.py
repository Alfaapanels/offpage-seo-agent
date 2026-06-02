import anthropic
from anthropic import beta_tool
import json
import os
import sys
import time
from datetime import datetime, date

try:
    import schedule
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False

client = anthropic.Anthropic()

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "building panels facade panels construction materials sandwich panels wall cladding",
    "competitors": [
        "rockwool.com",
        "kingspaninsulation.com",
        "etalbondusa.com",
    ],
    "target_keywords": [
        "building panels",
        "facade panels",
        "sandwich panels",
        "wall cladding panels",
        "construction panels",
        "insulated panels",
        "composite panels",
    ],
    "description": (
        "Alfa Panels manufactures and supplies high-quality building panels, "
        "facade panels, sandwich panels, and wall cladding solutions for "
        "residential, commercial, and industrial construction projects."
    ),
}

DAILY_STRATEGIES = {
    0: ("directory_submission",   "Directory Submissions"),
    1: ("forum_community",        "Forum & Community Participation"),
    2: ("guest_post_outreach",    "Guest Post Outreach"),
    3: ("resource_page_building", "Resource Page Link Building"),
    4: ("broken_link_building",   "Broken Link Building"),
    5: ("social_bookmarking",     "Social Bookmarking & Profiles"),
    6: ("content_haro",           "Content Links & HARO"),
}

BACKLINK_LOG = "backlink_log.json"


def load_log() -> dict:
    if os.path.exists(BACKLINK_LOG):
        with open(BACKLINK_LOG) as f:
            return json.load(f)
    return {"links": [], "stats": {"total": 0, "by_type": {}, "by_date": {}}}


def save_log(log: dict):
    with open(BACKLINK_LOG, "w") as f:
        json.dump(log, f, indent=2, default=str)


# ── tools ────────────────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    signals = []
    generic = ["click here", "website", "here", "link", "read more"]
    if anchor_text.lower() in generic:
        signals.append("Warning: Generic anchor text – low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor text: '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "payday loan", "adult"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC – disavow recommended")
    else:
        signals.append("Domain appears clean")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and determine sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    pos = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "trusted"]
    neg = ["bad", "worst", "avoid", "scam", "terrible", "poor", "expensive"]
    pos_score = sum(1 for w in pos if w in mention_text.lower())
    neg_score = sum(1 for w in neg if w in mention_text.lower())
    sentiment = "Positive" if pos_score > neg_score else ("Negative" if neg_score > pos_score else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to add your link"
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
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low niche relevance (+0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "directory"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/directory page (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High-authority TLD (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH" if score >= 70 else ("MEDIUM" if score >= 40 else "LOW")
    return f"Score: {score}/100 [{priority}]\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str,
    your_domain: str,
    linking_page_topic: str,
) -> str:
    """Identify a competitor backlink as an opportunity for your site.

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
        f"1. Find what specific content on {competitor_domain} earned this link\n"
        f"2. Create superior content covering the same topic for {your_domain}\n"
        f"3. Contact the linking page owner with your better resource\n"
        f"4. Track outreach in backlink log"
    )


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
            f"I came across your page on {their_page_topic} and noticed a broken link "
            f"that might be frustrating your readers.\n\n"
            f"I have a comprehensive guide at {your_content_url} that would be a perfect replacement.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\n[Your Name] | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Proposal for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site}'s coverage of {their_page_topic} and really enjoy your content.\n\n"
            f"I'd love to contribute a guest post from my experience at {your_site}. "
            f"I can offer a unique angle that would add real value to your readers.\n\n"
            f"Would you be open to discussing a collaboration?\n\nBest regards,\n[Your Name] | {your_site}"
        ),
        "resource": (
            f"Subject: Useful resource for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is excellent – exactly what construction professionals need.\n\n"
            f"I created {your_content_url} which might be a valuable addition for your readers.\n\n"
            f"Would you take a look?\n\nBest regards,\n[Your Name] | {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} – thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers "
            f"can find the resource easily?\n\nThanks,\n[Your Name] | {your_site}"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def generate_directory_submission(
    directory_name: str,
    directory_url: str,
    category: str,
) -> str:
    """Generate optimized submission content for a business directory.

    Args:
        directory_name: Name of the directory.
        directory_url: Submission URL of the directory.
        category: Best category for the submission.
    """
    cfg = SITE_CONFIG
    return (
        f"DIRECTORY SUBMISSION – {directory_name}\n"
        f"Submit at: {directory_url}\n"
        f"Category: {category}\n\n"
        f"Business Name: {cfg['brand_name']}\n"
        f"Website: https://{cfg['domain']}\n"
        f"Short Description (160 chars):\n"
        f"  Premium building panels, facade panels & sandwich panels for residential, "
        f"commercial and industrial construction. Quality manufacturing.\n\n"
        f"Long Description:\n"
        f"  {cfg['description']}\n\n"
        f"Keywords: {', '.join(cfg['target_keywords'])}"
    )


@beta_tool
def generate_forum_response(
    forum_url: str,
    thread_topic: str,
    thread_question: str,
) -> str:
    """Draft a helpful forum reply with a natural backlink opportunity.

    Args:
        forum_url: URL of the forum thread.
        thread_topic: Topic of the thread.
        thread_question: The specific question being asked.
    """
    cfg = SITE_CONFIG
    return (
        f"FORUM RESPONSE DRAFT\n"
        f"Thread: {forum_url}\n"
        f"Topic: {thread_topic}\n\n"
        f"---\n"
        f"Great question about {thread_topic}!\n\n"
        f"[Write 2–3 paragraphs of genuinely useful advice addressing: {thread_question}]\n\n"
        f"For detailed technical specs and product comparisons on building panels and "
        f"facade materials, {cfg['domain']} has some solid resources worth checking out.\n\n"
        f"Hope that helps!\n"
        f"---\n\n"
        f"Note: Lead with value. The link should be natural, not promotional."
    )


@beta_tool
def generate_guest_post_pitch(
    site_name: str,
    site_url: str,
    site_topic: str,
    editor_name: str,
) -> str:
    """Generate a guest post pitch email for a target publication.

    Args:
        site_name: Name of the target site.
        site_url: URL of the site.
        site_topic: Main topic/niche of the site.
        editor_name: Editor or contact person name (use 'Editor' if unknown).
    """
    cfg = SITE_CONFIG
    pitch_topics = [
        "5 Key Factors to Choose the Right Building Panels for Commercial Projects",
        "How Modern Facade Panels Are Transforming Sustainable Architecture",
        "The Complete Guide to Sandwich Panel Installation: Best Practices",
        "Comparing Building Panel Materials: Which Is Right for Your Project?",
        "Energy Efficiency in Construction: How Insulated Panels Reduce Costs",
    ]
    topic = pitch_topics[hash(site_url) % len(pitch_topics)]
    return (
        f"GUEST POST PITCH\n"
        f"To: {editor_name}, {site_name} ({site_url})\n"
        f"Subject: Guest Post Proposal – \"{topic}\"\n\n"
        f"Hi {editor_name},\n\n"
        f"I love {site_name}'s coverage of {site_topic} – your audience clearly cares "
        f"about practical, expert-backed content.\n\n"
        f"I'd like to contribute: \"{topic}\"\n\n"
        f"The piece would cover:\n"
        f"• [Key point 1 relevant to {site_topic} audience]\n"
        f"• [Key point 2 with actionable takeaways]\n"
        f"• [Key point 3 with data/examples]\n\n"
        f"~1,500 words, original, not published elsewhere. "
        f"I write for {cfg['brand_name']} ({cfg['domain']}).\n\n"
        f"Would this fit your editorial calendar?\n\n"
        f"Best regards,\n[Your Name] | {cfg['brand_name']}\n{cfg['domain']}"
    )


@beta_tool
def track_backlink_opportunity(
    url: str,
    link_type: str,
    status: str,
    notes: str,
    domain_authority_estimate: int,
    niche_relevance: str,
) -> str:
    """Save a backlink opportunity or confirmed link to the daily log.

    Args:
        url: The URL where the backlink can be or was placed.
        link_type: Type: 'directory', 'forum', 'guest_post', 'resource', 'broken_link', 'social', 'haro'.
        status: Status: 'opportunity', 'submitted', 'pending', 'live'.
        notes: Action details – what to do, submission link, contact info, etc.
        domain_authority_estimate: Estimated domain authority 1–100.
        niche_relevance: Relevance to building panels niche: 'high', 'medium', 'low'.
    """
    log = load_log()
    today = str(date.today())
    entry = {
        "date": today,
        "url": url,
        "link_type": link_type,
        "status": status,
        "notes": notes,
        "da_estimate": domain_authority_estimate,
        "niche_relevance": niche_relevance,
        "tracked_at": datetime.now().isoformat(),
    }
    log["links"].append(entry)
    log["stats"]["total"] += 1
    log["stats"]["by_type"][link_type] = log["stats"]["by_type"].get(link_type, 0) + 1
    log["stats"]["by_date"][today] = log["stats"]["by_date"].get(today, 0) + 1
    save_log(log)
    return (
        f"Tracked [{status}] {url}\n"
        f"Type: {link_type} | DA: {domain_authority_estimate} | Relevance: {niche_relevance}"
    )


@beta_tool
def get_todays_progress() -> str:
    """Return today's backlink building progress and all-time totals."""
    log = load_log()
    today = str(date.today())
    today_count = log["stats"]["by_date"].get(today, 0)
    total = log["stats"]["total"]
    by_type = json.dumps(log["stats"]["by_type"], indent=2)
    return (
        f"Today ({today}): {today_count} links tracked\n"
        f"All-time total: {total}\n"
        f"Breakdown by type:\n{by_type}"
    )


# ── strategy prompts ──────────────────────────────────────────────────────────

def _strategy_prompt(strategy_key: str) -> str:
    cfg = SITE_CONFIG
    domain = cfg["domain"]
    brand = cfg["brand_name"]
    niche = cfg["niche"]
    keywords = ", ".join(cfg["target_keywords"])

    prompts = {
        "directory_submission": f"""TODAY'S TASK: Directory Submissions for {domain}

Use web_search to find high-quality directories in these categories:
1. Construction and building industry directories
2. Manufacturing company directories
3. General high-DA business directories (e.g. Manta, Hotfrog, Cylex, EZlocal)
4. Regional/country-specific business directories

For each directory found (find AT LEAST 5):
a) Use score_link_prospect to evaluate it – focus on DA and niche relevance
b) Use generate_directory_submission to create the full submission content
c) Use track_backlink_opportunity with link_type='directory' and status='submitted'

Prioritize directories with estimated DA > 30 and construction/B2B focus.
End with get_todays_progress to confirm tracking.""",

        "forum_community": f"""TODAY'S TASK: Forum & Community Participation for {domain}

Use web_search to find active discussions mentioning these topics:
- Building panels questions on forums
- Facade materials advice threads
- Construction panels comparisons on Quora, Reddit r/construction, Stack Exchange
- Architecture forums discussing cladding or insulated panels
- LinkedIn/industry groups (search for public threads)

For each thread/opportunity (find AT LEAST 5):
a) Use generate_forum_response to draft a helpful reply
b) Use track_backlink_opportunity with link_type='forum' and status='opportunity'
c) Include the exact thread URL and your drafted reply in notes

Focus on threads where {brand}'s expertise genuinely adds value.
End with get_todays_progress.""",

        "guest_post_outreach": f"""TODAY'S TASK: Guest Post Outreach for {domain}

Use web_search with queries like:
- "construction blog" "write for us"
- "architecture write for us" OR "submit guest post"
- "building materials blog" "contribute"
- "contractor blog" "guest author"
- "green building" "submit article"

For each site found (find AT LEAST 5 with DA > 20):
a) Use score_link_prospect to evaluate relevance
b) Use generate_guest_post_pitch to create the full pitch email
c) Use track_backlink_opportunity with link_type='guest_post' and status='opportunity'

Include the editor contact email in notes if findable via web_search.
End with get_todays_progress.""",

        "resource_page_building": f"""TODAY'S TASK: Resource Page Link Building for {domain}

Use web_search to find resource/links pages:
- "construction resources" inurl:resources OR inurl:links
- "building materials" recommended resources site
- Architecture school resource lists
- Contractor association link pages
- Building industry "useful links" pages

For each resource page (find AT LEAST 5):
a) Use identify_link_gap_opportunity to frame the opportunity
b) Use generate_outreach_template with link_type='resource'
c) Use track_backlink_opportunity with link_type='resource', status='opportunity'

Target pages that link to similar brands or competitors.
End with get_todays_progress.""",

        "broken_link_building": f"""TODAY'S TASK: Broken Link Building for {domain}

Use web_search and web_fetch to find broken link opportunities:
1. Search for outdated resource pages in the construction niche
2. Look for pages that linked to old building materials guides
3. Check competitor link pages for dead links
4. Search: "construction resources" "broken link" OR "404"

For each broken link opportunity (find AT LEAST 5):
a) Use analyze_backlink_quality to assess the linking domain
b) Use generate_outreach_template with link_type='broken_link'
c) Use track_backlink_opportunity with link_type='broken_link', status='opportunity'

Include the broken URL and your replacement content URL in the outreach template.
End with get_todays_progress.""",

        "social_bookmarking": f"""TODAY'S TASK: Social Bookmarking & Profile Building for {domain}

Use web_search to find the best platforms for {brand} to build profiles on:
1. Industry-specific platforms: Houzz, ArchDaily, Dezeen, BuildingDesign.co.uk
2. Business profiles: Alignable, Clutch, G2, GoodFirms
3. Contractor networks: Bark.com, Thumbtack (if applicable)
4. Social bookmarks: Mix, Digg, Flipboard (construction/business category)
5. Review sites: Trustpilot, Sitejabber

For each platform (find AT LEAST 5 with DA > 40):
a) Use score_link_prospect to evaluate
b) Use track_backlink_opportunity with link_type='social', status='opportunity'
c) In notes: include exact signup/listing URL and the description to use

End with get_todays_progress.""",

        "content_haro": f"""TODAY'S TASK: Content Links & HARO Opportunities for {domain}

Use web_search to find:
1. Recent "expert roundup" posts about construction or building materials
   Search: "expert roundup" "building panels" OR "construction 2024 2025"
2. Journalists writing about construction trends (check Twitter/X, HARO categories)
3. Data/statistics pages that cite building materials sources
4. Scholarship opportunities at architecture/engineering schools
5. "Best of" lists in construction that don't include {brand}

For each opportunity (find AT LEAST 5):
a) Use categorize_brand_mention if {brand} is already mentioned
b) Use generate_outreach_template with link_type='mention' for unlinked mentions
c) Use track_backlink_opportunity with link_type='haro', status='opportunity'

Also search: site:helpareporter.com OR site:sourcebottle.com construction panels
End with get_todays_progress.""",
    }
    return prompts.get(strategy_key, prompts["directory_submission"])


# ── main runner ───────────────────────────────────────────────────────────────

def run_daily_session():
    today = date.today()
    strategy_key, strategy_label = DAILY_STRATEGIES[today.weekday()]
    cfg = SITE_CONFIG

    print(f"\n{'='*60}")
    print(f"  DAILY BACKLINK BUILDER – {cfg['domain']}")
    print(f"  Date:     {today} ({today.strftime('%A')})")
    print(f"  Strategy: {strategy_label}")
    print(f"{'='*60}\n")

    system_context = (
        f"You are an expert off-page SEO and link building specialist working for "
        f"{cfg['brand_name']} ({cfg['domain']}).\n\n"
        f"Company: {cfg['brand_name']}\n"
        f"Website: https://{cfg['domain']}\n"
        f"Industry: Building panels, facade panels, sandwich panels, construction materials\n"
        f"Target keywords: {', '.join(cfg['target_keywords'])}\n"
        f"Description: {cfg['description']}\n"
        f"Competitors: {', '.join(cfg['competitors'])}\n\n"
        f"Always use track_backlink_opportunity to log every opportunity you find. "
        f"Be specific in notes so the team can act immediately."
    )

    user_task = (
        f"{_strategy_prompt(strategy_key)}\n\n"
        f"After completing all tasks, provide a DAILY SUMMARY:\n"
        f"1. Total opportunities found and tracked\n"
        f"2. Top 3 highest-priority actions for today (with direct URLs)\n"
        f"3. Quick wins: actions completable in under 15 minutes\n"
        f"4. Estimated monthly traffic value of these links if acquired"
    )

    all_tools = [
        analyze_backlink_quality,
        categorize_brand_mention,
        score_link_prospect,
        identify_link_gap_opportunity,
        generate_outreach_template,
        generate_directory_submission,
        generate_forum_response,
        generate_guest_post_pitch,
        track_backlink_opportunity,
        get_todays_progress,
        {"type": "web_search_20260209", "name": "web_search"},
        {"type": "web_fetch_20260209", "name": "web_fetch"},
    ]

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        system=system_context,
        tools=all_tools,
        messages=[{"role": "user", "content": user_task}],
    )

    report_parts = []
    print("Agent working...\n")
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                report_parts.append(block.text)

    os.makedirs("daily_reports", exist_ok=True)
    report_path = f"daily_reports/backlinks_{today}_{strategy_key}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report – {cfg['domain']}\n\n")
        f.write(f"**Date:** {today} ({today.strftime('%A')})\n")
        f.write(f"**Strategy:** {strategy_label}\n\n---\n\n")
        f.write("\n\n".join(report_parts))

    print(f"\n{'='*60}")
    print(f"  Report saved: {report_path}")
    log = load_log()
    today_str = str(today)
    today_count = log["stats"]["by_date"].get(today_str, 0)
    print(f"  Links tracked today: {today_count}")
    print(f"  All-time total:      {log['stats']['total']}")
    print(f"{'='*60}\n")
    return report_path


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        if not HAS_SCHEDULE:
            print("Install schedule first: pip install schedule")
            sys.exit(1)
        run_time = "09:00"
        for arg in sys.argv:
            if arg.startswith("--time="):
                run_time = arg.split("=", 1)[1]
        print(f"Scheduling daily backlink building at {run_time} every day.")
        print("Running first session now. Press Ctrl+C to stop.\n")
        run_daily_session()
        schedule.every().day.at(run_time).do(run_daily_session)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_daily_session()
