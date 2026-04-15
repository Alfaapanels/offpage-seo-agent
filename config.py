# Configuration for alfaapanels.com daily backlink building

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "solar panels, solar energy, renewable energy, photovoltaic systems",
    "target_keywords": [
        "solar panels",
        "solar energy systems",
        "photovoltaic panels",
        "solar power installation",
        "residential solar panels",
        "commercial solar panels",
        "solar panel supplier",
        "solar energy solutions",
        "monocrystalline solar panels",
        "polycrystalline solar panels",
    ],
    "competitors": [
        "sunpower.com",
        "canadiansolar.com",
        "jinko-solar.com",
        "longi-solar.com",
        "q-cells.com",
    ],
    "target_countries": ["US", "UK", "AU", "CA", "DE"],
    "report_output_dir": "reports",
    "tracker_file": "backlink_tracker.json",
}

# Daily task rotation — each day of the week focuses on a different strategy
DAILY_TASK_ROTATION = {
    0: {  # Monday
        "name": "Directory & Citation Building",
        "description": "Submit alfaapanels.com to high-authority business directories, solar energy directories, and local citation sites.",
        "strategies": [
            "Submit to general business directories (Google My Business, Yelp, Bing Places, Yellow Pages)",
            "Submit to solar/renewable energy specific directories",
            "Submit to industry association directories",
            "Create/update social profiles with backlinks (LinkedIn, Twitter/X, Facebook, YouTube)",
        ],
    },
    1: {  # Tuesday
        "name": "Guest Post Prospecting",
        "description": "Find and reach out to solar/renewable energy blogs and websites for guest posting opportunities.",
        "strategies": [
            'Search Google for: "solar energy" "write for us" OR "guest post"',
            'Search for: "renewable energy blog" "contribute" OR "submit article"',
            "Find top solar energy blogs via web search",
            "Identify editors/webmasters and generate personalized outreach emails",
        ],
    },
    2: {  # Wednesday
        "name": "Broken Link Building",
        "description": "Find broken links on solar/energy resource pages and offer alfaapanels.com as a replacement.",
        "strategies": [
            'Find resource pages: "solar panels" intitle:"resources" OR "useful links"',
            "Check for 404 links on competitor resource pages",
            "Generate outreach emails for broken link replacements",
        ],
    },
    3: {  # Thursday
        "name": "Brand Mention Conversion",
        "description": "Find unlinked brand mentions of Alfa Panels and convert them to followed backlinks.",
        "strategies": [
            'Search: "Alfa Panels" -site:alfaapanels.com',
            'Search: "alfaapanels" -site:alfaapanels.com',
            "Categorize each mention (positive/negative, linked/unlinked)",
            "Generate outreach for unlinked positive mentions",
        ],
    },
    4: {  # Friday
        "name": "Competitor Backlink Gap Analysis",
        "description": "Analyse which sites link to competitors but not to alfaapanels.com and build a target list.",
        "strategies": [
            "Find who links to sunpower.com, canadiansolar.com, jinko-solar.com",
            "Score each prospect for relevance and authority",
            "Build prioritised outreach list",
            "Generate personalised pitch emails for top 5 prospects",
        ],
    },
    5: {  # Saturday
        "name": "Forum & Community Engagement",
        "description": "Engage in solar/energy forums, Q&A sites, and Reddit threads with helpful answers + natural backlinks.",
        "strategies": [
            "Find active solar/renewable energy forums and communities",
            "Search Reddit for relevant solar discussions",
            "Find Quora questions about solar panels to answer",
            "Identify Stack Exchange / home improvement Q&A opportunities",
        ],
    },
    6: {  # Sunday
        "name": "Content & Resource Link Earning",
        "description": "Identify content gaps and resource page opportunities; suggest linkable asset ideas for alfaapanels.com.",
        "strategies": [
            'Find resource pages: "solar energy" inurl:resources OR inurl:links',
            "Identify skyscraper content opportunities",
            "Find infographic/data pages where alfaapanels.com content could earn links",
            "Research trending solar topics for linkable content ideas",
        ],
    },
}
