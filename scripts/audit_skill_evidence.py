"""Inspect historical A/B skill continuity from the existing manual evidence map.

This is retrospective, non-exhaustive annotation, not calibrated prediction.
"""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import json
from forecast_confidence import SKILLS

R=Path(__file__).resolve().parents[1]
def read(path): return json.loads((R/path).read_text(encoding='utf-8'))
def date(value): return datetime.strptime(value,'%d/%m/%Y')
bank={q['id']:q for q in read('data/bank.json')['questions']}
pairs=read('data/pairs.json')
selected=set(read('data/forecast-best.json')['question_ids'])
forecast=[q for q in read('data/forecast.json') if q['id'] in selected]
records=[]
for key,(name,raw) in SKILLS.items():
    support=defaultdict(list)
    for qid in raw.split():
        assert qid in bank, qid
        for s in bank[qid]['sources']:
            if s.get('date') and qid not in support[s['date']]: support[s['date']].append(qid)
    transitions=[]
    for pair in pairs:
        a,b=pair['a'],pair['b']
        transitions.append(dict(a=a,b=b,a_ids=sorted(support[a]),b_ids=sorted(support[b]),
            prior_support_dates=sorted((d for d,ids in support.items() if ids and date(d)<date(a)),key=date)))
    records.append(dict(skill=key,label=name,
        latest_a_ids=sorted(support['19/10/2026']),
        latest_a_present=bool(support['19/10/2026']),
        a_appearances=sum(bool(x['a_ids']) for x in transitions),
        b_appearances=sum(bool(x['b_ids']) for x in transitions),
        continued=sum(bool(x['a_ids'] and x['b_ids']) for x in transitions),
        b_after_absent_a=sum(not x['a_ids'] and bool(x['b_ids']) for x in transitions),
        transitions=transitions))
by_skill={r['skill']:r for r in records}
out=dict(description='Retrospective partial manual evidence mapping. An absent mapping does not prove the skill was absent from the exam; counts are lower bounds and may be biased.',
         focused=[dict(id=q['id'],skill=q['skill'],score=q['confidence'],
             a=by_skill[q['skill']]['a_appearances'],b=by_skill[q['skill']]['b_appearances'],
             both=by_skill[q['skill']]['continued'],latest_a_ids=by_skill[q['skill']]['latest_a_ids']) for q in forecast],
         skills=records)
(R/'data/skill-transition-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
if __name__=='__main__':
    print(json.dumps(out['focused'],ensure_ascii=False,indent=2))
