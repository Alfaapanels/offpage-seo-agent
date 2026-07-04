"""
Daily backlink building runner for alfaapanels.com
Generates a prioritized off-page SEO action report each day.
"""

import datetime
import os
import json


TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfaa Panels"
NICHE = "sandwich panel manufacturer India PUF PIR Rockwool insulation panels"
COMPETITORS = ["epack.in", "rinac.com", "mountroof.com"]

DATE_STR = datetime.date.today().isoformat()


BRAND_MENTIONS = [
    {
        "source": "quora.com",
        "url": "https://www.quora.com/What-is-a-sandwich-PUF-panel",
        "snippet": "Discussion on sandwich PUF panels without linking to alfaapanels.com",
        "has_link": False,
        "sentiment": "Neutral",
        "action": "Answer the question and mention alfaapanels.com as a reference source",
    },
    {
        "source": "tradeindia.com",
        "url": "https://www.tradeindia.com/blog/top-15-puf-panel-manufacturers/",
        "snippet": "Top PUF Panel Manufacturers in India list – alfaapanels.com may not be included",
        "has_link": False,
        "sentiment": "Neutral",
        "action": "Reach out to TradeIndia editorial team to be included in the Top PUF Panel list with a dofollow link",
    },
    {
        "source": "constructionworld.in",
        "url": "https://www.constructionworld.in/",
        "snippet": "Leading Indian construction publication – no Alfaa Panels mention found",
        "has_link": False,
        "sentiment": "Neutral",
        "action": "Pitch a press release or expert quote article about Alfaa Panels' BIS-certified panels",
    },
]

LINK_PROSPECTS = [
    {
        "url": "https://www.constructionworld.in/",
        "title": "Construction World – India's Premium Construction Magazine",
        "topic": "Industrial construction, building materials, insulation",
        "type": "editorial",
        "score": 92,
        "priority": "HIGH",
        "reasons": [
            "Top-tier Indian construction media (+40)",
            "Covers PUF/insulation panels directly (+30)",
            "High domain authority – .in authority site (+22)",
        ],
        "contact": "editorial@constructionworld.in",
        "link_type": "guest_post",
        "pitch": "Offer an expert article: '5 Things to Check Before Buying PUF Panels in India (2026)'",
    },
    {
        "url": "https://rinac.com/blog/cold-storage-warehouse-india-2026-guide/",
        "title": "Cold Storage Warehouse: Complete Guide – Rinac",
        "topic": "Cold storage construction, insulation panels, warehouse design",
        "type": "resource_page",
        "score": 78,
        "priority": "HIGH",
        "reasons": [
            "Direct niche relevance – cold room panels (+40)",
            "Competitor content = link gap opportunity (+30)",
            "Blog post format accepts supplemental links (+8)",
        ],
        "contact": "info@rinac.com",
        "link_type": "resource",
        "pitch": "Suggest adding alfaapanels.com/product-category/cold-room/ as an additional supplier resource",
    },
    {
        "url": "https://pararthproducts.com/blog/thermal-insulation-materials-in-india-7-best-options-for-2026-complete-buyers-guide/",
        "title": "7 Best Thermal Insulation Materials in India – Buyer's Guide",
        "topic": "Thermal insulation materials India",
        "type": "resource_list",
        "score": 74,
        "priority": "HIGH",
        "reasons": [
            "Buyer's guide – perfect for brand mention link (+40)",
            "Insulation niche match (+30)",
            "2026 content – actively maintained (+4)",
        ],
        "contact": "contact@pararthproducts.com",
        "link_type": "mention",
        "pitch": "Request inclusion of Alfaa Panels (PUF/PIR/Rockwool) as a recommended supplier",
    },
    {
        "url": "https://kishoreindustries.in/cold-storage-construction-using-peb-complete-2026-guide/",
        "title": "Cold Storage Construction Using PEB – Kishore Infratech",
        "topic": "Cold storage PEB construction guide",
        "type": "blog_guide",
        "score": 68,
        "priority": "HIGH",
        "reasons": [
            "Cold storage + PEB niche match (+40)",
            "Guide format – supplier links natural (+20)",
            "2026 active content (+8)",
        ],
        "contact": "info@kishoreindustries.in",
        "link_type": "resource",
        "pitch": "Propose adding Alfaa Panels as a trusted cold room panel supplier reference",
    },
    {
        "url": "https://www.coldroombazaar.com/",
        "title": "Cold Room Bazaar – India's Cold Storage B2B Marketplace",
        "topic": "Cold storage B2B marketplace",
        "type": "directory",
        "score": 65,
        "priority": "MEDIUM",
        "reasons": [
            "Cold room niche – exact match (+40)",
            "Marketplace = business listing backlink (+20)",
            "B2B audience = qualified traffic (+5)",
        ],
        "contact": "support@coldroombazaar.com",
        "link_type": "resource",
        "pitch": "Submit a free supplier listing for Alfaa Panels cold room PUF/PIR panels",
    },
    {
        "url": "https://bmtpc.org/",
        "title": "Building Materials & Technology Promotion Council – Govt of India",
        "topic": "Building materials, insulation, construction standards",
        "type": "government",
        "score": 95,
        "priority": "HIGH",
        "reasons": [
            ".gov.in authority – maximum domain trust (+30)",
            "BIS-certified panels = qualification for listing (+40)",
            "Direct niche match (+25)",
        ],
        "contact": "bmtpc@nic.in",
        "link_type": "resource",
        "pitch": "Apply for BMTPC product registration/listing – Alfaa Panels is BIS certified, making it eligible",
    },
    {
        "url": "https://www.tradeindia.com/manufacturers/sandwich-panels.html",
        "title": "Sandwich Panels Manufacturers – TradeIndia",
        "topic": "B2B manufacturer directory",
        "type": "directory",
        "score": 61,
        "priority": "MEDIUM",
        "reasons": [
            "B2B directory – standard listing backlink (+20)",
            "Sandwich panel category – direct match (+30)",
            "High-traffic source (+11)",
        ],
        "contact": "support@tradeindia.com",
        "link_type": "resource",
        "pitch": "Claim/upgrade Alfaa Panels listing on TradeIndia with website link and product details",
    },
    {
        "url": "https://phoenixxsmartbuild.com/resources/blogs/puf-panel-price-india-cost-per-sq-ft",
        "title": "PUF Panel Price in India 2026 – Phoenixx Smartbuild",
        "topic": "PUF panel pricing guide",
        "type": "blog_resource",
        "score": 58,
        "priority": "MEDIUM",
        "reasons": [
            "Pricing guide – manufacturer mention natural (+30)",
            "PUF niche match (+20)",
            "2026 active content (+8)",
        ],
        "contact": "info@phoenixxsmartbuild.com",
        "link_type": "mention",
        "pitch": "Reach out to be featured as a manufacturer for accurate 2026 pricing data",
    },
]

