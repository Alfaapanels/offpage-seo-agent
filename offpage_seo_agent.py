import anthropic
import os
import json
from datetime import date

def _create_client():
    token_file = os.environ.get("CLAUDE_SESSION_INGRESS_TOKEN_FILE")
    if token_file and os.path.exists(token_file):
        with open(token_file) as f:
            return anthropic.Anthropic(auth_token=f.read().strip())
    return anthropic.Anthropic()

client = _create_client()

TOOLS = [
    {
        "name": "analyze_backlink_quality",
        "description": "Evaluate quality of a backlink pointing to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Your target URL."},
                "backlink_url": {"type": "string", "description": "The URL linking to you."},
                "anchor_text": {"type": "string", "description": "The anchor text used in the link."},
            },
            "required": ["url", "backlink_url", "anchor_text"],
        },
    },
    {
        "name": "categorize_brand_mention",
        "description": "Categorize a brand mention as linked/unlinked and sentiment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "mention_text": {"type": "string", "description": "The text containing the brand mention."},
                "brand_name": {"type": "string", "description": "Your brand or website name."},
            },
            "required": ["mention_text", "brand_name"],
        },
    },
    {
        "name": "score_link_prospect",
        "description": "Score a potential link building prospect on a 0-100 scale.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page_url": {"type": "string", "description": "URL of the prospect page."},
                "page_title": {"type": "string", "description": "Title of the page."},
                "page_content_snippet": {"type": "string", "description": "Short snippet of page content."},
                "your_niche": {"type": "string", "description": "Your website's niche/topic."},
            },
            "required": ["page_url", "page_title", "page_content_snippet", "your_niche"],
        },
    },
    {
        "name": "generate_outreach_template",
        "description": "Generate a personalized outreach email for link building.",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_name": {"type": "string", "description": "Name of the website owner/editor."},
                "prospect_site": {"type": "string", "description": "Their website name."},
                "their_page_topic": {"type": "string", "description": "Topic of the page where you want a link."},
                "your_site": {"type": "string", "description": "Your website name."},
                "your_content_url": {"type": "string", "description": "URL of your content to be linked."},
                "link_type": {"type": "string", "enum": ["guest_post", "broken_link", "resource", "mention"]},
            },
            "required": ["prospect_name", "prospect_site", "their_page_topic", "your_site", "your_content_url", "link_type"],
        },
    },
    {
        "name": "identify_link_gap_opportunity",
        "description": "Identify if a competitor backlink is an opportunity for you.",
        "input_schema": {
            "type": "object",
            "properties": {
                "competitor_domain": {"type": "string", "description": "Competitor's domain."},
                "your_domain": {"type": "string", "description": "Your domain."},
                "linking_page_topic": {"type": "string", "description": "Topic of the page linking to competitor."},
            },
            "required": ["competitor_domain", "your_domain", "linking_page_topic"],
        },
    },
]


def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
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


def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    sentiment = "Positive" if pos_score > neg_score else ("Negative" if neg_score > pos_score else "Neutral")
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    action = "Monitor" if has_link else "Reach out to add your link"
    return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {action}"


def score_link_prospect(page_url: str, page_title: str, page_content_snippet: str, your_niche: str) -> str:
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
    if any(s in page_url for s in [".edu", ".gov", ".org"]):
        score += 30
        reasons.append("High authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    priority = "HIGH PRIORITY" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Prospect Score: {score}/100 - {priority}\nURL: {page_url}\nReasons:\n" + "\n".join(reasons)


def generate_outreach_template(
    prospect_name: str, prospect_site: str, their_page_topic: str,
    your_site: str, your_content_url: str, link_type: str
) -> str:
    templates = {
        "broken_link": f"Subject: Broken link on your {their_page_topic} page\n\nHi {prospect_name},\n\nI noticed a broken link on your {their_page_topic} page on {prospect_site}.\n\nI have a comprehensive guide at {your_content_url} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\n[Your Name]",
        "guest_post": f"Subject: Guest Post Idea for {prospect_site}\n\nHi {prospect_name},\n\nI love your content on {prospect_site} about {their_page_topic}.\n\nI'd love to contribute a guest post. I write for {your_site}.\n\nWould you be open to a collaboration?\n\nBest,\n[Your Name]",
        "resource": f"Subject: Resource suggestion for your {their_page_topic} page\n\nHi {prospect_name},\n\nYour resource page on {their_page_topic} is great! I created {your_content_url} which might help your readers.\n\nWould you take a look?\n\nBest,\n[Your Name]",
        "mention": f"Subject: You mentioned {your_site} - thank you!\n\nHi {prospect_name},\n\nThank you for mentioning {your_site} in your article about {their_page_topic}!\n\nWould you be open to linking directly to {your_content_url}?\n\nThanks,\n[Your Name]",
    }
    return templates.get(link_type, templates["resource"])


def identify_link_gap_opportunity(competitor_domain: str, your_domain: str, linking_page_topic: str) -> str:
    return (
        f"LINK GAP OPPORTUNITY\nCompetitor: {competitor_domain}\nYour site: {your_domain}\n"
        f"Linking page topic: {linking_page_topic}\n\nActions:\n"
        f"1. Find what content earned {competitor_domain} this link\n"
        f"2. Create better content on the same topic for {your_domain}\n"
        f"3. Reach out to the linking page with your resource"
    )


def _dispatch_tool(name: str, inputs: dict) -> str:
    if name == "analyze_backlink_quality":
        return analyze_backlink_quality(**inputs)
    if name == "categorize_brand_mention":
        return categorize_brand_mention(**inputs)
    if name == "score_link_prospect":
        return score_link_prospect(**inputs)
    if name == "generate_outreach_template":
        return generate_outreach_template(**inputs)
    if name == "identify_link_gap_opportunity":
        return identify_link_gap_opportunity(**inputs)
    return f"Unknown tool: {name}"


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    print(f"\nStarting Off-Page SEO Agent for: {your_domain}\n")
    print("=" * 60)

    messages = [{
        "role": "user",
        "content": f"""You are an expert off-page SEO strategist.
Perform a complete off-page SEO analysis for: {your_domain}

Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute these tasks using the available tools:

TASK 1 - Brand Mention Audit
Search for "{brand_name}" mentions and categorize them.

TASK 2 - Competitor Backlink Research
For each competitor, identify link gap opportunities for {your_domain}.

TASK 3 - Link Building Opportunities
Score prospects and identify resource pages, guest post sites, directories.

TASK 4 - Outreach Templates
Generate personalized email templates for top 3 prospects.

TASK 5 - Final Report
Create a prioritized 30-day off-page SEO action plan.""",
    }]

    full_report = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8000,
            tools=TOOLS,
            messages=messages,
        )

        tool_results = []
        for block in response.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)
            elif block.type == "tool_use":
                result = _dispatch_tool(block.name, block.input)
                print(f"\n[Tool: {block.name}]\n{result}\n")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if response.stop_reason == "end_turn" or not tool_results:
            break

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    today = date.today().isoformat()
    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfaa Panels",
        niche="sandwich panel PUF panel pre-engineered building insulated panels India",
        competitors=["epack.in", "mountroof.com", "kingspanjindal.com", "viraatindustries.com", "metecno.in"],
    )
