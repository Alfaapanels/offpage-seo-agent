#!/usr/bin/env python3
"""Daily backlink builder for alfaapanels.com — runs every day to build relevant backlinks."""

import anthropic
from anthropic import beta_tool
import json
import os
from datetime import datetime, date

client = anthropic.Anthropic()

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "AlfaPanels"
NICHE = "SMM panel, social media marketing services, buy followers likes views reseller panel"
COMPETITORS = ["justanotherpanel.com", "peakerr.com", "smmstone.com", "smmfollows.com"]
LOG_FILE = "backlink_log.json"


def _load_log() -> dict:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return {"activities": [], "contacted_domains": [], "submitted_directories": []}


def _save_log(log_data: dict) -> None:
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2, default=str)


@beta_tool
def log_backlink_activity(activity_type: str, target_url: str, status: str, notes: str = "") -> str:
    """Log a completed backlink activity and mark the domain as contacted.

    Args:
        activity_type: Type: 'forum_post', 'qa_answer', 'directory', 'blog_comment', 'profile', 'outreach'.
        target_url: The URL where the backlink was placed or outreach was sent.
        status: Outcome: 'completed', 'pending', 'failed'.
        notes: Optional context about the activity.
    """
    log = _load_log()
    entry = {
        "date": datetime.now().isoformat(),
        "type": activity_type,
        "url": target_url,
        "status": status,
        "notes": notes,
    }
    log["activities"].append(entry)
    # Extract domain and mark as contacted
    try:
        domain = target_url.split("//")[-1].split("/")[0].lstrip("www.")
    except Exception:
        domain = target_url
    if domain and domain not in log["contacted_domains"]:
        log["contacted_domains"].append(domain)
    _save_log(log)
    return f"Logged [{activity_type}] at {target_url} — {status}. Domain '{domain}' marked as contacted."


@beta_tool
def check_already_contacted(domain: str) -> str:
    """Check whether a domain has already been contacted to avoid duplicate outreach.

    Args:
        domain: The root domain to check (e.g. 'example.com', no www or protocol).
    """
    log = _load_log()
    clean = domain.lstrip("www.").rstrip("/")
    if clean in log["contacted_domains"]:
        return f"SKIP — already contacted: {clean}"
    return f"GO — new opportunity: {clean}"


@beta_tool
def get_todays_activity_summary() -> str:
    """Return a summary of backlink activities already completed today."""
    today = date.today().isoformat()
    log = _load_log()
    todays = [a for a in log["activities"] if a["date"].startswith(today)]
    if not todays:
        return f"No activities yet today ({today}). Starting fresh."
    lines = [f"Activities completed today ({today}): {len(todays)}"]
    for a in todays:
        lines.append(f"  [{a['type']}] {a['url']} — {a['status']}")
    lines.append(f"\nTotal unique domains contacted overall: {len(log['contacted_domains'])}")
    return "\n".join(lines)


@beta_tool
def generate_forum_post(forum_topic: str, context: str, link_placement: str) -> str:
    """Generate a valuable, non-spammy forum post that naturally references alfaapanels.com.

    Args:
        forum_topic: The title or topic of the forum thread.
        context: A brief summary of what the thread discusses and the audience.
        link_placement: Where the link goes: 'contextual' (in post body) or 'signature'.
    """
    if link_placement == "signature":
        return f"""Great discussion on {forum_topic}!

{context}

Based on my experience, I'd add that reliability and support matter just as much as pricing when choosing services in this space. A bad provider can hurt your accounts, so always test with small orders first.

---
_Need affordable SMM services? I use [AlfaPanels](https://alfaapanels.com) — covers Instagram, YouTube, TikTok, and more._"""

    return f"""Jumping in on {forum_topic} since I've tested a few options recently.

{context}

From personal experience: **AlfaPanels** (https://alfaapanels.com) has been my go-to. Key reasons:
- Wide service catalog — Instagram, YouTube, TikTok, Facebook, Twitter, LinkedIn
- Reseller API with competitive wholesale rates
- Actual refill guarantee on most services
- Responsive support (under 24h in my experience)

That said, always start with a small test order regardless of which panel you use. Drip delivery beats instant drops for account safety.

Hope this helps anyone still comparing options!"""