LINK_GAP_OPPORTUNITIES = [
    {
        "competitor": "epack.in",
        "linking_page": "https://bmtpc.org/DataFiles/CMS/file/PDF_Files/75_Epack_PUF_F.pdf",
        "topic": "BMTPC Technical Report on PUF panels",
        "action": "Submit Alfaa Panels' BIS-certified products to BMTPC for a similar technical evaluation report – creates a high-authority .gov.in backlink",
    },
    {
        "competitor": "rinac.com",
        "linking_page": "https://rinac.com/blog/cold-storage-warehouse-india-2026-guide/",
        "topic": "Cold storage warehouse guide India",
        "action": "Create a competing/complementary resource at alfaapanels.com/cold-storage-construction-guide/ and promote it to the same publisher ecosystem",
    },
    {
        "competitor": "epack.in",
        "linking_page": "https://www.epack.in/ultimate-sandwich-panels-guide-types-applications-benefits",
        "topic": "Ultimate Sandwich Panels Guide",
        "action": "Develop a more comprehensive guide at alfaapanels.com/ultimate-sandwich-panel-guide/ and outreach to all sites currently linking to EPACK's guide",
    },
]

OUTREACH_TEMPLATES = {
    "constructionworld_guest_post": """
Subject: Expert Article Offer – PUF Panel Buying Guide for 2026

Hi Construction World Editorial Team,

I'm reaching out from Alfaa Panels (alfaapanels.com), India's leading sandwich panel manufacturer with 35+ years of experience and 5 fully automated plants across India.

I'd like to contribute an expert article for your readers:

**"5 Things Every Buyer Must Check Before Purchasing PUF Panels in India (2026)"**

This piece would cover:
- BIS certification requirements (we are BIS certified)
- GRIHA-compliant insulation choices
- Cold storage vs. clean room panel selection
- How to evaluate manufacturer capacity and lead times
- Price benchmarks for 2026

This is timely content for your audience planning industrial and cold storage construction projects.

Would you be open to a guest contribution?

Best regards,
[Your Name]
Alfaa Panels | alfaapanels.com
""",

    "bmtpc_listing": """
Subject: Application for BMTPC Product Registration – BIS Certified Sandwich Panels

Dear BMTPC Team,

We are Alfaa Panels (alfaapanels.com), a BIS-certified manufacturer of PUF, PIR, and Rockwool sandwich insulation panels, operating 5 fully automated plants across India (Hosur, Ahmedabad, Raipur, Karnal, Baramati).

We wish to apply for BMTPC product registration/listing to support India's construction standards ecosystem.

Our credentials:
- BIS Certified
- GRIHA Certified
- 15-year product warranty
- Monthly capacity: 10 lakh+ sq meters
- 35+ years industry expertise

Please advise on the registration process or documentation required.

Thank you,
[Your Name]
Alfaa Panels
info@alfaapanels.com
""",

    "paraarth_buyer_guide_mention": """
Subject: Suggestion for Your Thermal Insulation Buyer's Guide

Hi,

I came across your excellent buyer's guide on thermal insulation materials in India. It's a great resource!

I noticed Alfaa Panels isn't listed. We're one of India's largest sandwich panel manufacturers (BIS & GRIHA certified) offering PUF, PIR, and Rockwool panels – exactly the materials your readers are looking for.

Our product page: alfaapanels.com/product-category/all-products/

Would you be open to adding us as a supplier reference? Happy to provide product specs or an exclusive quote for your readers.

Best,
[Your Name]
Alfaa Panels | alfaapanels.com
""",
}

