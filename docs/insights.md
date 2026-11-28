# GoDesi Sales & Distribution: insights for the founder

**Live dashboard:** https://godesi-analytics.streamlit.app/ (also runs inside Snowflake on live data)
**Period:** January 2024 to December 2025 · 80,000 orders · 60 SKUs · 4 channels · 4 regions

> Sales, customers and inventory are **synthetic** (generated with a fixed seed), so the numbers show the
> method, not GoDesi's real business. The market comparison (insight 7) uses **real Open Food Facts** data.
> All revenue figures are net revenue (gross minus discount) on orders that were not cancelled.

## Summary

| # | Finding | Number | Recommendation |
|---|---|---|---|
| 1 | Revenue grew strongly, led by offline | ₹8.14 cr → ₹10.62 cr (**+30.4%**) | Keep investing in offline distribution |
| 2 | Online channels earn almost double the margin | 45% vs **24.9%** offline | Push margin mix online without starving offline |
| 3 | Mithai is the business; 29 of 60 SKUs make 80% | Top 10 SKUs are **all mithai** | Protect mithai availability; prune the long tail |
| 4 | West and North grow fastest | West **+44%**, North +41% | Expand West through marketplace and quick commerce |
| 5 | Repeat buying is weaker for newer customers | Month-1 retention **34%** (2024 cohorts) → **12.5%** (2025 cohorts) | Second-order programme in the first 30 days |
| 6 | Festival promos work; generic ones do not | DIWALI25 **+131%**; 9 of 26 negative | Fewer, festival-led promos |
| 7 | Stock-outs peak just when demand peaks | **681** warehouse-SKU-days in Oct 2025 | Build festival stock from August |
| 8 | GoDesi is visible in Sweets & mithai | Joint **11th of 317** brands | Use the low-sugar angle as a differentiator |

---

## 1. Revenue grew 30%, and offline still carries the business
- **Finding:** net revenue rose from ₹8.14 cr (2024) to ₹10.62 cr (2025), **+30.4%**. Orders went from 33,437 to 41,681 and
  AOV from ₹2,435 to ₹2,548. Gross margin improved from 29.1% to 29.9%.
- **Chart:** Executive overview → monthly revenue (festival months coloured).
- **Recommendation:** growth comes from more orders and slightly bigger baskets. Both levers are working, so plan
  2026 capacity for +25–30%.

## 2. Offline is 77% of revenue but has the lowest margin
| Channel | Net revenue | Share | Gross margin |
|---|---|---|---|
| Offline (kirana, modern trade) | ₹14.37 cr | 76.6% | 24.9% |
| Marketplace | ₹2.16 cr | 11.5% | 43.6% |
| Quick commerce | ₹1.40 cr | 7.4% | 46.4% |
| D2C (godesi.in) | ₹0.83 cr | 4.4% | 45.9% (highest discount, 2.86%) |

- **Finding:** online channels earn about **1.8×** the margin of offline. Yet the online share did not grow
  (23.9% in 2024 vs 23.0% in 2025), because offline grew fastest (+31.9%).
- **Chart:** Channels & regions → channel table; Executive overview → 100% channel mix.
- **Recommendation:** every 1 point of revenue moved from offline to online adds about 0.2 points of total margin.
  Aim for online at 30% of revenue, mainly via quick commerce (best margin, lowest discount).

## 3. Mithai drives the business, and the range has a long tail
- **Finding:** Mithai is **63%** of revenue. The top 10 SKUs are all mithai, led by **Dates Dry Fruit Laddu
  (₹1.46 cr)**, Kaju Katli (₹1.19 cr) and Ghee Mysore Pak (₹0.94 cr). **29 of the 60 SKUs make 80%** of revenue.
  The 15 new launches already bring 17.6%. Namkeen has the best margin (31.4%) but the smallest share (14%).
- **Chart:** Products → top 10, Pareto curve, category margin.
- **Recommendation:** never let the top 10 go out of stock (see insight 7). Review the bottom 10 SKUs for delisting.
  Test growing Namkeen for margin.

## 4. West and North are the growth regions
| Region | 2025 revenue | Growth | Margin | Online share |
|---|---|---|---|---|
| South | ₹7.17 cr | +27% | 29.0% | 21% |
| North | ₹1.60 cr | +41% | 30.1% | 26% |
| West | ₹1.21 cr | **+44%** | **33.3%** | **41%** |
| East | ₹0.63 cr | +18% | 27.9% | 15% |

- **Finding:** South is two-thirds of revenue. West grows fastest and has the best margin, *because* 41% of its
  revenue is online (vs 21% in the South). Among cities with at least ₹10 lakh in 2024, **Mumbai (+76%)** and
  **Jaipur (+68%)** grow fastest. (Smaller cities such as Mangaluru show bigger percentages, but from a tiny base.)
- **Chart:** Channels & regions → region growth, fastest-growing cities.
- **Recommendation:** grow West and North through marketplace and quick commerce, not by opening offline distribution there first.

