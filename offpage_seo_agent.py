"""
Off-Page SEO Agent for alfaapanels.com
Finds and builds relevant backlinks daily using Claude AI + web tools.
"""

import anthropic
from anthropic import beta_tool


client = anthropic.Anthropic()


# ── Custom SEO tools ──────────────────────────────────────────────────────────

@beta_tool
def analyze_backlink_quality(url: str, backlink_url: str, anchor_text: str) -> str:
    """Evaluate quality of a backlink pointing to a URL.

    Args:
        url: Your target URL.
        backlink_url: The URL linking to you.
        anchor_text: The anchor text used in the link.
    """
    quality_signals = []
    generic_anchors = {"click here", "website", "here", "link", "read more"}
    if anchor_text.lower() in generic_anchors:
        quality_signals.append("Warning: Generic anchor text - low value")
    else:
        quality_signals.append(f"Good: Descriptive anchor: '{anchor_text}'")

    toxic_keywords = ["spam", "casino", "viagra", "adult", "porn", "gambling"]
    if any(word in backlink_url.lower() for word in toxic_keywords):
        quality_signals.append("TOXIC link - disavow recommended")
    else:
        quality_signals.append("Domain appears clean")

    authority_domains = [".edu", ".gov", ".org"]
    if any(s in backlink_url for s in authority_domains):
        quality_signals.append("High authority domain - prioritise")

    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "quality", "durable", "reliable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "expensive", "slow"]

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
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for word in niche_words if word in content_lower)

    if relevance >= 3:
        score += 40
        reasons.append("High relevance to your niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (+0)")

    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "directory", "supplier"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/directory page - high link value (+30)")

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
    link_type: str,
) -> str:
    """Generate a personalised outreach email for link building.

    Args:
        prospect_name: Name of the website owner/editor.
        prospect_site: Their website name.
        their_page_topic: Topic of the page where you want a link.
        your_site: Your website name.
        your_content_url: URL of your content to be linked.
        link_type: 'guest_post', 'broken_link', 'resource', or 'mention'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed a broken link on your {their_page_topic} page at {prospect_site}.\n\n"
            f"I have a comprehensive resource at {your_content_url} that would make a great replacement.\n\n"
            f"Would you consider updating the link?\n\nBest regards,\n{your_site} Team"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I've been following your content on {their_page_topic} at {prospect_site} — really insightful work.\n\n"
            f"I write for {your_site} and would love to contribute a guest post tailored to your audience.\n\n"
            f"Happy to share topic ideas that align with what you publish. Would you be open to a collaboration?\n\n"
            f"Best regards,\n{your_site} Team"
        ),
        "resource": (
            f"Subject: Resource suggestion for your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really helpful! "
            f"I thought {your_content_url} might add value for your readers as well.\n\n"
            f"Would you take a look and consider including it?\n\n"
            f"Best regards,\n{your_site} Team"
        ),
        "mention": (
            f"Subject: Loved your mention of {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"Thank you for mentioning {your_site} in your article about {their_page_topic} on {prospect_site}!\n\n"
            f"Would you be open to linking directly to {your_content_url} so your readers can find us easily?\n\n"
            f"Thanks,\n{your_site} Team"
        ),
    }
    return templates.get(link_type, templates["resource"])


@beta_tool
def identify_link_gap_opportunity(
    competitor_domain: str,
    your_domain: str,
    linking_page_topic: str,
) -> str:
    """Identify if a competitor backlink is an opportunity for you.

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
        f"1. Find the specific content on {competitor_domain} that earned this link\n"
        f"2. Create a better / more up-to-date version for {your_domain}\n"
        f"3. Reach out to the linking page owner with your improved resource\n"
        f"4. Mention specific ways your content is more helpful than the competitor's"
    )


@beta_tool
def draft_directory_submission(
    directory_name: str,
    directory_url: str,
    business_name: str,
    business_url: str,
    niche: str,
    description: str,
) -> str:
    """Draft a business directory submission for a given directory.

    Args:
        directory_name: Name of the directory site.
        directory_url: URL of the directory.
        business_name: Your business name.
        business_url: Your website URL.
        niche: Business category/niche.
        description: Short business description (max 150 words).
    """
    return (
        f"DIRECTORY SUBMISSION DRAFT\n"
        f"Directory: {directory_name} ({directory_url})\n\n"
        f"Business Name: {business_name}\n"
        f"Website: {business_url}\n"
        f"Category: {niche}\n"
        f"Description:\n{description}\n\n"
        f"Next steps:\n"
        f"1. Visit {directory_url} and find the 'Add Listing' or 'Submit Business' page\n"
        f"2. Use the details above to complete the form\n"
        f"3. Verify ownership if required\n"
        f"4. Track submission date and follow up if not listed within 2 weeks"
    )


