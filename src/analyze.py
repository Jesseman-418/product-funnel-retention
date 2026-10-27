"""Session funnel and weekly cohort retention analysis for ecommerce events."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

REQUIRED={"event_time","event_type","user_id","user_session"}
STAGES=["view","cart","purchase"]

def clean_events(events: pd.DataFrame) -> pd.DataFrame:
    missing=REQUIRED-set(events.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    df=events.copy()
    df["event_time"]=pd.to_datetime(df.event_time,utc=True,errors="coerce")
    df=df.dropna(subset=["event_time","user_id","user_session"])
    df["event_type"]=df.event_type.astype(str).str.lower()
    return df[df.event_type.isin(STAGES)].sort_values("event_time")

def funnel(events: pd.DataFrame) -> pd.DataFrame:
    df=clean_events(events)
    session_stage=df.pivot_table(index="user_session",columns="event_type",values="event_time",aggfunc="min")
    for stage in STAGES:
        if stage not in session_stage: session_stage[stage]=pd.NaT
    viewed=session_stage["view"].notna()
    carted=viewed & session_stage["cart"].notna() & (session_stage["cart"]>=session_stage["view"])
    purchased=carted & session_stage["purchase"].notna() & (session_stage["purchase"]>=session_stage["cart"])
    counts=[int(viewed.sum()),int(carted.sum()),int(purchased.sum())]
    rows=[]
    for i,stage in enumerate(STAGES):
        prior=counts[i-1] if i else counts[0]
        rows.append({"stage":stage,"sessions":counts[i],"conversion_from_previous":1.0 if i==0 else (counts[i]/prior if prior else None),
                     "conversion_from_view":counts[i]/counts[0] if counts[0] else None})
    return pd.DataFrame(rows)

def retention(events: pd.DataFrame) -> pd.DataFrame:
    df=clean_events(events)
    df["week"]=df.event_time.dt.to_period("W-SUN").astype(str)
    first=df.groupby("user_id").week.min().rename("cohort_week")
    active=df[["user_id","week"]].drop_duplicates().join(first,on="user_id")
    active["week_number"]=active.apply(lambda r: (pd.Period(r.week,freq="W-SUN")-pd.Period(r.cohort_week,freq="W-SUN")).n,axis=1)
    counts=active.groupby(["cohort_week","week_number"]).user_id.nunique().rename("active_users").reset_index()
    sizes=active[active.week_number==0].groupby("cohort_week").user_id.nunique().rename("cohort_size")
    counts=counts.join(sizes,on="cohort_week"); counts["retention"]=(counts.active_users/counts.cohort_size).round(4)
    return counts.sort_values(["cohort_week","week_number"])

def write_outputs(events: pd.DataFrame, out_dir: str|Path) -> dict:
    cleaned=clean_events(events); f=funnel(cleaned); r=retention(cleaned)
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    f.to_csv(out/"funnel.csv",index=False); r.to_csv(out/"retention.csv",index=False)
    drop=f.iloc[1:]; biggest=drop.sort_values("conversion_from_previous").iloc[0] if len(drop) else None
    memo={"event_rows":len(cleaned),"sessions":int(cleaned.user_session.nunique()),"users":int(cleaned.user_id.nunique()),
          "funnel_definition":"Session reached view, then cart at or after view, then purchase at or after cart.",
          "retention_definition":"Weekly active users divided by users first seen in that cohort week.",
          "largest_observed_stage_loss":None if biggest is None else str(biggest.stage),
          "interpretation":"Descriptive association only; this observational event sample does not establish why users drop off or prove an intervention will help.",
          "caveats":["The analysis covers only the supplied sample and date range.","A user/session missing an event is counted as not reaching that stage.","Retention is weekly and uses first observed activity in the sample as cohort start."]}
    (out/"decision_memo.json").write_text(json.dumps(memo,indent=2))
    return memo

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("csv"); p.add_argument("--output",default="outputs"); a=p.parse_args()
    print(json.dumps(write_outputs(pd.read_csv(a.csv),a.output),indent=2))

if __name__=="__main__": main()
