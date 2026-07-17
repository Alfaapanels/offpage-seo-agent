"""Daily backlink building run for alfaapanels.com - 2026-07-17"""
import sys
sys.path.insert(0, '/home/user/offpage-seo-agent')
from offpage_seo_agent import run_offpage_seo_agent

run_offpage_seo_agent(
    your_domain="alfaapanels.com",
    brand_name="Alfa Panels",
    niche="aluminum composite panels facade cladding building materials",
    competitors=[
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "dibond.com",
    ]
)
