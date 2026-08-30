# Off-Page SEO Report: alfaapanels.com
Date: 2026-08-30

I'll work through this systematically, starting with reconnaissance on the brand and competitors.

I've found something important that changes the entire brief. Let me verify before proceeding.

Analysis tools now — running brand mention categorization and competitor gap checks in parallel.

Now scoring real prospects — I'm testing both the briefed niche and the site's actual niche to quantify the mismatch.

# Off-Page SEO Analysis — alfaapanels.com

## ⚠️ Stop-and-Read: The Brief Has Two Critical Errors

Before any tactics, you need to know that **the niche and competitor set in your brief do not match the website.**

**Your brief says:** aluminum composite panels (ACP), cladding, facade.
**What alfaapanels.com actually sells:** 

Alfaa Panels manufactures high-performance PUF, PIR, Rockwool, Clean Room, and Cold Room Panels engineered for superior insulation, strength, and faster construction across industrial, commercial, cold storage, and clean room applications.

 

It positions as one of India's sandwich panel manufacturers serving warehouses, factories, cold storage facilities, commercial buildings and infrastructure projects.



These are **entirely different product categories**. A PUF/PIR panel is 

a rigid, closed-cell polyurethane foam core bonded between two pre-painted or galvanised steel sheets — the steel skins carry load, the foam core blocks heat transfer

. An ACP is 

two aluminium sheets with a low-density polyethylene filling between them

, used for 

building interior and exterior facades, decoration applications, and billboards

.

Different core, different skin, different buyer, different keywords, different trade media.

**Your competitor list is also wrong.** Dibond, Alucobond, Reynobond and Alpolic are all Western ACM/MCM facade brands — 

ALPOLIC, for example, is a global leader in metal and aluminum composite material manufacturing

. Alfaa is an **India-focused industrial insulation panel maker** with 

plants in Hosur (2), Ahmedabad (2), Raipur, Karnal, and Pune

. There is essentially zero SERP overlap.

I ran the link-gap tool against all four anyway so you can see the output, but **I'd advise you not to action any of it.** Chasing links from US architectural-facade publications for an Indian cold-storage panel manufacturer will burn your budget and produce irrelevant links.

I've therefore built the real deliverables against the **actual** niche, and shown you the cost of the mismatch below.

---

## Methodology & Honest Limitations

Please read this before you trust any number in this report.

- **I have no backlink index.** No Ahrefs, Majestic, Semrush or GSC access. I cannot see Alfaa's real backlink profile, its DR, its referring domains, or the actual backlink lists of the four competitors. Task 2 as literally specified — "find sites linking to them but not to you" — **cannot be completed with these tools.** What I've provided instead is a reasoned prospect strategy.
- **The `-site:` search operator you supplied isn't supported** by my search tool, so I ran broad brand searches instead.
- **The scoring tool is a fixed heuristic, not real data.** It awards points on keyword overlap and URL patterns. It rated `mechfab.org` a "high authority domain (+30)" — I don't believe that's accurate; it looks like a small regional site. Treat scores as *rough triage*, not authority metrics.
- **The backlink quality tool only inspects anchor text.** It returned "domain appears clean" for every URL I gave it, including ones I invented as tests. It did not verify those links exist. Two of the three backlinks I analysed are *hypothesised*, not confirmed live.

---

## TASK 1 — Brand Mention Audit

### Finding 1A: You have a severe brand-entity collision problem

This is the highest-value finding in the entire audit, and it's not a link issue — it's an identity issue.

Four distinct entities compete for "Alfa Panels":

| Entity | What it is | Collision risk |
|---|---|---|
| **alfaapanels.com** | Your client — Indian sandwich panels | — |
| **alfapanels.uk** | 

A family-run North East England company, established over 40 years, specialising in GRP fibreglass panels primarily for historic Alfa Romeo cars

 | **Severe** — near-identical domain |
| **ALFA PEB LTD** | 

Listed among PUF sandwich panel manufacturers on TradeIndia

 | **Severe** — same industry, same country |
| **Alfaa Panels** | Your own alternate spelling | Self-inflicted |

Note the UK site *also* refers to itself inconsistently as 

"Alpha Panels"

. The naming space is genuinely polluted.

**You are also fighting yourself.** Your homepage brands as 

"Alfaa Panels"

 while page titles render as "Alfa Panels" (see the Projects, FAQ and Cold Room pages). Search engines and LLMs cannot consolidate an entity that can't spell its own name consistently.

