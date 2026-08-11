"""Daily runner for the Alfaa Panels off-page SEO agent."""
import os
import sys
from datetime import date
from offpage_seo_agent import run_offpage_seo_agent, ALFAA_CONFIG


def main():
    today = date.today().isoformat()
    print(f"Running daily off-page SEO agent for alfaapanels.com — {today}")

    report_path, report_sections = run_offpage_seo_agent(
        config=ALFAA_CONFIG,
        report_date=today,
    )

    print(f"\nDaily run complete. Report: {report_path}")
    return report_path


if __name__ == "__main__":
    main()
