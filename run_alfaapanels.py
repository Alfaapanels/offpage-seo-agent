"""Daily off-page SEO backlink builder for alfaapanels.com."""
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from offpage_seo_agent import run_offpage_seo_agent

if __name__ == "__main__":
    date_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Running daily backlink campaign for alfaapanels.com — {date_str}")

    run_offpage_seo_agent(
        your_domain="alfaapanels.com",
        brand_name="Alfa Panels",
        niche="aluminum composite panels architectural cladding building facade panels",
        competitors=[
            "alucobond.com",
            "reynobond.com",
            "alpolic.com",
        ],
    )