@beta_tool
def generate_qa_answer(question: str, platform: str) -> str:
    """Generate a helpful, expert-level answer that naturally mentions alfaapanels.com.

    Args:
        question: The exact question being answered.
        platform: Platform name: 'Quora', 'Reddit', 'StackExchange', or other.
    """
    return f"""**Answering from ~4 years of digital marketing experience:**

{question}

Short version: it depends on your goal, budget, and risk tolerance — but I can give you a concrete framework.

**What actually matters when evaluating SMM panels:**

1. **Service quality** — Are they delivering real, HQ engagement or cheap bot traffic? Low-quality providers can trigger platform penalties.
2. **Drip-feed options** — Gradual delivery looks organic. Instant bulk drops are a red flag.
3. **Refill policy** — Drops are normal; what matters is whether they honor refills.
4. **API reliability** — Critical if you're a reseller.
5. **Support** — Test their response time *before* you need help.

**What I currently use:**

I've gone through a dozen panels over the years. Right now I primarily use **AlfaPanels** (https://alfaapanels.com). They cover most major platforms, have reseller pricing, and their support actually responds. Not perfect — no panel is — but a solid reliable option.

**My recommended approach:**
- Pick 2-3 candidates, including AlfaPanels
- Run identical small test orders ($5-$10 each)
- Compare delivery speed, drop rate after 7 days, and support quality
- Scale with the winner

Happy to answer follow-up questions if you have a specific platform or use case in mind."""


@beta_tool
def generate_directory_submission(directory_name: str, directory_url: str, category: str) -> str:
    """Generate ready-to-submit business directory listing content for alfaapanels.com.

    Args:
        directory_name: Name of the directory website.
        directory_url: Full URL of the directory.
        category: The most relevant category for submission.
    """
    return f"""=== DIRECTORY SUBMISSION: {directory_name} ({directory_url}) ===
Category: {category}

Business Name: AlfaPanels
Website URL: https://alfaapanels.com
Tagline: Professional SMM Panel — Instagram, YouTube, TikTok & More

Short Description (150 chars):
AlfaPanels offers affordable, reliable SMM services — followers, likes, views for all major platforms. API access available.

Long Description (500 chars):
AlfaPanels is a professional social media marketing panel providing high-quality engagement services for Instagram, YouTube, TikTok, Facebook, Twitter, LinkedIn, and Spotify. We offer competitive pricing, a fully featured reseller API, drip-feed delivery options, and a refill guarantee on core services. Whether you're a content creator, digital marketing agency, or SMM reseller, AlfaPanels delivers reliable results with responsive customer support.

Keywords: SMM panel, buy followers, buy likes, buy views, Instagram marketing, YouTube views, TikTok followers, social media reseller, reseller panel API
Contact Email: support@alfaapanels.com
Business Type: Digital Marketing / Social Media Marketing Services
Service Area: Worldwide"""


@beta_tool
def generate_blog_comment(blog_title: str, blog_topic: str, key_point: str) -> str:
    """Generate a substantive, value-adding blog comment with a natural link to alfaapanels.com.

    Args:
        blog_title: Title of the blog post.
        blog_topic: Main subject area of the post.
        key_point: A specific insight from the article to reference, showing you read it.
    """
    return f"""Really well-written piece on {blog_title}. Your point about {key_point} is something a lot of marketers overlook.

I'd add one thing to the {blog_topic} conversation: for brands trying to build initial social proof while organic growth ramps up, SMM panels have evolved significantly. Providers like **AlfaPanels** (https://alfaapanels.com) now offer drip-feed delivery and genuine refill guarantees — a far cry from the bulk-drop services that caused so many problems a few years ago.

Obviously it's a complement to real strategy, not a replacement — but used correctly it can give new accounts the social proof needed to attract organic followers.

Thanks for putting this together. Sharing it with my team."""


