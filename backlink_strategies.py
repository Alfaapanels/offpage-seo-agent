"""
Backlink strategy platform lists and helpers for alfaapanels.com.

Organized by strategy type — used by daily_backlink_builder.py as
reference data for the Claude agent.
"""

TARGET_DOMAIN = "alfaapanels.com"
BRAND_NAME = "Alfa Panels"
NICHE_KEYWORDS = [
    "solar panels",
    "electrical panels",
    "renewable energy",
    "solar energy",
    "photovoltaic panels",
    "panel installation",
    "energy efficiency",
    "solar power systems",
    "green energy",
    "residential solar",
    "commercial solar",
]

# ── Free business directories ────────────────────────────────────────────────

BUSINESS_DIRECTORIES = [
    {"name": "Google Business Profile", "url": "business.google.com", "da": 100, "do_follow": False},
    {"name": "Yelp", "url": "yelp.com/biz_search", "da": 93, "do_follow": False},
    {"name": "Yellow Pages", "url": "yellowpages.com", "da": 89, "do_follow": False},
    {"name": "Bing Places", "url": "bingplaces.com", "da": 96, "do_follow": False},
    {"name": "Foursquare", "url": "foursquare.com", "da": 92, "do_follow": True},
    {"name": "Hotfrog", "url": "hotfrog.com", "da": 63, "do_follow": True},
    {"name": "Manta", "url": "manta.com", "da": 73, "do_follow": True},
    {"name": "EZlocal", "url": "ezlocal.com", "da": 53, "do_follow": True},
    {"name": "Citysearch", "url": "citysearch.com", "da": 67, "do_follow": False},
    {"name": "Superpages", "url": "superpages.com", "da": 75, "do_follow": False},
    {"name": "Angi (Angie's List)", "url": "angi.com", "da": 90, "do_follow": False},
    {"name": "HomeAdvisor", "url": "homeadvisor.com", "da": 88, "do_follow": False},
    {"name": "Better Business Bureau", "url": "bbb.org", "da": 91, "do_follow": True},
    {"name": "Chamber of Commerce", "url": "chamberofcommerce.com", "da": 61, "do_follow": True},
    {"name": "Alignable", "url": "alignable.com", "da": 61, "do_follow": True},
    {"name": "Thumbtack", "url": "thumbtack.com", "da": 81, "do_follow": False},
    {"name": "Houzz", "url": "houzz.com", "da": 91, "do_follow": True},
    {"name": "EnergySage", "url": "energysage.com", "da": 72, "do_follow": True},
    {"name": "SolarReviews", "url": "solarreviews.com", "da": 65, "do_follow": True},
    {"name": "Find Solar", "url": "findsolar.com", "da": 48, "do_follow": True},
]

# ── Niche-relevant forums ────────────────────────────────────────────────────

FORUMS = [
    {"name": "Reddit r/solar", "url": "reddit.com/r/solar", "members": "200k+"},
    {"name": "Reddit r/solarDIY", "url": "reddit.com/r/solardiy", "members": "50k+"},
    {"name": "Reddit r/homeimprovement", "url": "reddit.com/r/HomeImprovement", "members": "3M+"},
    {"name": "Reddit r/RenewableEnergy", "url": "reddit.com/r/RenewableEnergy", "members": "100k+"},
    {"name": "Reddit r/electricians", "url": "reddit.com/r/electricians", "members": "150k+"},
    {"name": "Solar Panel Talk", "url": "solarpaneltalk.com/forum", "members": "niche"},
    {"name": "DIY Solar Forum", "url": "diysolarforum.com", "members": "niche"},
    {"name": "Electrician Talk Forum", "url": "electriciantalk.com", "members": "niche"},
    {"name": "Green Building Advisor Forum", "url": "greenbuildingadvisor.com/forums", "members": "niche"},
    {"name": "Solar Quotes Forum", "url": "solarquotes.com.au/forums", "members": "niche"},
    {"name": "Home Energy Saver Forum", "url": "homeenergysaver.lbl.gov", "members": "niche"},
    {"name": "Houzz Discussions", "url": "houzz.com/discussions", "members": "40M+"},
]

# ── Q&A platforms ────────────────────────────────────────────────────────────

QA_PLATFORMS = [
    {"name": "Quora", "url": "quora.com", "notes": "Answer solar/panel questions with link"},
    {"name": "Reddit AMA", "url": "reddit.com/r/AMA", "notes": "Host AMA about solar installation"},
    {"name": "Stack Exchange Home Improvement", "url": "diy.stackexchange.com", "notes": "Answer electrical/panel questions"},
    {"name": "Yahoo Answers Archive", "url": "answers.yahoo.com", "notes": "Historical reference only"},
    {"name": "LinkedIn Q&A", "url": "linkedin.com", "notes": "Answer in relevant LinkedIn groups"},
]

# ── Social bookmarking sites ─────────────────────────────────────────────────

SOCIAL_BOOKMARKS = [
    {"name": "Diigo", "url": "diigo.com", "do_follow": True},
    {"name": "Scoop.it", "url": "scoop.it", "do_follow": True},
    {"name": "Flipboard", "url": "flipboard.com", "do_follow": False},
    {"name": "Mix", "url": "mix.com", "do_follow": True},
    {"name": "Pocket", "url": "getpocket.com", "do_follow": False},
    {"name": "Pearltrees", "url": "pearltrees.com", "do_follow": True},
    {"name": "Folkd", "url": "folkd.com", "do_follow": True},
    {"name": "BizSugar", "url": "bizsugar.com", "do_follow": True},
    {"name": "GrowthHackers", "url": "growthhackers.com", "do_follow": True},
    {"name": "Slashdot", "url": "slashdot.org", "do_follow": False},
]

