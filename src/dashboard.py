from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Funnel & Retention",layout="wide")
st.title("Product Funnel & Retention")
path=st.sidebar.text_input("Events CSV", "data/events.csv")
if not Path(path).exists():
    st.info("Run `python src/fetch_events.py --rows 500000` or provide an events CSV.")
    st.stop()
from analyze import clean_events,funnel,retention
events=clean_events(pd.read_csv(path))
f=funnel(events); r=retention(events)
c1,c2,c3=st.columns(3); c1.metric("Events",f"{len(events):,}"); c2.metric("Sessions",f"{events.user_session.nunique():,}"); c3.metric("Users",f"{events.user_id.nunique():,}")
st.subheader("Session funnel"); st.dataframe(f,use_container_width=True,hide_index=True)
st.bar_chart(f.set_index("stage")["sessions"])
st.subheader("Weekly cohort retention"); pivot=r.pivot(index="cohort_week",columns="week_number",values="retention")
st.dataframe(pivot.style.format("{:.0%}"),use_container_width=True)
st.caption("Descriptive analysis of the supplied event sample. Missing events count as not reaching a stage; observed retention is not causal.")