@beta_tool
def draft_qa_answer(
    platform: str,
    question_url: str,
    question_text: str,
    your_domain: str,
    niche: str,
) -> str:
    """Draft an expert Q&A answer that naturally includes a backlink.

    Args:
        platform: Platform name (e.g., Quora, Reddit).
        question_url: URL of the question/thread.
        question_text: The question being answered.
        your_domain: Your website domain for the backlink.
        niche: Your niche for context.
    """
    return (
        f"Q&A ANSWER DRAFT\n"
        f"Platform: {platform}\n"
        f"Question URL: {question_url}\n"
        f"Question: {question_text}\n\n"
        f"[AI will generate a helpful, expert answer here that:\n"
        f" - Answers the question fully with practical advice about {niche}\n"
        f" - Naturally references {your_domain} as a resource or example\n"
        f" - Follows {platform}'s community guidelines (no spam)\n"
        f" - Is at least 150 words to provide real value]\n\n"
        f"Tip: Post this answer, then link back to a relevant page on {your_domain} as a 'further reading' resource."
    )


# ── Main agent runner ─────────────────────────────────────────────────────────

def run_offpage_seo_agent(
    your_domain: str,
    brand_name: str,
    niche: str,
    competitors: list,
    run_date: str = None,
) -> str:
    """Run the off-page SEO agent and return the full report text."""
    import datetime
    if run_date is None:
        run_date = datetime.date.today().isoformat()

    print(f"\nStarting Off-Page SEO Agent for: {your_domain}  [{run_date}]")
    print("=" * 60)

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            draft_directory_submission,
            draft_qa_answer,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO strategist working on {run_date}.

Build relevant backlinks today for: {your_domain}
Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute ALL of the following tasks and produce concrete, actionable output for each.

──────────────────────────────────────────
TASK 1 — Brand Mention Audit
──────────────────────────────────────────
Search for "{brand_name}" mentions across the web (exclude {your_domain}).
• Use web_search with: "{brand_name}" -site:{your_domain}
• For each result, use categorize_brand_mention to classify it.
• List top 5 unlinked mentions with the outreach action needed.

──────────────────────────────────────────
TASK 2 — Competitor Backlink Gap Analysis
──────────────────────────────────────────
For each competitor in [{', '.join(competitors)}]:
• Search for sites linking to them: link:{competitor} OR "{competitor}" resources
• Use identify_link_gap_opportunity for each promising result.
• Prioritise pages that would also accept a link to {your_domain}.

──────────────────────────────────────────
TASK 3 — Directory Submission Opportunities
──────────────────────────────────────────
Find 5 relevant business directories or niche directories where {your_domain}
is not yet listed. Search for: "{niche} business directory" OR "{niche} supplier listing".
For each, use draft_directory_submission with a compelling business description.

──────────────────────────────────────────
TASK 4 — Q&A & Forum Backlinks
──────────────────────────────────────────
Search Quora, Reddit, and niche forums for questions related to {niche}
that were asked in the last 30 days and have no accepted answer (or a weak one).
For each qualifying question, use draft_qa_answer to create a helpful, expert reply
that naturally references {your_domain}.
Find at least 3 questions.

──────────────────────────────────────────
TASK 5 — Resource Page & Guest Post Outreach
──────────────────────────────────────────
Search for:
  • "{niche} resources" inurl:resources OR inurl:links
  • "{niche} write for us" OR "{niche} guest post"
Use score_link_prospect for each candidate.
Use generate_outreach_template (type 'resource' or 'guest_post') for the top 3.

──────────────────────────────────────────
TASK 6 — Broken Link Building
──────────────────────────────────────────
Search for "{niche} useful links" OR "{niche} recommended suppliers".
Fetch one promising page using web_fetch and look for any links that appear outdated.
Use generate_outreach_template (type 'broken_link') for each opportunity found.

──────────────────────────────────────────
TASK 7 — Today's Action Summary
──────────────────────────────────────────
Produce a prioritised daily action plan:
• List each backlink opportunity with: Type | Target URL | Priority | Estimated Effort
• Sort by Priority (HIGH → MEDIUM → LOW)
• Include a "Quick wins" section (tasks completable in < 30 minutes today)
• Provide a running count: Total opportunities found today: X
""",
        }],
    )

    full_report: list[str] = []
    for message in runner:
        for block in message.content:
            if hasattr(block, "text"):
                print(block.text)
                full_report.append(block.text)

    report_text = "\n\n".join(full_report)
    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{run_date}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Report: {your_domain}\n")
        f.write(f"**Date:** {run_date}\n\n")
        f.write(report_text)

    print(f"\nReport saved to: {report_filename}")
    return report_text


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfa Panels",
        niche="sandwich panels building materials construction insulation",
        competitors=[
            "kingspan.com",
            "metecno.com",
            "isopan.com",
        ],
    )