**Action:** Pick **"Alfaa Panels"** (matches the domain, differentiates from ALFA PEB and the UK Alfa Romeo firm) and enforce it across every title tag, schema `Organization.name`, directory listing, and social profile. Do this *before* outreach — otherwise every link you build reinforces a fragmented entity.

### Finding 1B: Unlinked mentions

I ran three representative mentions through categorisation. All three returned **"Unlinked mention — link building opportunity"**, but that tool cannot distinguish relevance, so here's my actual read:

| Mention source | Tool verdict | My verdict |
|---|---|---|
| TradeIndia — "ALFA PEB LTD" in PUF supplier list | Unlinked, neutral, reach out | ❌ **False positive.** That's a competitor, not you. Do not claim it. |
| alfaapanels.com homepage copy | Unlinked, neutral, reach out | ❌ **False positive.** Your own site. |
| alfapanels.uk — Alfa Romeo GRP panels | Unlinked, neutral, reach out | ❌ **False positive.** Different company. |

**This is the real headline: I could not find a single genuine third-party editorial mention of Alfaa Panels.** Beyond its own domain, the brand is close to invisible in the open index. That is a very different problem from "we have unlinked mentions to convert" — and it changes the whole strategy from *reclamation* to *creation*.

### Finding 1C: Technical issue affecting link equity

Two live URL patterns serve the same content:
- `alfaapanels.com/all-products/`
- `www.alfaapanels.com/product-category/all-products/`

Both are indexed. **Any links you build risk splitting across duplicate URLs.** Fix canonicalisation and pick one www/non-www convention before the campaign starts, or you'll leak a meaningful share of the equity you earn.

Separately, the pages return large blocks of Zoho SalesIQ JavaScript in their crawled content. This suggests heavy client-side rendering that may be degrading how crawlers parse your pages.

---

## TASK 2 — Competitor Backlink Research

### What the brief asked for vs. what's possible

As stated in Limitations, I cannot pull competitor backlink profiles. Here is the tool output for transparency — all four returned the same generic three-step template:

| Competitor | Assumed link theme | Tool output |
|---|---|---|
| dibond.com | Signage/display substrates | Generic 3-step gap template |
| alucobond.com | Facade spec, rainscreen | Generic 3-step gap template |
| reynobond.com | Fire-rated cladding compliance | Generic 3-step gap template |
| alpolic.com | MCM data, architect CEUs | Generic 3-step gap template |

The tool does not query a link index — it reformats your inputs. **It confirms nothing.**

### The strategically correct competitor set

Replace your four with domains that actually compete for Alfaa's terms:

**Tier 1 — direct national rivals:** EPACK Prefab, Bansal Roofing Products Ltd, Industrial Foams Pvt Ltd, Everest Composites, Koreapuff 

(founded 2008 in Umbergaon, Gujarat, now expanded into Dubai, Oman, the US, Canada and Uruguay)

, Ice Make 

(established 1993)

, and ALFA PEB 

(two fully automated plants dedicated to sandwich panels)

.

**Tier 2 — regional:** Viraat Industries, 

which positions as the No. 1 trusted brand for PUF Panels in Bangalore

 — direct overlap with Alfaa's Hosur base.

**Where their links actually come from** (the realistic gap):
1. **B2B marketplace profiles** — IndiaMART, TradeIndia, Kompass, Justdial. Low authority individually, but these dominate Indian industrial SERPs and are table stakes.
2. **"Top N manufacturers" listicles** — the single highest-leverage format in this niche. Multiple such pages exist and Alfaa appears on none I found.
3. **Cold-chain and food-processing trade bodies.**

**Recommendation:** budget for one month of a real backlink tool (~$100–130). Without it, Task 2 stays guesswork.

---

## TASK 3 — Link Building Opportunities

Scored against the **correct** niche:

| # | Prospect | Score | Type | Notes |
|---|---|---|---|---|
| 1 | mechfab.org — Top 10 PUF Panel Manufacturers 2026 | **100** | Listicle inclusion | 

A 2026 buyer's guide with pricing, angled at Guwahati/Northeast buyers

. Discount the authority score. |
| 2 | tradeindia.com/blog — Top PUF Panel Manufacturers | **80** | Listicle inclusion | Strong domain, directly relevant |
| 3 | kompass.com — Top 10 PUF Manufacturers | **60** | Directory + listicle | 

Curated verified supplier list with contact details

 |
| 4 | fcaoi.org — Federation of Cold Storage Associations | **50** | Association | 

18 member states

; 

they circulate newsletters and convene manufacturers

 |
