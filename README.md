# E-Commerce Sales Intelligence Dashboard

An interactive data analytics dashboard built with **Streamlit + Plotly** analyzing 4 years of Global Superstore sales data.

## Project Highlights
- **10,000+ orders** analyzed across 4 years (2011–2014)
- **12 interactive charts** — trend, distribution, correlation, geo map
- **5 business insights** derived from data
- Fully interactive filters — year, category, region, segment

## Dashboard Sections
| Tab | Content |
|-----|---------|
| Overview | KPIs, monthly trend, quarterly growth, segment split |
| Products | Sub-category profit, top products, discount impact |
| Geography | US choropleth map, region comparison |
| Shipping | Mode performance, ship days distribution |
| Data Quality | Missing values, outliers, descriptive stats |
| Insights | 5 actionable business recommendations |

## Tech Stack
`Python` · `Pandas` · `Plotly` · `Streamlit` · `Seaborn` · `NumPy`

## Key Business Insights Found
1. **Tables & Bookcases** sub-categories generate negative profit despite high sales
2. Discounts above **20% cause negative margins** — pricing policy overhaul needed
3. **West region** leads in profitability — best ROI for marketing spend
4. **November–December** peak season — inventory should be stocked 6 weeks prior
5. **First Class** shipping has the best speed-to-cost ratio

## How to Run
```bash
pip install -r requirements.txt
# Place superstore.csv in data/ folder
streamlit run app.py
```

## Dataset
[Global Superstore Sales Dataset](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting) — Kaggle
