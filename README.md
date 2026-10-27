# Product Funnel and Cohort Retention

Analyze session progression and weekly user retention from public ecommerce events. The work defines every denominator, preserves event order, exports reproducible CSV outputs, and includes a small interactive dashboard.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/fetch_events.py --rows 500000 --output data/events.csv
python src/analyze.py data/events.csv --output outputs
streamlit run src/dashboard.py
python -m unittest discover -s tests -v
```

Source: [eCommerce Behavior Data from Multi-Category Store](https://huggingface.co/datasets/kevykibbz/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019), collected by Open CDP and attributed in its dataset card to REES46. The source is large (over 100 million rows); the downloader streams a bounded chronological sample. Its first-observed user week is the cohort origin. Sample windows, missing identifiers, and the source's observational nature limit interpretation.

## Metric definitions

- Funnel: sessions with a view, then a cart at or after the first view, then a purchase at or after the first cart.
- Weekly retention: distinct active users in cohort week N divided by distinct users first observed in cohort week 0.
- `outputs/decision_memo.json` records the largest observed stage loss and caveats. It does not claim a cause or forecast intervention impact.
