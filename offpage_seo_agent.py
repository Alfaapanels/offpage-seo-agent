import anthropic
import os
from datetime import datetime
from anthropic import beta_tool

client = anthropic.Anthropic()

# ── alfaapanels.com configuration ──────────────────────────────────────────
TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME    = "Alfaa Panels"
NICHE         = "sandwich panels PUF PIR rockwool cold room clean room insulated panels India manufacturer"
COMPETITORS   = [
    "epack.in",
    "alfapebltd.com",
    "phoenixxsmartbuild.com",
    "viraatindustries.com",
    "metecno.in",
    "beardsell.co.in",
    "prontopanels.com",
    "fmax.in",
]
# B2B directories and platforms to target for backlinks
DIRECTORY_TARGETS = [
    "indiamart.com",
    "tradeindia.com",
    "justdial.com",
    "sulekha.com",
    "dial4trade.com",
    "exportsindia.com",
    "b2bmart.in",
    "yellowpages.in",
    "constructiontimes.co.in",
    "constructionestimatorindia.com",
    "builditupp.com",
    "quora.com",
    "archinomy.com",
    "archello.com",
]
# ───────────────────────────────────────────────────────────────────────────


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
        quality_signals.append("Warning: Generic anchor text - low SEO value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")
    if any(word in backlink_url.lower() for word in ["spam", "casino", "viagra", "xxx"]):
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
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable", "reliable", "trusted", "leading"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "cheap", "defective"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to add your link"
    return (f"Brand: {brand_name}\nType: {mention_type}\n"
            f"Sentiment: {sentiment}\nAction: {action}")


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
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "manufacturer", "supplier", "directory", "blog", "list", "best"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/directory page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (+30)")
    elif any(s in page_url for s in ["indiamart", "tradeindia", "quora", "times", "construction"]):
        score += 25
        reasons.append("High-traffic Indian platform (+25)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return (f"Prospect Score: {score}/100 - {priority}\n"
            f"URL: {page_url}\nReasons:\n" + "\n".join(reasons))


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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your page on {their_page_topic} at {prospect_site} and noticed a broken link.\n\n"
            f"We have a comprehensive resource at {your_content_url} that would be a perfect replacement — "
            f"it covers sandwich panel specifications, PUF/PIR options, and Indian market pricing.\n\n"
            f"Would you consider updating the link? Happy to send more details.\n\n"
            f"Best regards,\n[Your Name]\nAlfaa Panels | {your_site}"
        ),
        "guest_post": (
            f"Subject: Guest Post Proposal for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following {prospect_site} and love your coverage of {their_page_topic}.\n\n"
            f"I'm a content contributor at {your_site} — India's leading sandwich panel manufacturer "
            f"with 35+ years of experience and BIS/ISO certifications. "
            f"I'd love to write a detailed, data-backed guest post for your audience on topics like:\n\n"
            f"• PUF vs PIR panels: which is right for your cold storage?\n"
            f"• How to calculate insulation thickness for industrial buildings\n"
            f"• Clean room panel compliance in pharma manufacturing\n\n"
            f"Would you be open to a contribution?\n\n"
            f"Best,\n[Your Name]\nAlfaa Panels | {your_site}"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your page on {their_page_topic} is really useful! I wanted to share a resource that might "
            f"benefit your readers — {your_content_url} provides a comprehensive guide to sandwich panel "
            f"selection for Indian construction projects, including PUF, PIR, and rockwool options.\n\n"
            f"Would you consider adding it to your {their_page_topic} page?\n\n"
            f"Best,\n[Your Name]\nAlfaa Panels | {your_site}"
        ),
        "mention": (
            f"Subject: You mentioned {your_site} – thank you!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic}!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It'll make it much easier for your readers to learn more about our sandwich panels.\n\n"
            f"Thank you!\n[Your Name]\nAlfaa Panels | {your_site}"
        ),
        "directory": (
            f"Subject: Listing request – Alfaa Panels on {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to add {your_site} to your {their_page_topic} directory.\n\n"
            f"Alfaa Panels is India's trusted sandwich panel manufacturer with 35+ years of experience, "
            f"BIS & ISO 9001 certifications, and automated plants in Hosur, Ahmedabad, Raipur, Karnal, and Pune.\n"
            f"We manufacture PUF, PIR, Rockwool, Cold Room, and Clean Room panels.\n\n"
            f"Listing page: {your_content_url}\n\n"
            f"Please let me know the process to get listed.\n\nBest,\n[Your Name]\nAlfaa Panels | {your_site}"
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
        f"Competitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\n"
        f"Actions:\n"
        f"1. Review what content earned {competitor_domain} this link\n"
        f"2. Create equal or better content on {your_domain}\n"
        f"3. Reach out to the linking page with your resource\n"
        f"4. Highlight Alfaa's advantages: all-India presence, BIS/ISO certs, 15-year warranty, 10 lakh+ sqm/month capacity"
    )