DIRECTORY_SUBMISSIONS = [
    {
        "platform": "IndiaMART",
        "url": "https://dir.indiamart.com/impcat/puf-panel.html",
        "status": "Verify listing exists and is complete with website URL",
        "priority": "HIGH",
    },
    {
        "platform": "TradeIndia",
        "url": "https://www.tradeindia.com/manufacturers/sandwich-panels.html",
        "status": "Claim listing and add alfaapanels.com URL",
        "priority": "HIGH",
    },
    {
        "platform": "Cold Room Bazaar",
        "url": "https://www.coldroombazaar.com/",
        "status": "New listing – submit as cold room panel supplier",
        "priority": "HIGH",
    },
    {
        "platform": "BMTPC (Govt)",
        "url": "https://bmtpc.org/",
        "status": "Apply for BIS-certified product registration",
        "priority": "HIGH",
    },
    {
        "platform": "JustDial",
        "url": "https://www.justdial.com/",
        "status": "Verify business listing is accurate with website link",
        "priority": "MEDIUM",
    },
]


def score_prospects(prospects):
    return sorted(prospects, key=lambda x: x["score"], reverse=True)


def generate_report():
    prospects_sorted = score_prospects(LINK_PROSPECTS)

    lines = []
    lines.append(f"# Off-Page SEO & Backlink Building Report: {TARGET_DOMAIN}")
    lines.append(f"**Date:** {DATE_STR}  |  **Brand:** {BRAND_NAME}  |  **Niche:** Sandwich Panel Manufacturer India\n")

    lines.append("---\n")
    lines.append("## Executive Summary\n")
    lines.append(
        f"Daily backlink building session for **{BRAND_NAME}** ({TARGET_DOMAIN}). "
        f"This report identifies **{len(prospects_sorted)} link building prospects**, "
        f"**{len(BRAND_MENTIONS)} brand mention opportunities**, "
        f"**{len(LINK_GAP_OPPORTUNITIES)} competitor link gap opportunities**, and "
        f"**{len(DIRECTORY_SUBMISSIONS)} directory submission targets**.\n"
    )

    high = [p for p in prospects_sorted if p["priority"] == "HIGH"]
    med = [p for p in prospects_sorted if p["priority"] == "MEDIUM"]
    lines.append(f"- **HIGH priority prospects:** {len(high)}")
    lines.append(f"- **MEDIUM priority prospects:** {len(med)}")
    lines.append(f"- **Competitors analysed:** {', '.join(COMPETITORS)}\n")

    lines.append("---\n")
    lines.append("## Task 1 – Brand Mention Audit\n")
    lines.append(
        "Unlinked brand mentions are link building opportunities – reach out to add a dofollow link to alfaapanels.com.\n"
    )
    for m in BRAND_MENTIONS:
        tag = "UNLINKED MENTION" if not m["has_link"] else "LINKED"
        lines.append(f"### [{tag}] {m['source']}")
        lines.append(f"- **URL:** {m['url']}")
        lines.append(f"- **Snippet:** {m['snippet']}")
        lines.append(f"- **Sentiment:** {m['sentiment']}")
        lines.append(f"- **Action:** {m['action']}\n")

    lines.append("---\n")
    lines.append("## Task 2 – Competitor Link Gap Analysis\n")
    lines.append(
        "Pages that link to competitors but NOT to alfaapanels.com – prime outreach targets.\n"
    )
    for gap in LINK_GAP_OPPORTUNITIES:
        lines.append(f"### {gap['competitor']} → {gap['topic']}")
        lines.append(f"- **Linking page:** {gap['linking_page']}")
        lines.append(f"- **Action:** {gap['action']}\n")

    lines.append("---\n")
    lines.append("## Task 3 – Link Building Prospects (Ranked by Score)\n")
    for i, p in enumerate(prospects_sorted, 1):
        lines.append(f"### #{i} | Score: {p['score']}/100 – {p['priority']}")
        lines.append(f"**{p['title']}**")
        lines.append(f"- **URL:** {p['url']}")
        lines.append(f"- **Type:** {p['type']}")
        lines.append(f"- **Topic:** {p['topic']}")
        lines.append(f"- **Scoring reasons:**")
        for r in p["reasons"]:
            lines.append(f"  - {r}")
        lines.append(f"- **Contact:** {p['contact']}")
        lines.append(f"- **Pitch:** {p['pitch']}\n")

    lines.append("---\n")
    lines.append("## Task 4 – Outreach Email Templates\n")
    for key, template in OUTREACH_TEMPLATES.items():
        lines.append(f"### Template: `{key}`")
        lines.append("```")
        lines.append(template.strip())
        lines.append("```\n")

    lines.append("---\n")
    lines.append("## Task 5 – Directory & Citation Submissions\n")
    lines.append(
        "Consistent NAP (Name, Address, Phone) citations and directory listings build domain authority.\n"
    )
    for d in DIRECTORY_SUBMISSIONS:
        lines.append(f"### {d['platform']} – {d['priority']}")
        lines.append(f"- **URL:** {d['url']}")
        lines.append(f"- **Action:** {d['status']}\n")

    lines.append("---\n")
    lines.append("## Task 6 – 30-Day Prioritised Action Plan\n")
    lines.append(
        "| Week | Action | Target | Expected Outcome |\n"
        "|------|--------|--------|------------------|\n"
        "| Week 1 | BMTPC product registration application | bmtpc.org | High-authority .gov.in link |\n"
        "| Week 1 | Verify & complete IndiaMART listing | indiamart.com | B2B directory backlink + traffic |\n"
        "| Week 1 | Claim TradeIndia listing with website URL | tradeindia.com | B2B directory backlink |\n"
        "| Week 1 | Submit listing to Cold Room Bazaar | coldroombazaar.com | Niche directory backlink |\n"
        "| Week 2 | Pitch guest article to Construction World | constructionworld.in | High-DA editorial backlink |\n"
        "| Week 2 | Outreach to Paraarth Products buyer's guide | pararthproducts.com | Resource page mention + link |\n"
        "| Week 2 | Answer Quora PUF panel questions | quora.com | Community authority + traffic |\n"
        "| Week 3 | Pitch cold storage supplier addition to Rinac guide | rinac.com | Niche resource link |\n"
        "| Week 3 | Outreach to Kishore Infratech cold storage guide | kishoreindustries.in | Niche blog backlink |\n"
        "| Week 3 | Publish competing 'Ultimate Sandwich Panel Guide' on alfaapanels.com | Own site | Link magnet asset |\n"
        "| Week 4 | Promote new guide to sites linking to EPACK's guide | epack.in link sources | Multiple backlinks via skyscraper |\n"
        "| Week 4 | Pitch Phoenixx Smartbuild for pricing guide mention | phoenixxsmartbuild.com | Pricing resource backlink |\n"
        "| Ongoing | Monitor for new unlinked brand mentions weekly | Web | Convert to links |\n"
    )

    lines.append("\n---\n")
    lines.append("## Key Content Assets Needed\n")
    lines.append("These pages should be created/optimised on alfaapanels.com to attract links:\n")
    assets = [
        ("alfaapanels.com/ultimate-sandwich-panel-guide/", "Comprehensive guide to replace EPACK's resource as top link target"),
        ("alfaapanels.com/cold-storage-construction-guide/", "Cold storage construction guide to compete with Rinac's resource page"),
        ("alfaapanels.com/puf-panel-price-india-2026/", "2026 pricing guide – natural link magnet for buyer queries"),
        ("alfaapanels.com/bis-certified-insulation-panels/", "BIS certification page – credibility asset for BMTPC & directories"),
    ]
    for url, desc in assets:
        lines.append(f"- **`{url}`** – {desc}")

    lines.append("\n---")
    lines.append(f"\n*Report generated: {DATE_STR} | Tool: Alfaa Panels Off-Page SEO Agent*")

    return "\n".join(lines)


if __name__ == "__main__":
    report = generate_report()
    filename = f"seo_report_{DATE_STR}.md"
    with open(filename, "w") as f:
        f.write(report)
    print(f"Report saved: {filename}")
    print(f"Prospects found: {len(LINK_PROSPECTS)}")
    print(f"Brand mentions: {len(BRAND_MENTIONS)}")
    print(f"Link gaps: {len(LINK_GAP_OPPORTUNITIES)}")
