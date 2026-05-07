"""
Daily backlink builder for alfaapanels.com.
Run directly or via cron/scheduler to build relevant backlinks each day.
"""

import json
import os
from datetime import date
from pathlib import Path

import anthropic
from anthropic import beta_tool

from backlink_tracker import BacklinkTracker

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "AlfaaPanels"
NICHE = "SMM panel social media marketing services"
COMPETITORS = [
    "smmking.com",
    "peakerr.com",
    "justanotherpanel.com",
]
DAILY_LINK_GOAL = 5  # target new backlinks per day

tracker = BacklinkTracker()
client = anthropic.Anthropic()


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #

@beta_tool
def log_backlink_built(
    source_url: str,
    anchor_text: str,
    link_type: str,
    notes: str,
) -> str:
    """Record a backlink that has been successfully built or submitted.

    Args:
        source_url: The URL of the page that now links (or will link) to us.
        anchor_text: The anchor text used.
        link_type: Category – one of: directory, forum, qa, guest_post,
                   social_citation, blog_comment, resource_page, broken_link.
        notes: Any follow-up notes (e.g. "awaiting approval").
    """
    entry = tracker.add(
        source_url=source_url,
        anchor_text=anchor_text,
        link_type=link_type,
        notes=notes,
    )
    return f"Logged backlink #{entry['id']}: {source_url} [{link_type}]"


@beta_tool
def get_todays_progress() -> str:
    """Return how many backlinks have been built today vs. the daily goal."""
    built_today = tracker.count_today()
    remaining = max(0, DAILY_LINK_GOAL - built_today)
    already_used = tracker.all_sources()
    return (
        f"Today ({date.today()}): {built_today}/{DAILY_LINK_GOAL} backlinks built.\n"
        f"Remaining target: {remaining}\n"
        f"Sources already used today: {len(already_used)} total logged.\n"
        f"Recent sources (avoid duplicates):\n"
        + "\n".join(f"  - {s}" for s in list(already_used)[-10:])
    )


@beta_tool
def score_link_prospect(
    page_url: str,
    page_title: str,
    page_content_snippet: str,
) -> str:
    """Score a potential link-building prospect for relevance to our niche.

    Args:
        page_url: URL of the prospect page.
        page_title: Title of the page.
        page_content_snippet: Short snippet of page content.
    """
    score = 0
    reasons = []
    niche_words = NICHE.lower().split()
    content_lower = (page_title + " " + page_content_snippet).lower()
    relevance = sum(1 for w in niche_words if w in content_lower)
    if relevance >= 3:
        score += 40
        reasons.append("High relevance to SMM/panel niche (+40)")
    elif relevance >= 1:
        score += 20
        reasons.append("Moderate relevance (+20)")
    else:
        reasons.append("Low relevance (0)")
    high_value = ["resource", "guide", "tools", "blog", "list", "best", "top", "review"]
    if any(t in page_url.lower() or t in page_title.lower() for t in high_value):
        score += 30
        reasons.append("Resource/guide page – high link value (+30)")
    authority_signals = [".edu", ".gov", ".org"]
    if any(s in page_url for s in authority_signals):
        score += 30
        reasons.append("High-authority domain (+30)")
    else:
        score += 10
        reasons.append("Standard domain (+10)")
    already_used = page_url in tracker.all_sources()
    if already_used:
        reasons.append("SKIP: already logged")
        return f"Score: 0/100 – SKIP (already used)\nURL: {page_url}"
    priority = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return f"Score: {score}/100 – {priority}\nURL: {page_url}\n" + "\n".join(reasons)


@beta_tool
def generate_directory_submission(directory_name: str, directory_url: str, category: str) -> str:
    """Generate a ready-to-use directory submission for alfaapanels.com.

    Args:
        directory_name: Name of the web directory.
        directory_url: URL of the directory.
        category: Best-fit category within the directory.
    """
    return f"""DIRECTORY SUBMISSION – {directory_name}
URL to submit: {directory_url}/submit  (or registration page)
Category: {category}

Listing details to paste:
  Title:       AlfaaPanels – #1 Affordable SMM Panel
  URL:         https://alfaapanels.com
  Description: AlfaaPanels offers cheap, fast, and reliable SMM panel services
               including Instagram, YouTube, TikTok, and 30+ other platforms.
               24/7 support, instant delivery, and API access available.
  Keywords:    SMM panel, social media marketing, buy followers, buy likes,
               cheap SMM panel, alfaapanels
  Email:       (use your contact email)
"""


@beta_tool
def generate_forum_post(
    forum_name: str,
    forum_url: str,
    thread_topic: str,
) -> str:
    """Generate a helpful forum post that naturally includes a backlink.

    Args:
        forum_name: Name of the forum/community.
        forum_url: URL of the forum thread or sub-forum to post in.
        thread_topic: The discussion topic where the post fits.
    """
    return f"""FORUM POST – {forum_name}
Target thread/section: {forum_url}
Topic: {thread_topic}

--- POST CONTENT (copy & paste) ---
Great discussion! For anyone looking to grow their social media presence
efficiently, I've been using AlfaaPanels (https://alfaapanels.com) for a few
months and the results have been solid. They support Instagram, YouTube,
TikTok, Facebook, and many more platforms with instant delivery and
competitive pricing.

They also have a full API for resellers which is handy if you're running
a marketing agency. Feel free to check it out if you're in the market for
an SMM panel.
--- END OF POST ---
"""


