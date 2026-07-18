"""
Off-Page SEO Agent for alfaapanels.com
Performs daily backlink research and opportunity identification.
Uses Anthropic API with web_search and web_fetch built-in tools.
"""

import anthropic
import os
import sys
import datetime

DOMAIN = "alfaapanels.com"
BRAND = "Alfaa Panels"
NICHE = "sandwich panel manufacturer insulated panels PUF PIR rockwool cold room clean room India"
COMPETITORS = ["epack.in", "kingspan.com/in", "alfapebltd.com", "lloydinsulations.com"]


def run_offpage_seo_agent(your_domain: str, brand_name: str, niche: str, competitors: list):
    print(f"\nStarting Off-Page SEO Agent for: {your_domain}\n")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.date.today().isoformat()

    messages = [{
        "role": "user",
        "content": f"""You are an expert off-page SEO strategist. Today is {today}.
Perform a complete off-page SEO backlink-building analysis for: {your_domain}

Brand name: {brand_name}
Niche: {niche}
Competitors: {', '.join(competitors)}

Execute these tasks using web search and web fetch:

TASK 1 - Brand Mention Audit
Search for "{brand_name}" unlinked mentions and citation opportunities.
Search query: "{brand_name}" -site:{your_domain}

TASK 2 - Competitor Backlink Research
For each competitor, find sites that link to them (construction directories,
industry blogs, B2B portals, supplier listings) that could also link to {your_domain}.

TASK 3 - Link Building Opportunities
Find resource pages, guest post opportunities, industry directories, and broken
links in the sandwich panel / insulated panel / cold room / clean room niche in India.
Look for:
- Construction and building material directories in India
- Industrial supply portals and B2B marketplaces
- Architecture and engineering blogs/resource pages
- Cold chain and food processing industry sites
- Pharmaceutical and cleanroom industry portals
- Green building / GRIHA / BIS certification resource sites

TASK 4 - Outreach Templates
Generate personalized email outreach templates for the top 3 highest-priority prospects found.

TASK 5 - Final Report
Create a prioritized 30-day off-page SEO action plan with specific URLs, contact info
where findable, and estimated link value for each opportunity.

Format the final output as a well-structured markdown report with clear sections.
Be specific — include actual URLs you found, not generic advice."""
    }]

    full_report = []
    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8000,
            tools=[
                {"type": "web_search_20260209", "name": "web_search"},
                {"type": "web_fetch_20260209", "name": "web_fetch"},
            ],
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                full_report.append(text)
    except Exception as e:
        print(f"\nStreaming failed: {e}. Trying non-streaming...")
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=8000,
            tools=[
                {"type": "web_search_20260209", "name": "web_search"},
                {"type": "web_fetch_20260209", "name": "web_fetch"},
            ],
            messages=messages,
        )
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)
                full_report.append(block.text)

    print()
    report_filename = f"seo_report_{your_domain.replace('.', '_')}_{today}.md"
    with open(report_filename, "w") as f:
        f.write(f"# Off-Page SEO Backlink Report: {your_domain}\n")
        f.write(f"**Date:** {today}\n\n")
        f.write("".join(full_report))
    print(f"\nReport saved to: {report_filename}")
    return report_filename


if __name__ == "__main__":
    run_offpage_seo_agent(
        your_domain=DOMAIN,
        brand_name=BRAND,
        niche=NICHE,
        competitors=COMPETITORS,
    )
