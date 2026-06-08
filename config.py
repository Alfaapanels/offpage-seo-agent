"""
Site configuration for alfaapanels.com daily backlink builder.
"""

SITE_CONFIG = {
    "domain": "alfaapanels.com",
    "brand_name": "Alfa Panels",
    "niche": "aluminum composite panels ACP cladding building facade materials",
    "description": (
        "Alfa Panels manufactures and supplies high-quality aluminum composite panels (ACP), "
        "facade cladding systems, and architectural building materials for construction projects."
    ),
    "target_keywords": [
        "aluminum composite panels",
        "ACP panels",
        "facade cladding",
        "building cladding systems",
        "architectural panels",
        "aluminum cladding",
        "exterior wall cladding",
        "composite facade panels",
        "ACP sheet",
        "building facade materials",
        "aluminum panel manufacturer",
        "cladding supplier",
        "sandwich panels",
        "PVDF coated panels",
        "fire retardant ACP",
    ],
    "competitors": [
        "alucobond.com",
        "reynobond.com",
        "alpolic.com",
        "alucoworld.com",
        "vbq-panels.com",
    ],
    "target_countries": ["UAE", "Saudi Arabia", "India", "USA", "UK", "Australia"],
    "contact_email": "info@alfaapanels.com",
}

# Backlink strategy rotation (7-day cycle)
DAILY_STRATEGIES = {
    0: {  # Monday
        "name": "Business Directory Submissions",
        "description": "Submit alfaapanels.com to high-authority business and niche directories",
        "focus": "directory",
        "target_count": 10,
        "search_queries": [
            'site:dir.* "aluminum panels" OR "ACP panels" submit listing',
            '"building materials" directory submit business free listing',
            '"construction suppliers" directory "add your business"',
            'UAE building materials supplier directory free submission',
            '"aluminum composite" manufacturer directory list',
        ],
    },
    1: {  # Tuesday
        "name": "Forum & Community Participation",
        "description": "Contribute valuable answers on forums related to construction and building materials",
        "focus": "forum",
        "target_count": 8,
        "search_queries": [
            '"aluminum composite panels" forum discussion site:reddit.com OR site:quora.com',
            '"ACP panels" OR "facade cladding" questions forum architecture',
            '"building materials" forum "aluminum panels" recommendation',
            'construction forum "exterior cladding" advice thread',
            '"panel installation" forum discussion wall cladding',
        ],
    },
    2: {  # Wednesday
        "name": "Resource Page Link Building",
        "description": "Find resource pages in construction niche and pitch alfaapanels.com as a resource",
        "focus": "resource",
        "target_count": 8,
        "search_queries": [
            'inurl:resources "aluminum composite panels" OR "ACP" building',
            '"useful resources" "building materials" OR "facade" construction',
            '"links" OR "resources" page architectural materials cladding',
            '"recommended suppliers" building construction materials page',
            'intitle:"resources" "cladding" OR "aluminum panels" architecture',
        ],
    },
    3: {  # Thursday
        "name": "Guest Post Outreach",
        "description": "Find blogs and publications accepting guest posts in construction, architecture, and building materials",
        "focus": "guest_post",
        "target_count": 6,
        "search_queries": [
            '"write for us" "building materials" OR "construction" OR "architecture"',
            '"guest post" "exterior cladding" OR "aluminum panels" blog',
            '"contribute" "architecture" blog building design materials',
            '"submit article" construction industry magazine',
            '"guest author" "building facade" OR "cladding systems"',
        ],
    },
    4: {  # Friday
        "name": "Broken Link Building",
        "description": "Find broken links on construction and architecture sites to replace with alfaapanels.com content",
        "focus": "broken_link",
        "target_count": 8,
        "search_queries": [
            '"aluminum composite panels" manufacturer site:* -alfaapanels.com inurl:resources',
            '"ACP panels supplier" resources architecture blog',
            '"building materials" supplier page "404" OR broken link construction',
            '"cladding systems" resources architectural firms',
            '"facade materials" supplier links architecture education site',
        ],
    },
    5: {  # Saturday
        "name": "Q&A & Social Platforms",
        "description": "Answer questions on Quora, Reddit, and industry Q&A about aluminum panels and cladding",
        "focus": "qa_social",
        "target_count": 10,
        "search_queries": [
            'site:quora.com "aluminum composite panels" OR "ACP panels" unanswered',
            'site:reddit.com "facade cladding" OR "aluminum panels" building question',
            '"aluminum composite" questions architecture forum',
            '"best ACP panels" recommendations construction forum',
            '"exterior wall cladding" material comparison discussion',
        ],
    },
    6: {  # Sunday
        "name": "Competitor Backlink Gap Analysis",
        "description": "Find sites linking to competitors but not alfaapanels.com and pitch your products",
        "focus": "competitor_gap",
        "target_count": 8,
        "search_queries": [
            f'"alucobond.com" OR "reynobond.com" supplier review construction',
            '"ACP panel" supplier comparison review site',
            '"aluminum composite panel" brand comparison architecture',
            '"facade cladding" manufacturer recommendation blog',
            '"building cladding" supplier review construction blog',
        ],
    },
}
