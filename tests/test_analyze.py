import sys,unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from analyze import funnel,retention,clean_events,write_outputs

def sample():
    rows=[]
    for user,week,steps in [(1,"2025-01-06",["view","cart","purchase"]),(2,"2025-01-06",["view","cart"]),(3,"2025-01-13",["view"])]:
        for i,stage in enumerate(steps): rows.append({"user_id":user,"user_session":f"s{user}","event_time":f"{week}T0{i}:00:00Z","event_type":stage})
    rows.append({"user_id":1,"user_session":"s1","event_time":"2025-01-20T01:00:00Z","event_type":"view"})
    return pd.DataFrame(rows)

class AnalysisTests(unittest.TestCase):
    def test_funnel_respects_stage_order(self):
        f=funnel(sample()).set_index("stage")
        self.assertEqual(f.loc["view","sessions"],3); self.assertEqual(f.loc["cart","sessions"],2); self.assertEqual(f.loc["purchase","sessions"],1)
    def test_retention_is_bounded(self):
        r=retention(sample()); self.assertTrue(r.retention.between(0,1).all())
    def test_missing_required_columns_fail(self):
        with self.assertRaises(ValueError): clean_events(pd.DataFrame({"event_time":[]}))

if __name__=="__main__": unittest.main()
