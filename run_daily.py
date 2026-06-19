"""
Daily runner for Alfaa Panels off-page SEO backlink agent.
Runs the SEO analysis and saves a dated report to reports/.
"""
import os
import sys
from datetime import date
from offpage_seo_agent import run_offpage_seo_agent

TODAY = date.today().isoformat()

os.makedirs("reports", exist_ok=True)

DOMAIN = "alfaapanels.com"
BRAND = "Alfaa Panels"
NICHE = "sandwich panel manufacturer PUF PIR insulated panels cold room clean room India"
COMPETITORS = [
    "kingspan.com",
    "metecno.in",
    "industrialfoams.com",
    "lloydinsulations.com",
    "tatabluescopesteel.com",
]

if __name__ == "__main__":
    report_path = f"reports/seo_report_{TODAY}.md"
    if os.path.exists(report_path):
        print(f"Report for {TODAY} already exists: {report_path}")
        sys.exit(0)

    run_offpage_seo_agent(
        your_domain=DOMAIN,
        brand_name=BRAND,
        niche=NICHE,
        competitors=COMPETITORS,
    )

    # rename the generic report to a dated one
    generic = f"seo_report_{DOMAIN.replace('.', '_')}.md"
    if os.path.exists(generic):
        os.rename(generic, report_path)
        print(f"Report saved to: {report_path}")
