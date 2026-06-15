import anthropic
import json
import os
from datetime import datetime


def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)
    token_file = os.environ.get("CLAUDE_SESSION_INGRESS_TOKEN_FILE")
    if token_file and os.path.exists(token_file):
        with open(token_file) as f:
            token = f.read().strip()
        return anthropic.Anthropic(auth_token=token)
    return anthropic.Anthropic()


client = _get_client()

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
        "description": "Categorize a brand mention as linked/unlinked and determine sentiment.",
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
                "link_type": {"type": "string", "description": "Type: guest_post, broken_link, resource, or mention."},
            },
            "required": ["prospect_name", "prospect_site", "their_page_topic", "your_site", "your_content_url", "link_type"],
        },
    },
    {
        "name": "identify_link_gap_opportunity",
        "description": "Identify if a competitor backlink is a link gap opportunity for you.",
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


def _execute_tool(name: str, inputs: dict) -> str:
    if name == "analyze_backlink_quality":
        url = inputs["url"]
        backlink_url = inputs["backlink_url"]
        anchor_text = inputs["anchor_text"]
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

    elif name == "categorize_brand_mention":
        mention_text = inputs["mention_text"]
        brand_name = inputs["brand_name"]
        has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
        pos_words = ["great", "best", "excellent", "recommend", "love", "amazing"]
        neg_words = ["bad", "worst", "avoid", "scam", "terrible", "poor"]
        pos = sum(1 for w in pos_words if w in mention_text.lower())
        neg = sum(1 for w in neg_words if w in mention_text.lower())
        sentiment = "Positive" if pos > neg else "Negative" if neg > pos else "Neutral"
        mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
        return f"Brand: {brand_name}\nType: {mention_type}\nSentiment: {sentiment}\nAction: {'Monitor' if has_link else 'Reach out to add your link'}"

    elif name == "score_link_prospect":
        page_url = inputs["page_url"]
        page_title = inputs["page_title"]
        snippet = inputs["page_content_snippet"]
        niche = inputs["your_niche"]
        score = 0
        reasons = []
        niche_words = niche.lower().split()
        content_lower = (page_title + " " + snippet).lower()
        relevance = sum(1 for w in niche_words if w in content_lower)
        if relevance >= 3:
            score += 40
            reasons.append("High relevance to your niche (+40)")
        elif relevance >= 1:
            score += 20
            reasons.append("Moderate relevance (+20)")
        else:
            reasons.append("Low relevance (0)")
        high_value = ["resource", "guide", "tools", "blog", "list", "best"]
        if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
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

    elif name == "generate_outreach_template":
        pn = inputs["prospect_name"]
        ps = inputs["prospect_site"]
        pt = inputs["their_page_topic"]
        ys = inputs["your_site"]
        yc = inputs["your_content_url"]
        lt = inputs["link_type"]
        templates = {
            "broken_link": f"Subject: Broken link on your {pt} page\n\nHi {pn},\n\nI noticed a broken link on your {pt} page on {ps}.\n\nI have a comprehensive guide at {yc} that would be a great replacement.\n\nWould you consider updating the link?\n\nBest,\n[Your Name]",
            "guest_post": f"Subject: Guest Post Idea for {ps}\n\nHi {pn},\n\nI love your content on {ps} about {pt}.\n\nI'd love to contribute a guest post. I write for {ys}.\n\nWould you be open to a collaboration?\n\nBest,\n[Your Name]",
            "resource": f"Subject: Resource suggestion for your {pt} page\n\nHi {pn},\n\nYour resource page on {pt} is great! I created {yc} which might help your readers.\n\nWould you take a look?\n\nBest,\n[Your Name]",
            "mention": f"Subject: You mentioned {ys} - thank you!\n\nHi {pn},\n\nThank you for mentioning {ys} in your article about {pt}!\n\nWould you be open to linking directly to {yc}?\n\nThanks,\n[Your Name]",
        }
        return templates.get(lt, templates["resource"])

    elif name == "identify_link_gap_opportunity":
        cd = inputs["competitor_domain"]
        yd = inputs["your_domain"]
        lpt = inputs["linking_page_topic"]
        return (
            f"LINK GAP OPPORTUNITY\nCompetitor: {cd}\nYour site: {yd}\n"
            f"Linking page topic: {lpt}\n\nActions:\n"
            f"1. Find what content earned {cd} this link\n"
            f"2. Create better content on the same topic for {yd}\n"
            f"3. Reach out to the linking page with your resource"
        )

    return f"Unknown tool: {name}"


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\nStarting Off-Page SEO Agent for: {your_domain} [{today}]\n")
    print("=" * 60)

    system_prompt = (
        "You are an expert off-page SEO strategist with deep knowledge of link building, "
        "brand mentions, and competitor analysis. Use web_search to find real data and opportunities. "
        "Be specific and actionable in all recommendations."
    )

    user_prompt = f"""Perform a complete off-page SEO analysis for: {your_domain}
Date: {today}
Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute these tasks IN ORDER and use web_search to find real, current data:

TASK 1 - Brand Mention Audit
Search for "{brand_name}" AND "alfa panels" mentions online (excluding {your_domain}).
Identify unlinked mentions that can be converted to backlinks.
Use categorize_brand_mention tool on each mention found.

TASK 2 - Competitor Backlink Research
For each competitor ({', '.join(competitors)}), use web_search to find sites that link to them.
Search: link:{competitors[0]} site:construction OR building OR architecture
Use identify_link_gap_opportunity for the best opportunities found.

TASK 3 - Link Building Opportunities
Find 5-10 high-value link building targets:
- Resource pages in the construction/building panels niche
- Guest post opportunities on architecture and construction blogs
- Industry directories for building materials manufacturers
- Forum discussions about insulated panels where you can contribute
Search for these specifically and score each using score_link_prospect.

TASK 4 - Outreach Templates
Generate personalized email templates for the top 3 prospects found.
Use generate_outreach_template for each.

TASK 5 - Final Report
Create a prioritized 30-day off-page SEO action plan with specific URLs, contacts, and deadlines.
Include at least 10 specific actionable items with expected impact scores."""

    messages = [{"role": "user", "content": user_prompt}]
    full_report = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=16000,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        tool_uses = []
        text_blocks = []

        for block in response.content:
            if block.type == "text":
                text_blocks.append(block.text)
                print(block.text)
                full_report.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        if response.stop_reason == "end_turn" or not tool_uses:
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tu in tool_uses:
            print(f"\n[Tool: {tu.name}]")
            result = _execute_tool(tu.name, tu.input)
            print(result[:200] + "..." if len(result) > 200 else result)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("\n\n".join(full_report))
    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfa Panels",
        niche="building panels construction insulated facade panels",
        competitors=[
            "kingspanpanels.com",
            "metecno.com",
            "isopan.com",
            "brunel.net",
            "panelsuk.co.uk",
        ],
    )
