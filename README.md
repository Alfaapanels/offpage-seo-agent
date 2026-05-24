# Off-Page SEO Agent — alfaapanels.com

Automatically discovers and builds relevant backlinks for **alfaapanels.com** every day using Claude AI.

## What it does each day

| Task | Description |
|------|-------------|
| Brand Mention Audit | Finds unlinked mentions of "Alfa Panels" and prioritises outreach |
| Competitor Gap Analysis | Spots sites linking to Kingspan / Metecno / Isopan that could link to you |
| Directory Submissions | Drafts ready-to-submit listings for niche and general directories |
| Q&A & Forum Answers | Drafts expert answers for Quora/Reddit questions about sandwich panels |
| Resource Page Outreach | Finds resource pages and generates personalised pitch emails |
| Broken Link Building | Detects outdated links in your niche and pitches your content as a replacement |
| Action Summary | Prioritised list of today's opportunities sorted by impact |

A Markdown report is saved to `reports/seo_report_YYYY-MM-DD.md` after every run.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Run once (today)

```bash
python daily_backlink_builder.py
```

Force re-run if already ran today:

```bash
python daily_backlink_builder.py --force
```

## Run on a daily schedule

```bash
# Runs every day at 08:00 UTC (also runs immediately on startup)
python daily_backlink_builder.py --schedule

# Custom time — 06:30 UTC
python daily_backlink_builder.py --schedule --hour 6 --minute 30
```

## Run with cron (alternative)

```cron
0 8 * * * cd /path/to/offpage-seo-agent && python daily_backlink_builder.py >> seo_agent.log 2>&1
```

## Files

| File | Purpose |
|------|---------|
| `offpage_seo_agent.py` | Core agent with all SEO tools and the Claude runner |
| `daily_backlink_builder.py` | Daily scheduler, tracker, and CLI entry point |
| `backlink_tracker.json` | Auto-generated; tracks every run to avoid duplicates |
| `reports/` | Auto-generated; one Markdown report per day |
| `seo_agent.log` | Auto-generated; structured run log |

## Targets

- **Domain:** alfaapanels.com  
- **Brand:** Alfa Panels  
- **Niche:** Sandwich panels, building materials, construction insulation  
- **Competitors monitored:** kingspan.com, metecno.com, isopan.com, rockwool.com, paroc.com
