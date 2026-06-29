#!/usr/bin/env python3
"""Daily backlink building runner for alfaapanels.com."""

import datetime
import os
import sys
from offpage_seo_agent import run_offpage_seo_agent

DATE = datetime.date.today().isoformat()
REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)

DOMAIN = "alfaapanels.com"
BRAND = "Alfaa Panels"
NICHE = "aluminium composite panels ACP cladding building facade panels"
COMPETITORS = [
    "alucobond.com",
    "reynobond.com",
    "vivaacp.com",
    "alpolymeric.com",
]

if __name__ == "__main__":
    print(f"Running daily backlink builder for {DOMAIN} — {DATE}")
    run_offpage_seo_agent(
        your_domain=DOMAIN,
        brand_name=BRAND,
        niche=NICHE,
        competitors=COMPETITORS,
    )
    # Move generated report into dated reports directory
    src = f"seo_report_{DOMAIN.replace('.', '_')}.md"
    dst = os.path.join(REPORT_DIR, f"seo_report_{DATE}.md")
    if os.path.exists(src):
        os.rename(src, dst)
        print(f"Report saved: {dst}")