| 5 | wiselinkgroup.com — Top 10 Sandwich Panel Mfrs | **50** | Listicle inclusion | Lower authority, easy win |

### Proof of the niche-mismatch cost

I scored the *same* mechfab page twice, changing only the niche:

- Correct niche → **100/100**, "High relevance (+40)"
- Your briefed ACP niche → **80/100**, "Moderate relevance (+20)"

A 20-point relevance penalty on a page that is a *perfect* fit. Every prospect you evaluate through the ACP lens will be similarly mis-ranked, and you'll systematically deprioritise your best targets.

### Additional untapped angles

- **Cold-chain sector:** NCCD (nccd.gov.in) is 

a think tank with participation from educational and research institutions, regulatory authorities, trade bodies and companies

 — strong, hard-to-replicate authority.
- **Certification leverage:** 

CBRI certification

 is a genuine, linkable differentiator. Most competitors can't claim it.
- **Digital PR asset:** 

"the only panel manufacturer in all four corners of India" with 10 lakh+ sq m monthly capacity

 is a real story for Indian construction and logistics trade press.
- **Broken link building:** I found no confirmed broken links. This requires a crawler (Screaming Frog + Check My Links) — flagging as un-executed, not as "none exist."

---

## TASK 4 — Outreach Templates

The generator produced serviceable but generic drafts. **I'd advise against sending them as-is** — "Your resource page is great!" gets deleted by editors. Below are the raw outputs plus rewrites.

### Prospect 1 — Mechfab (Resource / listicle inclusion)

<details><summary>Tool output</summary>

> Subject: Resource suggestion for your Top 10 PUF Panel Manufacturers in India 2026 buyer's guide page
> Hi Editor, Your resource page on Top 10 PUF Panel Manufacturers in India 2026 buyer's guide is great! I created https://alfaapanels.com/about-us/ which might help your readers. Would you take a look?

</details>

**Rewritten:**

> **Subject:** CBRI-certified addition for your 2026 PUF panel guide
>
> Hi [Name],
>
> Your 2026 PUF buyer's guide is one of the few that actually publishes pricing bands and core-density figures instead of vague claims — the 38–45 kg/m³ note is the sort of detail buyers need.
>
> One gap worth considering: none of the ten listed manufacturers are CBRI-certified. Alfaa Panels is, which is relevant given your guide's emphasis on separating strong suppliers from cheap ones. We also run plants in Hosur, Ahmedabad, Raipur, Karnal and Pune — useful for your Northeast readers, since Raipur and Karnal materially change delivery lead times into Assam.
>
> Happy to send our CBRI test report and current pricing so you can verify independently. No obligation to include us.
>
> [Name], Alfaa Panels

*Why it works: proves the page was read, leads with a verifiable differentiator, ties to their stated reader segment, offers evidence rather than asking for a favour.*

### Prospect 2 — TradeIndia (Mention conversion)

<details><summary>Tool output</summary>

> Subject: You mentioned Alfaa Panels - thank you!
> Hi TradeIndia Content Team, Thank you for mentioning Alfaa Panels in your article about Top PUF Panel Manufacturers in India listicle! Would you be open to linking directly to https://alfaapanels.com/all-products/?

</details>

⚠️ **Do not send this.** It's built on the false-positive mention — TradeIndia listed **ALFA PEB**, a competitor. Thanking them for a mention that doesn't exist destroys credibility instantly.

**Rewritten as a correct-the-record pitch:**

> **Subject:** Possible name mix-up in your PUF manufacturers list
>
> Hi [Name],
>
> Quick note on your Top PUF Panel Manufacturers piece — you list ALFA PEB Ltd. Readers regularly confuse them with us (Alfaa Panels, alfaapanels.com); we're separate companies with similar names in the same category, which I suspect causes some sourcing friction for your audience.
>
> If you're updating the list, we'd be a legitimate addition: CBRI-certified, 35+ years, five plants across India, 10 lakh+ sq m monthly capacity. Documentation available on request.
>
> Either way, worth disambiguating the two names for your readers.
>
> [Name], Alfaa Panels

### Prospect 3 — Kompass India (Guest post)

<details><summary>Tool output</summary>

> Subject: Guest Post Idea for Kompass India Solutions Blog
> Hi Kompass India Editorial, I love your content on Kompass India Solutions Blog... I'd love to contribute a guest post. I write for Alfaa Panels. Would you be open to a collaboration?

</details>

**Rewritten:**

