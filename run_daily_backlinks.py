"""Daily backlink building runner for alfaapanels.com

Requires ANTHROPIC_API_KEY environment variable.
Reports are saved to reports/backlink_report_YYYY-MM-DD.md
"""
import os
from datetime import date
from offpage_seo_agent import run_offpage_seo_agent

TODAY = date.today().isoformat()

DOMAIN = "alfaapanels.com"
BRAND = "Alfaa Panels"
# Alfaa Panels: insulated sandwich panels (PUF, PIR, EPS, Rockwool),
# cold room panels, clean room panels — India's largest manufacturer.
NICHE = (
    "insulated sandwich panels PUF PIR EPS rockwool cold room clean room "
    "prefab industrial building India"
)
COMPETITORS = [
    "epack.in",
    "rinac.com",
    "viraatindustries.com",
    "kingspanjindal.com",
    "bnalprefabs.com",
]

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set. Export it before running this script."
        )
    print(f"Daily Backlink Build: {TODAY} — {DOMAIN}\n")
    run_offpage_seo_agent(
        your_domain=DOMAIN,
        brand_name=BRAND,
        niche=NICHE,
        competitors=COMPETITORS,
    )
    src = f"seo_report_{DOMAIN.replace('.', '_')}.md"
    dst = f"reports/backlink_report_{TODAY}.md"
    os.makedirs("reports", exist_ok=True)
    if os.path.exists(src):
        os.rename(src, dst)
        print(f"\nReport moved to: {dst}")
