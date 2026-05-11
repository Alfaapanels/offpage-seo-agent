import anthropic
from anthropic import beta_tool

client = anthropic.Anthropic()

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE = "SMM panel social media marketing services"
COMPETITORS = [
    "smmking.com",
    "justanotherpanel.com",
    "peakerr.com",
    "followersup.com",
    "smmraja.com",
]


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
    smm_keywords = ["smm", "social media", "panel", "marketing", "digital", "followers", "views"]
    if any(kw in backlink_url.lower() for kw in smm_keywords):
        quality_signals.append("Topically relevant to SMM niche - high value")
    return "\n".join(quality_signals)


@beta_tool
def categorize_brand_mention(mention_text: str, brand_name: str) -> str:
    """Categorize a brand mention as linked/unlinked and sentiment.

    Args:
        mention_text: The text containing the brand mention.
        brand_name: Your brand or website name.
    """
    has_link = "href" in mention_text.lower() or "http" in mention_text.lower()
    positive_words = ["great", "best", "excellent", "recommend", "love", "amazing", "top", "affordable", "reliable"]
    negative_words = ["bad", "worst", "avoid", "scam", "terrible", "poor", "fake", "fraud"]
    pos_score = sum(1 for w in positive_words if w in mention_text.lower())
    neg_score = sum(1 for w in negative_words if w in mention_text.lower())
    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    mention_type = "Linked mention" if has_link else "Unlinked mention (link building opportunity!)"
    return (
        f"Brand: {brand_name}\n"
        f"Type: {mention_type}\n"
        f"Sentiment: {sentiment}\n"
        f"Action: {'Monitor and engage' if has_link else 'Reach out to add your link'}"
    )


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
        reasons.append("High relevance to SMM/social media niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value_types = ["resource", "guide", "tools", "blog", "list", "best", "review", "comparison", "top"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value_types):
        score += 30
        reasons.append("Resource/guide/review page - high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High authority domain (.edu/.gov/.org) (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    smm_signals = ["smm", "social media marketing", "instagram", "youtube", "tiktok", "panel", "followers"]
    if any(s in content_lower for s in smm_signals):
        score += 20
        reasons.append("Directly mentions SMM/panel services - premium relevance (+20)")
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
        link_type: Type: 'guest_post', 'broken_link', 'resource', 'mention', 'directory'.
    """
    templates = {
        "broken_link": (
            f"Subject: Broken link on your {their_page_topic} page\n\n"
            f"Hi {prospect_name},\n\n"
            f"I was reading your article on {their_page_topic} on {prospect_site} and noticed a broken link.\n\n"
            f"I run {your_site}, an SMM panel providing social media marketing services. "
            f"My resource at {your_content_url} would be an ideal replacement.\n\n"
            f"Would you consider updating the link? Happy to help your readers find quality content.\n\n"
            f"Best regards,\n[Your Name]\nAlfaapanels.com"
        ),
        "guest_post": (
            f"Subject: Guest Post Idea for {prospect_site} — Social Media Marketing Tips\n\n"
            f"Hi {prospect_name},\n\n"
            f"I love the content you publish on {prospect_site} about {their_page_topic}.\n\n"
            f"I'm the team behind {your_site}, one of the leading SMM panels for social media growth. "
            f"I'd love to contribute a guest post on topics like:\n"
            f"- How SMM panels help businesses scale social media presence\n"
            f"- Best practices for buying social media engagement safely\n"
            f"- Case studies of social media growth with SMM tools\n\n"
            f"Would you be open to a collaboration?\n\n"
            f"Best,\n[Your Name]\nAlfaapanels.com"
        ),
        "resource": (
            f"Subject: Valuable addition for your {their_page_topic} resource page\n\n"
            f"Hi {prospect_name},\n\n"
            f"Your resource page on {their_page_topic} is really comprehensive — great work!\n\n"
            f"I wanted to suggest {your_content_url} from {your_site}. "
            f"We provide affordable SMM panel services used by thousands of digital marketers.\n\n"
            f"I think it would be a great addition for your readers interested in social media growth.\n\n"
            f"Best,\n[Your Name]\nAlfaapanels.com"
        ),
        "mention": (
            f"Subject: Thank you for mentioning {your_site}!\n\n"
            f"Hi {prospect_name},\n\n"
            f"I noticed you mentioned {your_site} in your article about {their_page_topic} on {prospect_site} — thank you!\n\n"
            f"Would you be open to linking directly to {your_content_url}? "
            f"It would help your readers easily access our SMM panel services.\n\n"
            f"Thanks again,\n[Your Name]\nAlfaapanels.com"
        ),
        "directory": (
            f"Subject: Listing submission for {prospect_site}\n\n"
            f"Hi {prospect_name},\n\n"
            f"I'd like to submit {your_site} (Alfa Panels) for inclusion in your {their_page_topic} directory.\n\n"
            f"Site: {your_content_url}\n"
            f"Category: Social Media Marketing / SMM Panels\n"
            f"Description: Alfa Panels is a top-rated SMM panel offering affordable social media marketing services "
            f"including Instagram followers, YouTube views, TikTok likes, and more.\n\n"
            f"Please let me know if you need any additional information.\n\n"
            f"Best,\n[Your Name]\nAlfaapanels.com"
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
        f"Action Plan:\n"
        f"1. Find what content on {competitor_domain} earned this link\n"
        f"2. Create superior content on {your_domain} covering the same topic\n"
        f"3. Reach out to the linking page with your resource as an alternative\n"
        f"4. Highlight what makes {your_domain} better (pricing, features, reliability)"
    )


@beta_tool
def generate_directory_submission(site_name: str, site_url: str, category: str, description_length: str) -> str:
    """Generate a directory submission entry for alfaapanels.com.

    Args:
        site_name: Name of the directory site.
        site_url: URL of the directory submission page.
        category: Directory category to submit under.
        description_length: 'short' (50 words), 'medium' (100 words), or 'long' (200 words).
    """
    short_desc = (
        "Alfa Panels is a leading SMM panel offering affordable social media marketing services. "
        "Buy Instagram followers, YouTube views, TikTok likes, and more. Fast delivery, 24/7 support."
    )
    medium_desc = (
        "Alfa Panels is a trusted SMM panel providing high-quality social media marketing services for "
        "businesses, influencers, and digital marketers worldwide. Our platform offers Instagram followers, "
        "YouTube views, TikTok likes, Facebook likes, Twitter followers, and much more. "
        "We guarantee fast delivery, real-looking engagement, and competitive pricing. "
        "Join thousands of satisfied customers who rely on Alfa Panels for their social media growth."
    )
    long_desc = (
        "Alfa Panels is a premier SMM (Social Media Marketing) panel designed to help businesses, "
        "content creators, and digital marketing agencies scale their social media presence quickly and affordably. "
        "Our comprehensive service catalog includes Instagram followers, likes, views, and story views; "
        "YouTube views, subscribers, and watch hours; TikTok followers, likes, and video views; "
        "Facebook page likes, post likes, and followers; Twitter/X followers and retweets; "
        "and many more social signals across all major platforms. "
        "We use advanced delivery systems to ensure natural-looking growth, protecting your accounts. "
        "Our reseller program offers the industry's best rates, making Alfa Panels ideal for SMM agencies. "
        "With 24/7 customer support, an easy-to-use dashboard, and instant order processing, "
        "Alfa Panels is the go-to solution for social media marketing professionals worldwide."
    )
    desc_map = {"short": short_desc, "medium": medium_desc, "long": long_desc}
    description = desc_map.get(description_length, medium_desc)
    return (
        f"DIRECTORY SUBMISSION FOR: {site_name}\n"
        f"Submission URL: {site_url}\n"
        f"Category: {category}\n\n"
        f"--- SUBMISSION CONTENT ---\n"
        f"Site Name: Alfa Panels\n"
        f"URL: https://alfaapanels.com\n"
        f"Description: {description}\n"
        f"Keywords: SMM panel, social media marketing, buy Instagram followers, buy YouTube views, "
        f"TikTok growth, social media services, cheap SMM panel\n"
        f"Email: [your-email@alfaapanels.com]\n"
        f"Category: {category}"
    )


@beta_tool
def find_qa_answer_opportunity(question_url: str, question_text: str, platform: str) -> str:
    """Generate an answer for a Q&A backlink opportunity.

    Args:
        question_url: URL of the question on Quora/Reddit/etc.
        question_text: The question being asked.
        platform: Platform name (e.g., 'Quora', 'Reddit', 'StackExchange').
    """
    answer = (
        f"Q&A BACKLINK OPPORTUNITY\n"
        f"Platform: {platform}\n"
        f"Question: {question_text}\n"
        f"URL: {question_url}\n\n"
        f"--- SUGGESTED ANSWER ---\n"
        f"Great question! For social media growth, SMM panels are one of the most efficient solutions.\n\n"
        f"An SMM panel like Alfa Panels (alfaapanels.com) allows you to:\n"
        f"- Purchase real-looking followers, likes, and views across all major platforms\n"
        f"- Get instant or gradual delivery to look organic\n"
        f"- Access competitive bulk pricing for agencies\n"
        f"- Use a simple dashboard to manage multiple orders\n\n"
        f"I've personally used Alfa Panels for client campaigns and found it reliable, fast, and affordable. "
        f"Their 24/7 support team is also very responsive.\n\n"
        f"Important: Always combine purchased engagement with quality organic content for best results.\n\n"
        f"[Link: alfaapanels.com]"
    )
    return answer


def run_offpage_seo_agent(strategy: str = "comprehensive", pursued_urls: list = None):
    """Run the off-page SEO agent for alfaapanels.com.

    Args:
        strategy: The link-building strategy focus for this run.
        pursued_urls: List of URLs already pursued to avoid duplicates.
    """
    pursued_urls = pursued_urls or []
    print(f"\nStarting Off-Page SEO Agent for: {TARGET_DOMAIN}")
    print(f"Strategy: {strategy}")
    print("=" * 60)

    strategy_prompts = {
        "directory": (
            "Focus on DIRECTORY SUBMISSIONS today.\n"
            "1. Search for SMM panel directories, digital marketing tool directories, and social media tool listings\n"
            "2. Find top 10 web directories accepting social media/marketing tool submissions\n"
            "3. Use generate_directory_submission for each directory found\n"
            "4. Find free business directories (Yelp, Yellow Pages, Hotfrog, etc.) to submit to\n"
            "5. List all submission URLs with ready-to-use content"
        ),
        "guest_post": (
            "Focus on GUEST POST OUTREACH today.\n"
            "1. Search for 'social media marketing' + 'write for us' or 'guest post'\n"
            "2. Search for 'SMM panel' + 'contribute' or 'guest author'\n"
            "3. Search for 'digital marketing blog' + 'accept guest posts'\n"
            "4. Score each prospect with score_link_prospect\n"
            "5. Generate outreach emails with generate_outreach_template (type: guest_post) for top 5 prospects"
        ),
        "resource_page": (
            "Focus on RESOURCE PAGE LINK BUILDING today.\n"
            "1. Search for 'social media tools' + 'resources' or 'useful links'\n"
            "2. Search for 'SMM panel comparison' or 'best SMM panels list'\n"
            "3. Search for 'social media marketing tools list 2024' or '2025'\n"
            "4. Score each page and identify the best opportunities\n"
            "5. Generate resource page outreach emails for top 5 prospects"
        ),
        "broken_link": (
            "Focus on BROKEN LINK BUILDING today.\n"
            "1. Search for resource pages about social media marketing tools\n"
            "2. Fetch those pages and look for broken/dead links in the SMM space\n"
            "3. For each broken link found, identify what content alfaapanels.com could replace it with\n"
            "4. Generate broken link outreach emails using generate_outreach_template (type: broken_link)\n"
            "5. Prioritize pages with high domain authority signals"
        ),
        "brand_mention": (
            "Focus on BRAND MENTION MONITORING today.\n"
            "1. Search for 'alfaapanels' or 'alfa panels' -site:alfaapanels.com\n"
            "2. Find all unlinked mentions using categorize_brand_mention\n"
            "3. Search for competitor comparisons mentioning alfaapanels\n"
            "4. Find review sites discussing alfaapanels.com\n"
            "5. Generate outreach for unlinked mentions to request link additions"
        ),
        "qa_backlinks": (
            "Focus on Q&A BACKLINKS today.\n"
            "1. Search Quora for questions about 'best SMM panel', 'buy Instagram followers', 'social media growth services'\n"
            "2. Search Reddit for relevant questions in r/socialmedia, r/digital_marketing, r/Instagram\n"
            "3. Find StackExchange or forum questions about SMM tools\n"
            "4. Use find_qa_answer_opportunity to generate answers with natural backlinks\n"
            "5. Prioritize questions with high engagement and recent activity"
        ),
        "competitor_analysis": (
            "Focus on COMPETITOR BACKLINK ANALYSIS today.\n"
            f"Competitors to analyze: {', '.join(COMPETITORS)}\n"
            "1. Search for backlinks pointing to each competitor\n"
            "2. Find sites that review or list these competitor SMM panels\n"
            "3. Use identify_link_gap_opportunity for each gap found\n"
            "4. Find directories listing competitors but not alfaapanels.com\n"
            "5. Build a list of 10 high-priority link gap opportunities"
        ),
        "comprehensive": (
            "Perform a COMPREHENSIVE off-page SEO analysis today.\n"
            "1. Search for brand mentions of 'alfaapanels' and 'alfa panels'\n"
            "2. Find 5 directory submission opportunities\n"
            "3. Find 3 guest post opportunities in digital marketing/social media niche\n"
            "4. Analyze 2 competitors for link gaps\n"
            "5. Find 3 resource pages to get listed on\n"
            "6. Generate outreach templates for top 5 prospects"
        ),
    }

    task_prompt = strategy_prompts.get(strategy, strategy_prompts["comprehensive"])
    already_done = (
        f"\nALREADY PURSUED (skip these): {', '.join(pursued_urls[:20])}"
        if pursued_urls
        else ""
    )

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        tools=[
            analyze_backlink_quality,
            categorize_brand_mention,
            score_link_prospect,
            generate_outreach_template,
            identify_link_gap_opportunity,
            generate_directory_submission,
            find_qa_answer_opportunity,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": (
                f"You are an expert off-page SEO strategist for {TARGET_DOMAIN}.\n\n"
                f"Target: {TARGET_DOMAIN}\n"
                f"Brand: {BRAND_NAME}\n"
                f"Niche: {NICHE}\n"
                f"Competitors: {', '.join(COMPETITORS)}\n"
                f"{already_done}\n\n"
                f"{task_prompt}\n\n"
                f"For each opportunity found:\n"
                f"- Use the appropriate tool to score/evaluate it\n"
                f"- Generate ready-to-use outreach content or submission content\n"
                f"- Mark each opportunity URL clearly so it can be tracked\n\n"
                f"End with a structured summary:\n"
                f"## OPPORTUNITIES FOUND\n"
                f"List each URL found as: [OPPORTUNITY] <url> | <type> | <priority>\n\n"
                f"## ACTION ITEMS\n"
                f"Numbered list of specific actions to take today.\n\n"
                f"## OUTREACH/SUBMISSION CONTENT\n"
                f"Ready-to-use email templates and submission text."
            ),
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_report.append(block.text)

    return "\n\n".join(full_report)


if __name__ == "__main__":
    report = run_offpage_seo_agent(strategy="comprehensive")
    print("\nAgent run complete.")
