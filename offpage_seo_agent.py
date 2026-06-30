import anthropic
import json
import os
from anthropic import beta_tool
from datetime import date

TARGET_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "aluminum composite panels building materials facade cladding ACP sheets",
    "competitors": [
        "alucoworld.com",
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "3acomposites.com",
    ],
    "target_keywords": [
        "aluminum composite panels",
        "ACP panels",
        "facade cladding",
        "aluminum panels supplier",
        "composite cladding systems",
        "building facade panels",
        "exterior cladding",
        "metal composite panels",
        "PVDF coated ACP",
        "fire rated ACP panels",
    ],
}

BACKLINK_LOG_FILE = "backlink_log.json"
client = anthropic.Anthropic()


def load_backlink_log() -> dict:
    if os.path.exists(BACKLINK_LOG_FILE):
        with open(BACKLINK_LOG_FILE) as f:
            return json.load(f)
    return {
        "submissions": [],
        "outreach_sent": [],
        "opportunities": [],
        "dates_run": [],
        "targeted_sites": [],
    }


def save_backlink_log(data: dict) -> None:
    with open(BACKLINK_LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


@beta_tool
def log_backlink_action(action_type: str, target_site: str, status: str, notes: str) -> str:
    """Log a completed or planned backlink building action to track daily progress.

    Args:
        action_type: One of: directory_submission, guest_post_pitch, forum_post, social_profile, resource_request, broken_link_outreach, citation_building, mention_outreach.
        target_site: Domain or platform where the action was taken or planned.
        status: One of: completed, pending, opportunity_identified.
        notes: Details about the action taken or opportunity found, including any outreach email subject lines.
    """
    log = load_backlink_log()
    today = str(date.today())
    entry = {
        "date": today,
        "action_type": action_type,
        "target_site": target_site,
        "status": status,
        "notes": notes,
    }
    if action_type in ("directory_submission", "citation_building", "social_profile"):
        log["submissions"].append(entry)
    elif action_type in ("guest_post_pitch", "resource_request", "broken_link_outreach", "mention_outreach"):
        log["outreach_sent"].append(entry)
    else:
        log["opportunities"].append(entry)
    if target_site not in log.get("targeted_sites", []):
        log.setdefault("targeted_sites", []).append(target_site)
    save_backlink_log(log)
    return f"Logged: {action_type} -> {target_site} [{status}]"


@beta_tool
def get_backlink_history() -> str:
    """Get the full history of all backlink actions to avoid targeting the same sites twice.

    Returns a summary with all previously targeted sites so the agent never repeats work.
    """
    log = load_backlink_log()
    targeted = log.get("targeted_sites", [])
    submissions = len(log.get("submissions", []))
    outreach = len(log.get("outreach_sent", []))
    opps = len(log.get("opportunities", []))
    dates = log.get("dates_run", [])
    if not targeted:
        return "No backlink history found. This is the first run — all sites are fair game."
    return (
        f"BACKLINK HISTORY SUMMARY\n"
        f"Runs completed: {len(dates)} (last: {dates[-1] if dates else 'N/A'})\n"
        f"Directory/citation submissions: {submissions}\n"
        f"Outreach emails drafted: {outreach}\n"
        f"Opportunities logged: {opps}\n"
        f"Total unique sites targeted: {len(targeted)}\n\n"
        f"PREVIOUSLY TARGETED SITES — DO NOT REPEAT:\n" + "\n".join(sorted(targeted))
    )


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
        signals.append("Warning: Generic anchor text — low SEO value")
    else:
        signals.append(f"Good: Descriptive anchor text: '{anchor_text}'")
    toxic = ["spam", "casino", "viagra", "porn", "adult", "pharma"]
    if any(w in backlink_url.lower() for w in toxic):
        signals.append("TOXIC link detected — disavow recommended")
    else:
        signals.append("Domain appears clean")
    if any(s in backlink_url for s in [".edu", ".gov", ".org"]):
        signals.append("High authority TLD — excellent link")
    return "\n".join(signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked or unlinked with sentiment analysis.

    Args:
        mention_text: The text or snippet containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive = ["great", "best", "excellent", "recommend", "quality", "professional", "trusted", "reliable", "premium"]
    negative = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake", "cheap"]
    pos = sum(1 for w in positive if w in mention_text.lower())
    neg = sum(1 for w in negative if w in mention_text.lower())
    sentiment = "Positive" if pos > neg else ("Negative" if neg > pos else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor for sentiment changes" if has_link else "Send mention outreach to convert into a backlink"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nRecommended Action: {action}"


@beta_tool
def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
    """Score a potential link building prospect on a 0-100 scale.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
        your_niche: Your website's niche or topic.
    """
    score = 0
    reasons = []
    niche_words = your_niche.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High niche relevance (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate niche relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier", "manufacturer", "top", "recommended"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide/directory page type (+30)")
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High authority TLD (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else ("MEDIUM PRIORITY" if score >= 40 else "LOW PRIORITY")
    return f"Score: {score}/100 — {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(f"  • {r}" for r in reasons)


@beta_tool
def generate_outreach_template(
    prospect_name: str,
    prospect_site: str,
    their_page_topic: str,
    your_site: str,
    your_content_url: str,
    link_type: str,
) -> str:
    """Generate a personalized outreach email template for link building.

    Args:
        prospect_name: Name of the website owner or editor (use 'Team' if unknown).
        prospect_site: Their website name or domain.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content or page to be linked.
        link_type: One of: guest_post, broken_link, resource, mention.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link found on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was researching {their_page_topic} and found a broken link on your page at {prospect_site} "
            f"that may be sending your readers to a dead end.\n\n"
            f"I have a detailed resource at {your_content_url} covering aluminum composite panels and facade "
            f"cladding solutions that would be a great replacement for your readers.\n\n"
            f"Would you consider updating the link? Happy to help keep your content valuable.\n\n"
            f"Best regards,\nThe Alfa Panels Team | alfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Pitch for {prospect_site} — ACP & Facade Cladding\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following the content on {prospect_site} about {their_page_topic} — excellent work!\n\n"
            f"We're the team at Alfa Panels (alfaapanels.com), specialists in aluminum composite panels "
            f"and facade cladding systems. I'd love to contribute a guest article on one of these topics:\n\n"
            f"• The Complete Guide to Choosing ACP Panels for Commercial Buildings\n"
            f"• Sustainable Facade Cladding: Materials, Costs & Installation Tips\n"
            f"• Fire-Rated vs Standard ACP Panels: What Architects Need to Know\n\n"
            f"Each article would be original, data-rich, and genuinely useful to your audience.\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best regards,\nThe Alfa Panels Team | alfaapanels.com"
        ),
        "resource": (
            f"Subject: Suggestion for your {their_page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} at {prospect_site} is a great reference — "
            f"I noticed you're curating quality building materials suppliers for your readers.\n\n"
            f"Alfa Panels (alfaapanels.com) might be a valuable addition. We're a leading manufacturer "
            f"and supplier of aluminum composite panels (ACP) and facade cladding systems for commercial "
            f"and architectural projects worldwide.\n\n"
            f"Our resource at {your_content_url} includes technical specifications, installation guides, "
            f"and design inspiration.\n\n"
            f"Would you take a look?\n\n"
            f"Best regards,\nThe Alfa Panels Team | alfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning Alfa Panels!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning Alfa Panels in your content about {their_page_topic} on {prospect_site}! "
            f"We really appreciate the recognition.\n\n"
            f"Would you be open to adding a direct link to {your_content_url}? It would help your readers "
            f"find our product range and technical resources more easily.\n\n"
            f"Thanks again — we'd be happy to return the favour by sharing your content with our audience.\n\n"
            f"Best regards,\nThe Alfa Panels Team | alfaapanels.com"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    """Identify a competitor backlink as a link gap opportunity for your site.

    Args:
        competitor_domain: Competitor's domain that has the backlink.
        your_domain: Your domain that should also have this backlink.
        linking_page_topic: Topic of the page that links to the competitor.
    """
    return (
        f"LINK GAP OPPORTUNITY IDENTIFIED\n"
        f"Competitor: {competitor_domain}\n"
        f"Your site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Action Plan:\n"
        f"1. Find the specific content on {competitor_domain} that earned this link\n"
        f"2. Create more comprehensive content on {your_domain} on the same topic\n"
        f"3. Reach out to the linking site with your superior resource\n"
        f"4. Highlight Alfa Panels' product quality, technical certifications, and global supply capability"
    )


@beta_tool
def generate_directory_listing(directory_name: str, directory_type: str) -> str:
    """Generate standardized business information for directory or citation submissions.

    Args:
        directory_name: Name of the directory or platform.
        directory_type: One of: business_directory, industry_directory, b2b_platform, social_profile, local_directory.
    """
    profiles = {
        "business_directory": (
            f"BUSINESS DIRECTORY SUBMISSION — {directory_name}\n\n"
            f"Business Name: Alfa Panels\n"
            f"Website: https://alfaapanels.com\n"
            f"Category: Building Materials / Aluminum Products / Construction Supplies\n"
            f"Description: Alfa Panels is a leading manufacturer and supplier of premium aluminum composite "
            f"panels (ACP) and facade cladding systems. We serve commercial, residential, and architectural "
            f"projects worldwide with durable, high-quality, and aesthetically superior panel solutions. "
            f"Our product range includes PVDF-coated ACP sheets, PE-coated panels, fire-rated ACP, and "
            f"complete facade cladding systems.\n"
            f"Products: Aluminum Composite Panels, ACP Sheets, Facade Cladding, Metal Cladding Systems, "
            f"Decorative Panels, Fire-Rated ACP\n"
            f"Industries: Construction, Architecture, Interior Design, Commercial Real Estate, Signage\n"
            f"Email: info@alfaapanels.com\n"
            f"Website: alfaapanels.com"
        ),
        "industry_directory": (
            f"INDUSTRY DIRECTORY LISTING — {directory_name}\n\n"
            f"Company: Alfa Panels\n"
            f"Website: alfaapanels.com\n"
            f"Specialization: Aluminum Composite Panels (ACP) & Facade Cladding Systems\n"
            f"Product Categories: ACP Sheets, Exterior Facade Cladding, Interior Decorative Panels, "
            f"Commercial Facades, Fire-Rated Panels\n"
            f"Applications: Commercial Buildings, Shopping Malls, Office Towers, Hotels, Hospitals, "
            f"Airports, Signage & Branding\n"
            f"Features: ISO quality standards, fire-rated options, custom colours & sizes, bulk supply\n"
            f"Contact: info@alfaapanels.com | alfaapanels.com"
        ),
        "b2b_platform": (
            f"B2B PLATFORM PROFILE — {directory_name}\n\n"
            f"Company Name: Alfa Panels\n"
            f"Website: alfaapanels.com\n"
            f"Business Type: Manufacturer & Supplier\n"
            f"Main Products:\n"
            f"  - Aluminum Composite Panels (ACP) — PVDF & PE coated\n"
            f"  - Fire-Rated ACP Panels (FR grade)\n"
            f"  - Facade Cladding Systems\n"
            f"  - Decorative Wall Panels\n"
            f"  - Custom-size ACP Sheets\n"
            f"Min Order: Enquire via website\n"
            f"Supply Ability: Large volume / bulk orders available\n"
            f"Description: Premium aluminum composite panel manufacturer supplying the global construction "
            f"and architecture market. Quality products, competitive pricing, reliable delivery.\n"
            f"Website: https://alfaapanels.com"
        ),
        "social_profile": (
            f"SOCIAL MEDIA PROFILE — {directory_name}\n\n"
            f"Display Name: Alfa Panels | Aluminum Composite Panels\n"
            f"Username Suggestion: alfapanels or alfa_panels\n"
            f"Bio (short): Premium aluminum composite panels & facade cladding manufacturer. "
            f"Quality ACP for commercial & architectural projects. 🔗 alfaapanels.com\n"
            f"Bio (long): Alfa Panels is a leading manufacturer and supplier of high-quality aluminum "
            f"composite panels (ACP) and facade cladding systems. We supply premium building materials "
            f"to construction and architecture projects worldwide. Product range: PVDF ACP, PE ACP, "
            f"fire-rated panels, facade systems. Visit alfaapanels.com\n"
            f"Website: https://alfaapanels.com\n"
            f"Key Hashtags: #AluminumPanels #ACPPanels #FacadeCladding #BuildingMaterials "
            f"#Architecture #ConstructionMaterials #AlfaPanels #MetalCladding"
        ),
        "local_directory": (
            f"LOCAL DIRECTORY LISTING — {directory_name}\n\n"
            f"Business Name: Alfa Panels\n"
            f"Website: https://alfaapanels.com\n"
            f"Category: Building Materials Supplier / Manufacturer\n"
            f"Description: Alfa Panels supplies premium aluminum composite panels (ACP) and facade "
            f"cladding systems for construction and architectural projects. Quality materials, "
            f"competitive pricing, global supply.\n"
            f"Email: info@alfaapanels.com\n"
            f"Services: ACP Panels, Facade Cladding, Metal Panels, Decorative Cladding"
        ),
    }
    return profiles.get(directory_type, profiles["business_directory"])


def run_daily_backlink_agent() -> str:
    config = TARGET_CONFIG
    today = str(date.today())

    print(f"\n{'='*60}")
    print(f"Daily Backlink Building Agent: {config['domain']}")
    print(f"Date: {today}")
    print(f"{'='*60}\n")

    log = load_backlink_log()
    log["dates_run"].append(today)
    save_backlink_log(log)

    print(f"Previously targeted sites: {len(log.get('targeted_sites', []))}")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            log_backlink_action,
            get_backlink_history,
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            generate_directory_listing,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist executing daily backlink building for alfaapanels.com.

Domain: {config['domain']}
Brand: {config['brand_name']}
Niche: {config['niche']}
Target Keywords: {', '.join(config['target_keywords'])}
Competitors: {', '.join(config['competitors'])}
Today: {today}

STEP 1 — CHECK HISTORY (mandatory first step)
Call get_backlink_history() immediately. Study the list of previously targeted sites carefully.
NEVER target any site that appears in that list — find entirely new opportunities each day.

STEP 2 — DIRECTORY & CITATION BUILDING (target 3 new directories)
Search for NEW directories not already in history:
• "aluminum composite panel suppliers directory" site:.com OR site:.org
• "building materials manufacturer directory" "add listing" OR "submit site"
• "construction products directory" free listing
• "B2B manufacturers directory aluminum"
For each new directory found:
1. Score with score_link_prospect()
2. Generate listing text with generate_directory_listing()
3. Log with log_backlink_action(action_type="directory_submission", ...)

STEP 3 — UNLINKED BRAND MENTION HUNTING
Search: "Alfa Panels" -site:alfaapanels.com
Search: "alfaapanels" -site:alfaapanels.com
For each unlinked mention found (not already in history):
1. Categorize with categorize_brand_mention()
2. Generate outreach with generate_outreach_template(link_type="mention")
3. Log with log_backlink_action(action_type="mention_outreach", ...)

STEP 4 — COMPETITOR BACKLINK GAP ANALYSIS
Pick one competitor (rotate daily — today use: {config['competitors'][int(today.replace('-','')) % len(config['competitors'])]}):
Search: "links to {config['competitors'][int(today.replace('-','')) % len(config['competitors'])]}" OR "{config['competitors'][int(today.replace('-','')) % len(config['competitors'])]} backlinks" site listings
For each site linking to the competitor but not alfaapanels.com:
1. Run identify_link_gap_opportunity()
2. Score with score_link_prospect()
3. Generate outreach for top 2 prospects
4. Log with log_backlink_action(action_type="resource_request", ...)

STEP 5 — GUEST POST & RESOURCE PAGE OUTREACH (2 new targets)
Search for NEW opportunities not in history:
• "aluminum composite panels" "write for us" 2025 OR 2026
• "building construction" "guest post guidelines"
• "architecture blog" "contribute" "submit article"
• "construction materials" inurl:resources suppliers
For each new prospect:
1. Score with score_link_prospect()
2. Generate outreach with generate_outreach_template()
3. Log with log_backlink_action(action_type="guest_post_pitch" or "resource_request", ...)

STEP 6 — BROKEN LINK OPPORTUNITIES (1 new target)
Search: "aluminum composite panels" site:*.com -site:alfaapanels.com "resources" OR "links"
Look for pages with outdated or dead links in the ACP/building materials space.
For each opportunity:
1. Score with score_link_prospect()
2. Generate outreach with generate_outreach_template(link_type="broken_link")
3. Log with log_backlink_action(action_type="broken_link_outreach", ...)

STEP 7 — FINAL DAILY REPORT
After completing all tasks and logging all actions, produce this structured report:

## Daily Backlink Building Report — {today}
### Summary
- Total new opportunities actioned today: [N]
- Directories targeted: [N]
- Outreach emails drafted: [N]
- Competitor gaps identified: [N]

### Directory Submissions
[List each directory with its listing text]

### Outreach Emails Drafted
[List each prospect with the full outreach template]

### Link Gap Opportunities
[List competitor gaps found]

### Tomorrow's Priority Actions
[Top 3 recommended actions for the next run]

IMPORTANT: Log EVERY action using log_backlink_action() before producing the final report.""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    os.makedirs("reports", exist_ok=True)
    report_path = f"reports/backlink_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Building Report\n")
        f.write(f"**Domain:** {config['domain']}  \n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_path}")
    return report_path


if __name__ == "__main__":
    run_daily_backlink_agent()