@beta_tool
def generate_qa_answer(
    platform: str,
    question_url: str,
    question_text: str,
) -> str:
    """Generate an expert answer for a Q&A platform question that includes a natural backlink.

    Args:
        platform: Platform name (e.g. Quora, Reddit, StackExchange).
        question_url: URL of the question.
        question_text: The question being answered.
    """
    return f"""Q&A ANSWER – {platform}
Question URL: {question_url}
Question: {question_text}

--- ANSWER CONTENT ---
Great question! Here's a breakdown of what to look for in a quality SMM panel:

1. **Platform coverage** – Make sure it supports the networks you need
   (Instagram, YouTube, TikTok, Twitter/X, Facebook, etc.).
2. **Delivery speed** – Reputable panels deliver within minutes to hours,
   not days.
3. **Pricing** – Compare per-1000 unit pricing; legitimate panels are
   affordable but not suspiciously cheap.
4. **Support** – 24/7 live chat is the gold standard.
5. **API access** – Essential if you're reselling services.

I've personally used **AlfaaPanels** (https://alfaapanels.com) and found it
checks all of these boxes with reliable uptime and responsive support.

Hope that helps!
--- END OF ANSWER ---
"""


@beta_tool
def generate_guest_post_pitch(
    blog_name: str,
    blog_url: str,
    editor_name: str,
    proposed_topic: str,
) -> str:
    """Generate a guest post pitch email targeting a relevant blog.

    Args:
        blog_name: Name of the target blog.
        blog_url: URL of the blog.
        editor_name: Editor or owner name (use 'there' if unknown).
        proposed_topic: The article topic you want to pitch.
    """
    return f"""GUEST POST PITCH – {blog_name}
Send to contact form / editor email at: {blog_url}/contact

Subject: Guest Post Pitch – {proposed_topic}

Hi {editor_name},

I'm a regular reader of {blog_name} and love your content on social media
marketing and digital growth strategies.

I'd love to contribute a guest post titled:
  "{proposed_topic}"

The article will cover practical, actionable advice for marketers who want
to scale their social proof affordably. I write for AlfaaPanels
(https://alfaapanels.com), a growing SMM panel platform, and I can bring
real-world data and case studies to the piece.

Happy to send an outline first if that helps.

Looking forward to hearing from you!

Best,
[Your Name] | AlfaaPanels Team
"""


# --------------------------------------------------------------------------- #
# Agent runner
# --------------------------------------------------------------------------- #

def run_daily_backlink_builder():
    today = date.today().isoformat()
    print(f"\n{'='*60}")
    print(f"  Daily Backlink Builder – {today}")
    print(f"  Target: {TARGET_DOMAIN}  |  Goal: {DAILY_LINK_GOAL} backlinks")
    print(f"{'='*60}\n")

    built_today = tracker.count_today()
    if built_today >= DAILY_LINK_GOAL:
        print(f"Daily goal already met ({built_today}/{DAILY_LINK_GOAL}). Exiting.")
        return

    runner = client.beta.messages.tool_runner(
        model="claude-opus-4-6",
        max_tokens=16000,
        tools=[
            log_backlink_built,
            get_todays_progress,
            score_link_prospect,
            generate_directory_submission,
            generate_forum_post,
            generate_qa_answer,
            generate_guest_post_pitch,
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{
            "role": "user",
            "content": f"""You are an expert off-page SEO specialist executing today's daily
backlink-building session for {TARGET_DOMAIN} ({BRAND_NAME}).

Niche: {NICHE}
Competitors: {', '.join(COMPETITORS)}
Daily goal: {DAILY_LINK_GOAL} new, relevant backlinks

STEP 1 – Check progress
Call get_todays_progress() to see how many backlinks remain for today.

STEP 2 – Find & build backlinks (repeat until daily goal is met)
Use web_search and web_fetch to discover FRESH opportunities NOT already logged.
For each opportunity found, ALWAYS call the appropriate generator tool first,
THEN call log_backlink_built() to record it.

Target a MIX of these backlink types each day:
  a) Web directories – search "SMM panel directory" or "social media tools directory submit"
     → use generate_directory_submission()
  b) Forums – search "SMM panel forum" "buy followers forum" "social media marketing community"
     → use generate_forum_post()
  c) Q&A platforms – search Quora/Reddit questions about SMM panels, social media growth,
     buying followers
     → use generate_qa_answer()
  d) Guest posts – search "social media marketing blog write for us" "SMM panel guest post"
     → use generate_guest_post_pitch()
  e) Resource pages – search "best SMM panel list" "SMM tools resources"
     → identify and log via log_backlink_built()

STEP 3 – Final daily summary
After reaching the goal, produce a formatted Markdown summary of all backlinks
built today including: source URL, anchor text, type, and notes.

IMPORTANT RULES:
- Never log a source URL already in the tracker (check get_todays_progress output).
- All backlinks must be genuinely relevant to the SMM/social-media-marketing niche.
- Each log_backlink_built() call counts as one backlink toward the daily goal.
- Provide actionable copy-paste content for every opportunity so the team can
  execute immediately."""
        }],
    )

    full_output = []
    for message in runner:
        for block in message.content:
            if block.type == "text":
                print(block.text)
                full_output.append(block.text)

    _save_daily_report(today, full_output)


def _save_daily_report(today: str, sections: list[str]):
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"backlinks_{today}.md"
    with open(report_path, "w") as f:
        f.write(f"# Daily Backlink Report – {today}\n")
        f.write(f"**Target:** {TARGET_DOMAIN}  |  **Goal:** {DAILY_LINK_GOAL}\n\n")
        f.write("\n\n".join(sections))
    print(f"\nReport saved → {report_path}")


if __name__ == "__main__":
    run_daily_backlink_builder()