> **Subject:** Pitch: how to spec cold-room panels (thickness/density buyer's guide)
>
> Hi [Name],
>
> Your verified PUF supplier directory helps buyers find manufacturers — but the follow-on question we field daily is *which spec do I actually need?* Wrong-thickness orders are the most common and most expensive mistake in this category.
>
> Proposed piece: **"Cold Room Panel Specification: Matching Thickness and Core Density to Application"** — ~1,200 words covering the 30–150mm range, why 80–150mm is specified for deep-freeze, density trade-offs, and a spec checklist. Vendor-neutral; no product pitching.
>
> I'd want one contextual link to our cold-room resource, nothing more. Happy to send a full outline first.
>
> [Name], Alfaa Panels

---

## TASK 5 — 30-Day Action Plan

**Sequencing principle:** fix the foundation before pouring links into it. Weeks 1–2 are non-negotiable prerequisites — outreach before the entity and canonical issues are fixed will waste a meaningful share of every link earned.

### Week 1 — Foundation (do not skip)

| Priority | Action | Owner | Success measure |
|---|---|---|---|
| **P0** | Confirm strategy pivot: correct niche + competitor set signed off by client | Strategist | Written sign-off |
| **P0** | Lock brand name as **"Alfaa Panels"** across all titles, schema, socials | Content/Dev | 100% consistency |
| **P0** | Fix www/non-www + duplicate URL paths; implement canonicals | Dev | One indexed URL per page |
| **P1** | Procure backlink tool; export competitor profiles for the corrected Tier 1 set | SEO | Real referring-domain data |
| **P1** | Audit client-side rendering / Zoho script bloat | Dev | Clean server-rendered HTML |

### Week 2 — Baseline & asset build

| Priority | Action | Success measure |
|---|---|---|
| **P0** | Establish true backlink baseline (RD, DR, anchor distribution) | Documented starting point |
| **P1** | Claim/optimise IndiaMART, TradeIndia, Kompass, Justdial profiles | 4 consistent NAP listings |
| **P1** | Build the linkable asset: **"India Insulated Panel Specification Guide"** — thickness/density/application matrix + CBRI data | Published, indexable |
| **P2** | Verify the 3 hypothesised backlinks (IndiaMART, Mechfab, LinkedIn) actually exist | Confirmed live/not |

### Week 3 — Outreach wave 1

| Priority | Action | Target |
|---|---|---|
| **P0** | Send rewritten pitches to Mechfab, TradeIndia, Kompass | 3 sent, personalised |
| **P1** | Listicle sweep: identify 15 more "top N manufacturers India" pages; pitch inclusion | 15 contacted |
| **P1** | Approach FCAOI + NCCD re: membership/supplier listing | 2 conversations open |
| **P2** | Run Screaming Frog broken-link scan across top 20 niche domains | Prospect list built |

### Week 4 — Wave 2, PR & review

| Priority | Action | Target |
|---|---|---|
| **P1** | Follow up all week-3 non-responders (one polite follow-up only) | 100% followed up |
| **P1** | Digital PR push: "only manufacturer in all four corners of India" + Pune plant to Indian construction/logistics trade press | 10 outlets |
| **P2** | Guest post drafting for any accepted pitches | 1–2 drafts |
| **P0** | 30-day review: RD delta, anchor health, entity consolidation check | Reported vs. baseline |

### Realistic 30-day targets

| Metric | Target | Confidence |
|---|---|---|
| Directory/profile links live | 4–6 | High |
| Listicle inclusions won | 2–4 | Medium |
| Association listings | 1–2 | Medium |
| Guest posts published | 0–1 | Low (lead times) |
| Trade press pickups | 0–2 | Low |
| **Net new referring domains** | **8–14** | Medium |

Set expectations accordingly: this is a **near-zero-authority starting position** in a low-media-density B2B niche. Month 1 is foundation and directory capture. Meaningful editorial authority is a 4–6 month build, not a 30-day one.

---

## Three Things I'd Tell the Client First

1. **The brief pointed at the wrong industry.** Executing it as written would have produced irrelevant links in a facade-cladding vertical the client doesn't operate in. Fixing the brief is worth more than any link in this report.
2. **The brand is invisible and its name is contested.** Zero genuine third-party mentions found, competing against a same-industry near-namesake (ALFA PEB) and a near-identical domain (alfapanels.uk). Entity disambiguation outranks link acquisition in priority.
3. **Half this analysis needs paid tooling to complete.** Task 2 is currently inference, not data. Approve a backlink tool subscription or accept that competitor gap analysis stays theoretical.