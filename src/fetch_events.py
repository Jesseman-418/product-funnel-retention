"""Stream a bounded sample from a public Hugging Face ecommerce event dataset."""
import argparse
from itertools import islice
import pandas as pd
from datasets import load_dataset

DATASET="kevykibbz/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019"

def fetch(rows:int, output:str):
    stream=load_dataset(DATASET,split="train",streaming=True)
    sample=list(islice(iter(stream),rows))
    if not sample: raise RuntimeError("Dataset stream returned no rows")
    df=pd.DataFrame(sample)
    needed=["event_time","event_type","user_id","user_session"]
    missing=set(needed)-set(df.columns)
    if missing: raise ValueError(f"Dataset schema changed; missing {sorted(missing)}")
    df.to_csv(output,index=False)
    return {"rows_written":len(df),"file":output,"first_event":str(df.event_time.iloc[0]),"last_event":str(df.event_time.iloc[-1])}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--rows",type=int,default=500_000); p.add_argument("--output",default="data/events.csv"); a=p.parse_args()
    from pathlib import Path
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    print(fetch(a.rows,a.output))