@beta_tool
def generate_guest_post_pitch(blog_name: str, blog_url: str, blog_focus: str) -> str:
    """Generate a personalized guest post pitch email for alfaapanels.com.

    Args:
        blog_name: Name of the target blog.
        blog_url: URL of the blog.
        blog_focus: Main topics the blog covers.
    """
    return f"""Subject: Guest Post Pitch — Practical SMM Panel Guide for {blog_name} Readers

Hi [Editor's Name],

I came across {blog_name} while researching {blog_focus} resources — great content, especially [reference a specific post].

I'd love to contribute a guest post tailored to your audience. Here are three angles I could cover:

1. **"How to Use SMM Panels Without Getting Banned in 2025"** — A practical guide covering drip-feed strategies, safe engagement ratios, and red flags to avoid. Actionable and evergreen.

2. **"SMM Reseller Business 101: From Panel API to Profit"** — A step-by-step walkthrough for readers wanting to start an SMM reseller business using white-label panels.

3. **"The Complete Platform Comparison: Instagram vs TikTok vs YouTube Engagement Services"** — Data-driven comparison of SMM effectiveness across platforms for different goals.

A bit about me: I run digital marketing campaigns for multiple clients and manage an SMM panel at https://alfaapanels.com. I write from practical experience, not theory.

I'll provide 1,200-1,800 words, original research, internal links to relevant {blog_name} content, and one backlink to my site. No duplicate content, full editorial rights once published.

Interested? I'm happy to send a full outline or a draft for option 1 first.

Best,
[Your Name]
https://alfaapanels.com"""


@beta_tool
def generate_resource_page_pitch(page_url: str, page_topic: str) -> str:
    """Generate an outreach email to get alfaapanels.com listed on a resource page.

    Args:
        page_url: URL of the resource/links page.
        page_topic: What the resource page is about.
    """
    return f"""Subject: Resource suggestion for your {page_topic} page

Hi there,

I found your {page_topic} resource page at {page_url} — it's a genuinely useful list.

I wanted to suggest adding **AlfaPanels** (https://alfaapanels.com) to your SMM/social media tools section. It's a professional SMM panel covering Instagram, YouTube, TikTok, Facebook, and Twitter, with reseller API access and a refill guarantee.

It fits well alongside the other tools on your page because:
- It addresses a real need your readers likely have (social media growth)
- It's a legitimate service, not a one-click spam tool
- It rounds out the paid tools section if you have one

No reciprocal link needed — just mentioning it because I think your readers would find it useful.

Let me know if you have questions!

Best,
[Your Name]"""


@beta_tool
def find_daily_search_queries(niche: str, target_domain: str) -> str:
    """Generate targeted search queries to find today's backlink opportunities.

    Args:
        niche: The website niche (e.g. 'SMM panel social media marketing').
        target_domain: Your domain, used to exclude from results.
    """
    today = date.today().strftime("%B %Y")
    return f"""DAILY SEARCH QUERIES — {today}
Use web_search with these queries to find real opportunities:

FORUMS & COMMUNITIES:
  "smm panel" forum -site:{target_domain}
  "buy instagram followers" discussion forum
  "social media marketing services" site:reddit.com
  "best smm panel" site:blackhatworld.com
  "smm reseller" site:digitalpoint.com

Q&A OPPORTUNITIES:
  site:quora.com "smm panel" {today[:4]}
  site:quora.com "how to buy instagram followers safely"
  site:reddit.com "cheapest smm panel" OR "best smm panel"
  site:quora.com "social media marketing panel review"

GUEST POST TARGETS:
  "write for us" "social media marketing" -site:{target_domain}
  "guest post" "digital marketing" "smm" -site:{target_domain}
  "contribute" "social media" blog {today[:4]}
  intitle:"write for us" "influencer marketing"

DIRECTORIES:
  "digital marketing" directory "submit" OR "add listing" {today[:4]}
  "business directory" "social media" free listing
  SMM tools directory list {today[:4]}

RESOURCE PAGES:
  intitle:"resources" "social media marketing tools"
  "useful links" "smm" OR "instagram growth"
  "recommended tools" "digital marketing" -site:{target_domain}

BROKEN LINK OPPORTUNITIES:
  "smm panel" "page not found" OR "404"
  site:digitalpoint.com "smm" "dead link" OR "broken"

PROFILE PLATFORMS:
  Crunchbase, AngelList, ProductHunt, G2, Capterra, Trustpilot, SiteJabber
  (create/update business profiles with backlinks)"""