def run_offpage_seo_agent(
    your_domain: str = TARGET_DOMAIN,
    brand_name: str = BRAND_NAME,
    niche: str = NICHE,
    competitors: list = None,
    directories: list = None,
):
    if competitors is None:
        competitors = COMPETITORS
    if directories is None:
        directories = DIRECTORY_TARGETS

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\nOff-Page SEO Agent — {your_domain} — {today}")
    print("=" * 65)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-8",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist specialising in industrial construction,
insulated sandwich panels, cold room panels, clean room panels, and B2B manufacturing in India.

Perform a complete daily off-page SEO backlink-building session for: {your_domain}

Brand name: {brand_name}
Business: India's leading sandwich panel manufacturer — PUF, PIR, Rockwool, Cold Room & Clean Room panels
USPs: 35+ years, BIS/ISO 9001 certified, 10 lakh+ sqm/month, pan-India plants (Hosur, Ahmedabad, Raipur, Karnal, Pune)
Competitors: {', '.join(competitors)}
Directory targets: {', '.join(directories)}
Date: {today}

Execute ALL of the following tasks and report your findings in detail:

TASK 1 – Brand Mention Audit
Search for "Alfaa Panels" and "alfaapanels" online excluding the main site.
Search: "Alfaa Panels" -site:{your_domain}
Search: "alfaapanels" -site:{your_domain}
Categorize each mention with categorize_brand_mention tool. Flag unlinked mentions as outreach targets.

TASK 2 – Competitor Backlink Gap Analysis
For each competitor (epack.in, alfapebltd.com, phoenixxsmartbuild.com), search for:
- Sites linking to them in the sandwich panel / cold room niche
- Quora answers, blog posts, or directories that mention them but not {your_domain}
Use identify_link_gap_opportunity tool for each gap found.

TASK 3 – Today's Fresh Link Opportunities
Search for:
a) "PUF panels" OR "sandwich panels" site:quora.com — find unanswered or low-answer questions
b) "cold room panels manufacturers India" — find resource pages and lists
c) "best sandwich panel manufacturers India" — find roundup posts that exclude {your_domain}
d) Directories: check if {your_domain} is listed on indiamart.com, dial4trade.com, sulekha.com
e) Guest post: construction India "write for us" OR "guest post accepted" 2025 2026

Score the top 5 prospects with score_link_prospect tool.

TASK 4 – Outreach Email Templates
Generate personalised templates for:
1. indiamart.com — directory listing request
2. constructionestimatorindia.com — guest post pitch about PUF panels
3. A roundup post missing Alfaa Panels — resource mention
4. A Quora answer opportunity (mention alfaapanels.com)
5. A broken link or competitor-mention page

Use generate_outreach_template tool for each.

TASK 5 – Today's Action Plan
Create a prioritised list of TODAY's specific actions:
- Exact URLs to register/submit {your_domain} to RIGHT NOW
- Specific pages and editors to contact with exact subject lines
- Quora question URLs where adding an answer with link would be appropriate
- Content gap topics to create for future link attraction
- Quick wins completable in under 30 minutes

Format as a numbered checklist with HIGH / MEDIUM / LOW priority and estimated time."""
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_filename = f"seo_report_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Backlink Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_filename}")
    return report_filename, "\n\n".join(full_report)


if __name__ == "__main__":
    run_offpage_seo_agent()