# ── Profile/Web 2.0 properties ───────────────────────────────────────────────

PROFILE_PLATFORMS = [
    {"name": "Medium", "url": "medium.com", "type": "blog", "da": 96},
    {"name": "LinkedIn Company Page", "url": "linkedin.com/company", "type": "social", "da": 99},
    {"name": "Twitter/X", "url": "twitter.com", "type": "social", "da": 95},
    {"name": "Facebook Page", "url": "facebook.com/pages", "type": "social", "da": 96},
    {"name": "YouTube Channel", "url": "youtube.com", "type": "video", "da": 100},
    {"name": "Pinterest Board", "url": "pinterest.com", "type": "visual", "da": 94},
    {"name": "WordPress.com", "url": "wordpress.com", "type": "blog", "da": 96},
    {"name": "Blogger", "url": "blogger.com", "type": "blog", "da": 97},
    {"name": "Tumblr", "url": "tumblr.com", "type": "blog", "da": 95},
    {"name": "Issuu", "url": "issuu.com", "type": "document", "da": 95},
    {"name": "SlideShare", "url": "slideshare.net", "type": "slides", "da": 95},
    {"name": "Scribd", "url": "scribd.com", "type": "document", "da": 94},
    {"name": "About.me", "url": "about.me", "type": "profile", "da": 92},
    {"name": "Crunchbase", "url": "crunchbase.com", "type": "business", "da": 91},
]

# ── Guest post target niches ─────────────────────────────────────────────────

GUEST_POST_NICHES = [
    "solar energy blog",
    "renewable energy write for us",
    "home improvement guest post",
    "green building blog contribute",
    "energy efficiency write for us",
    "sustainable living guest post",
    "electrical contractor blog",
    "construction industry blog write for us",
    "eco-friendly home blog",
    "clean energy news contribute",
]

# ── Press release distribution sites ────────────────────────────────────────

PRESS_RELEASE_SITES = [
    {"name": "PR Newswire", "url": "prnewswire.com", "free": False, "da": 93},
    {"name": "Business Wire", "url": "businesswire.com", "free": False, "da": 93},
    {"name": "PRWeb", "url": "prweb.com", "free": False, "da": 87},
    {"name": "OpenPR", "url": "openpr.com", "free": True, "da": 66},
    {"name": "PR.com", "url": "pr.com", "free": True, "da": 62},
    {"name": "Free-Press-Release.com", "url": "free-press-release.com", "free": True, "da": 55},
    {"name": "PRLog", "url": "prlog.org", "free": True, "da": 68},
    {"name": "NewswireToday", "url": "newswiretoday.com", "free": True, "da": 52},
    {"name": "1888PressRelease", "url": "1888pressrelease.com", "free": True, "da": 49},
    {"name": "pressreleasepoint", "url": "pressreleasepoint.com", "free": True, "da": 47},
]

# ── Anchor text variations ───────────────────────────────────────────────────

ANCHOR_TEXT_VARIANTS = {
    "branded": [
        "Alfa Panels",
        "alfaapanels.com",
        "Alfa Panels solar solutions",
    ],
    "exact_match": [
        "solar panels",
        "electrical panels",
        "solar panel installation",
    ],
    "partial_match": [
        "high-efficiency solar panels",
        "residential solar panel systems",
        "commercial electrical panels",
        "solar energy solutions",
    ],
    "generic": [
        "click here",
        "learn more",
        "visit website",
        "read more",
    ],
    "long_tail": [
        "best solar panels for residential homes",
        "how to choose electrical panels",
        "solar panel installation guide",
        "solar panel cost calculator",
    ],
}

# ── Content angles for link bait ─────────────────────────────────────────────

LINKABLE_CONTENT_IDEAS = [
    "Ultimate Guide to Solar Panel Installation Costs [City/State-specific]",
    "Solar Panel Efficiency Comparison: Brand vs Brand [Annual Study]",
    "How to Calculate Your Solar Panel ROI [Interactive Calculator]",
    "Electrical Panel Upgrade Guide: When, Why, and How Much",
    "State-by-State Solar Incentives and Rebates [Annual Update]",
    "Solar Panel Maintenance Checklist: Printable PDF",
    "Top 10 Mistakes When Installing Solar Panels",
    "Solar Energy Statistics [Year]: Industry Data Roundup",
    "Do Solar Panels Work in Cloudy Weather? [Data Study]",
    "How Many Solar Panels Do I Need? [Free Calculator]",
]


def get_strategy_platforms(strategy: str) -> list[dict]:
    """Return platform list for a given strategy name."""
    mapping = {
        "directory_submission": BUSINESS_DIRECTORIES,
        "forum_participation": FORUMS,
        "qa_platform": QA_PLATFORMS,
        "social_bookmarking": SOCIAL_BOOKMARKS,
        "profile_creation": PROFILE_PLATFORMS,
        "press_release": PRESS_RELEASE_SITES,
    }
    return mapping.get(strategy, [])


def get_anchor_mix() -> dict:
    """Return recommended anchor text distribution for natural link profile."""
    return {
        "branded": "40% — use most often to build brand recognition",
        "partial_match": "30% — topically relevant, lower over-optimization risk",
        "exact_match": "10% — use sparingly to avoid over-optimization penalty",
        "long_tail": "15% — natural and diverse",
        "generic": "5% — minimal, only where anchor choice is limited",
    }