## 5. Repeat buying is weaker for newer customers
- **Finding:** weighted across all cohorts, **22.2%** of customers order again in month 1, 20.4% in month 3,
  17.5% in month 6 and **14.3% in month 12**. Average 12-month revenue per customer is **₹3,162**. Returning
  customers bring about two-thirds of revenue (70% in 2024, 66% in 2025).
- **But the heatmap shows the average hides a trend:** month-1 retention is **34.4%** for the 2024 cohorts and only
  **12.5%** for the 2025 cohorts (month 3: 28.2% vs 11.9%; month 6: 20.5% vs 12.1%). Two reasons:
  1. *Left-censoring:* the data starts in January 2024, so the early "new" cohorts include customers who were already
     buying in 2023. They look loyal because they are not really new. Treat the 2024-01 to 2024-03 cohorts with care.
  2. The customer base grew faster than orders, so each customer orders less often. (In this synthetic data, orders
     are assigned to random existing customers, which exaggerates the effect.)
  The honest planning number for a **new** customer today is about **12-15%** in month 1, not 22%.
- **Chart:** Customers & promotions → cohort heatmap, LTV curve, new vs returning.
- **Recommendation:** the biggest drop is right after the first order. A second-order offer within 30 days
  (D2C email or WhatsApp) is the cheapest growth lever. Measure it as month-1 retention per cohort in the heatmap.

## 6. Festival promos work; generic discounts often lose money
- **Finding:** average daily revenue during the promo vs the 28 days before:
  **DIWALI25 +130.7%**, INDEPENDENCE24 +123.4% (at only 10% off), DIWALI24 +115.1%, HOLI25 +105.2%. But
  **9 of 26** comparable promos had *negative* uplift: MEGASALE25 −18.3%, NEWYEAR26 −18.3%, UGADI24 −12.0%, and
  both GANESHA promos. A bigger discount does not guarantee more uplift: INDEPENDENCE24 at 10% performed
  like Diwali at 25%.
- **Chart:** Customers & promotions → promo uplift.
- **Recommendation:** concentrate the promo budget on Diwali, Holi, Rakhi and Independence Day; drop or
  redesign the generic sales (Mega Sale, New Year). Test 15% instead of 25% for Diwali.
- *Excluded:* SANKRANTI24, REPUBLICDAY24, WELCOME10 and FREESHIP have no full 28-day "before" window.

## 7. Stock-outs peak exactly when demand peaks
- **Finding:** stock-outs grew from 297 warehouse-SKU-days in October 2024 to **681 in October 2025, when all
  60 SKUs ran out somewhere**. Average days of cover fell to **9.4 days**. No SKU was ever overstocked (> 90 days),
  so the problem is too little stock, not too much.
- **Chart:** Supply & market → stock-out days and days of cover.
- **Recommendation:** build festive stock from August (cover of at least 21 days by 1 October), starting with the
  top 10 mithai SKUs. Revenue lost to stock-outs is not measured yet (next step: compare demand on days with and
  without stock).

## 8. GoDesi in the real market (Open Food Facts India)
- **Finding:** in Sweets & mithai, GoDesi ranks joint **11th of 317 brands** by number of listed products (8 products,
  1.3% of the segment, tied with Chupa Chups and Wrigley's). Cadbury leads (44), then Dabur, Nestlé, Parle, Amul,
  Apis and Kissan. GoDesi's median sugar is **59.3 g per 100 g**.
- *Data-quality fix found while building the dashboard:* many brands were written in several cases (Apis / apis,
  Chupa Chups / CHUPA CHUPS). Snowflake compares text case-sensitively, so they counted as separate brands and
  GoDesi looked 8th of 346. Power BI (case-insensitive) showed different bars, which exposed it. dbt now keeps one
  spelling per brand (5,751 brand names became 4,695 across all segments).
- **Chart:** Supply & market → brands in the segment, new products per year.
- **Recommendation:** GoDesi's online visibility is already strong for its size. A lower-sugar mithai line would
  stand out in a segment dominated by chocolate brands.
- *Caveat:* the "Sweets & mithai" segment also contains chocolate, honey and jams. Open Food Facts counts
  listed products, not sales, and 2026 is a partial year.

## Limitations
- Synthetic sales data: the patterns were designed into the generator, so they demonstrate the analysis, not real
  facts about GoDesi.
- Promo uplift compares with the 28 days before; it does not control for season (e.g. Diwali vs normal October demand).
- Retention counts any repeat order. There is no customer-level marketing data to explain *why* customers return.
- Open Food Facts is crowd-sourced: coverage differs by brand, and some categories are mixed.

## How these numbers were produced
- dbt models on Snowflake (`godesi/models/marts/`), with 144 data tests, 5 singular tests and 1 unit test.
- One SQL file per question in `godesi/analyses/q1..q9*.sql` (`dbt compile -s "path:analyses"`).
- KPIs are ratios of sums (e.g. margin % = Σ margin / Σ net revenue; retention = Σ active / Σ cohort customers).
- The dashboard numbers match the analyses and the Power BI measures (net revenue ₹18,76,44,075; 75,118 orders;
  AOV ₹2,498; margin 29.6%).