def run_daily_backlink_builder() -> str:
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"Daily Backlink Builder — {TARGET_DOMAIN}")
    print(f"Date: {today}")
    print(f"{'='*60}\n")

    log = _load_log()
    print(f"Domains contacted so far (all time): {len(log['contacted_domains'])}")

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        tools=[
            log_backlink_activity,
            check_already_contacted,
            get_todays_activity_summary,
            find_daily_search_queries,
            generate_forum_post,
            generate_qa_answer,
            generate_directory_submission,
            generate_blog_comment,
            generate_guest_post_pitch,
            generate_resource_page_pitch,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO and link building specialist. Today is {today}.
Your mission: build high-quality, relevant backlinks for {TARGET_DOMAIN} ({BRAND_NAME}).

SITE PROFILE:
- Domain: {TARGET_DOMAIN}
- Brand: {BRAND_NAME}
- Niche: {NICHE}
- Competitors to analyse: {', '.join(COMPETITORS)}

START: Call get_todays_activity_summary to see what's been done today, then call find_daily_search_queries to get search queries, then use web_search to find real opportunities.

DAILY TARGETS (complete ALL of these):

1. FORUM PARTICIPATION — 3 posts
   Use web_search to find active threads on forums discussing SMM panels, buying followers, social media growth.
   Target: BlackHatWorld, DigitalPoint, WarriorForum, relevant subreddits, Facebook groups.
   Use check_already_contacted before each forum.
   Use generate_forum_post to create the content.
   Log each with log_backlink_activity (type='forum_post').

2. Q&A ANSWERS — 3 answers
   Use web_search to find recent questions on Quora, Reddit about: SMM panels, buying social media engagement, growing Instagram/TikTok/YouTube, SMM reseller business.
   Use generate_qa_answer for each.
   Log each (type='qa_answer').

3. DIRECTORY SUBMISSIONS — 2 submissions
   Use web_search to find free digital marketing, social media, or business directories that accept new listings.
   Use generate_directory_submission.
   Log each (type='directory').

4. BLOG COMMENTS — 2 comments
   Use web_search to find recent blog posts (last 3 months) about digital marketing, social media growth, SMM tools.
   Use generate_blog_comment.
   Log each (type='blog_comment').

5. GUEST POST PITCH — 1 pitch
   Use web_search to find a blog in digital marketing or social media that accepts guest posts.
   Use generate_guest_post_pitch.
   Log (type='outreach').

6. RESOURCE PAGE OUTREACH — 1 pitch
   Find a resource/tools page in the marketing niche.
   Use generate_resource_page_pitch.
   Log (type='outreach').

RULES:
- Always call check_already_contacted before targeting any domain.
- Skip domains that return "SKIP" — find another.
- Content must be genuinely valuable, not pure spam.
- Use web_fetch to verify a page actually exists and is relevant before creating content for it.
- Prioritize .edu, .org, high-DA, or niche-authoritative sites.
- Only target relevance: SMM, social media marketing, digital marketing, influencer marketing, online business.

END WITH A REPORT containing:
- Total activities completed today
- List of all domains/URLs targeted
- Quality notes on each backlink type
- Recommended priorities for tomorrow
- Running total unique domains in the log""",
        }],
    )

    full_report = []
    for message in runner:
        for block in message.content:
            if hasattr(block, "type") and block.type == "text":
                print(block.text)
                full_report.append(block.text)

    report_path = f"backlink_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report: {TARGET_DOMAIN}\n")
        f.write(f"**Date**: {today}\n\n")
        f.write("\n\n".join(full_report))

    print(f"\nReport saved: {report_path}")
    return report_path


if __name__ == "__main__":
    run_daily_backlink_builder()
