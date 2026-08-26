import anthropic
from anthropic import beta_tool
from datetime import date
import json
import os

client = anthropic.Anthropic()

TODAY = date.today().isoformat()

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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
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
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide page - high link value (+30)")
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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention'.
    """
    templates = {
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\nI have a comprehensive guide at {your_content_url} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\n[Your Name] - Alfa Panels",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post. I write for Alfa Panels (alfaapanels.com), specialists in aluminium composite panels and facade systems.\n\nWould you be open to a collaboration?\n\nBest,\n[Your Name] - Alfa Panels",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is great! I created {your_content_url} which might help your readers who are looking for aluminium panel solutions.\n\nWould you take a look?\n\nBest,\n[Your Name] - Alfa Panels",
        "mention": f"Subject: You mentioned Alfa Panels - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning Alfa Panels in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url}?\n\nThanks,\n[Your Name] - Alfa Panels"
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
    return f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\nLinking page topic: {linking_page_topic}\n\nActions:\n1. Find what content earned {competitor_domain} this link\n2. Create better content on the same topic for {your_domain}\n3. Reach out to the linking page with your resource"

@beta_tool
def log_backlink_action(action_type: str, target_url: str, prospect_url: str, status: str, notes: str) -> str:
    """Log a backlink building action taken today.

    Args:
        action_type: Type of action: 'outreach_sent', 'directory_submitted', 'forum_post', 'guest_post_pitched', 'broken_link_found'.
        target_url: The alfaapanels.com URL being promoted.
        prospect_url: The site/page being targeted for the backlink.
        status: 'completed', 'pending', 'opportunity_identified'.
        notes: Additional notes about this action.
    """
    log_entry = {
        "date": TODAY,
        "action_type": action_type,
        "target_url": target_url,
        "prospect_url": prospect_url,
        "status": status,
        "notes": notes
    }

    log_file = f"backlink_log_{TODAY}.json"
    entries = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            entries = json.load(f)
    entries.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(entries, f, indent=2)

    return f"Logged: {action_type} → {prospect_url} [{status}]"


def run_daily_backlink_agent():
    domain = "alfaapanels.com"
    brand = "Alfa Panels"
    niche = "aluminium composite panels facade cladding building materials construction"
    competitors = [
        "alucobond.com",
        "reynobond.com",
        "almaxpanel.com"
    ]

    print(f"\nDaily Backlink Building Agent for: {domain}")
    print(f"Date: {TODAY}")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-5",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            log_backlink_action,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO and link building specialist working for {brand} ({domain}).

Today is {TODAY}. Execute the daily backlink building strategy.

Domain: {domain}
Brand: {brand}
Niche: {niche}
Competitors: {', '.join(competitors)}

DAILY TASKS TO COMPLETE:

**TASK 1 - Brand Mention Discovery**
Search for "{brand}" and "alfaapanels" mentions online.
Search: "{brand}" -site:{domain}
Search: "alfaapanels" -site:{domain}
Find unlinked mentions where we should request a link be added.
Use categorize_brand_mention to classify each mention found.
Use log_backlink_action to record each opportunity with action_type='opportunity_identified'.

**TASK 2 - Competitor Backlink Gap Analysis**
Search for pages linking to each competitor:
- Search: link:alucobond.com aluminium panels
- Search: link:reynobond.com composite panels
Find sites that link to competitors but likely not to alfaapanels.com.
Use identify_link_gap_opportunity for each gap found.
Score each prospect using score_link_prospect with niche="{niche}".

**TASK 3 - Directory & Resource Page Opportunities**
Search for relevant directories and resource pages:
- "aluminium composite panels" + "submit your site" OR "add listing"
- "building materials" + "resource page" OR "useful links"
- "construction suppliers" directory
- "facade systems" blog OR "cladding suppliers" list
Use score_link_prospect to evaluate each opportunity found.
Use log_backlink_action with action_type='directory_submitted' for high-value directories.

**TASK 4 - Forum & Community Engagement**
Search for active discussions in our niche:
- site:reddit.com "aluminium composite panels"
- site:quora.com "ACP panels" OR "aluminium cladding"
- construction forums discussing facade materials
Identify where we can provide expert answers with a natural link.
Use log_backlink_action with action_type='forum_post' for each forum engagement.

**TASK 5 - Broken Link Building**
Search for pages about aluminium panels / facade cladding that may have broken resource links:
- "aluminium composite panels" + "resources" OR "suppliers"
- "ACP panels guide" site:*.edu OR site:*.org
Use score_link_prospect to evaluate pages found.
Use generate_outreach_template with link_type='broken_link' for top prospects.
Use log_backlink_action with action_type='broken_link_found' for each opportunity.

**TASK 6 - Guest Post Prospecting**
Search for blogs accepting guest posts in construction/building materials:
- "write for us" + "construction" OR "building materials" OR "architecture"
- "guest post" + "facade" OR "cladding" OR "aluminium panels"
Generate outreach emails using generate_outreach_template with link_type='guest_post'.
Use log_backlink_action with action_type='guest_post_pitched' for top 3 prospects.

**FINAL REPORT**
Summarize all actions taken today in a structured daily report including:
1. Total opportunities found by category
2. Actions taken (with status)
3. Priority prospects for follow-up
4. Recommended outreach messages ready to send
5. Tomorrow's priority tasks"""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"backlink_report_{TODAY}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Daily Backlink Building Report: {domain}\n")
        f.write(f"**Date:** {TODAY}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_daily_backlink_agent()
