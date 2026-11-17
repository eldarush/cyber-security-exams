"""Retrospective, non-exhaustive historical A/B skill-continuity audit."""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import json
from forecast_confidence import SKILLS

R = Path(__file__).resolve().parents[1]

def evaluate(bank, pairs, forecast, selected):
    by_id = {q['id']: q for q in bank}
    selected = set(selected)
    date = lambda value: datetime.strptime(value, '%d/%m/%Y')
    records = []
    for key, (name, raw) in SKILLS.items():
        support = defaultdict(list)
        for qid in raw.split():
            assert qid in by_id, qid
            for source in by_id[qid]['sources']:
                if source.get('date') and qid not in support[source['date']]:
                    support[source['date']].append(qid)
        transitions = []
        for pair in pairs:
            a, b = pair['a'], pair['b']
            transitions.append(dict(a=a, b=b, a_ids=sorted(support[a]), b_ids=sorted(support[b]),
                prior_support_dates=sorted((d for d, ids in support.items() if ids and date(d)<date(a)), key=date)))
        records.append(dict(skill=key, label=name, latest_a_ids=sorted(support['19/10/2026']),
            latest_a_present=bool(support['19/10/2026']),
            a_appearances=sum(bool(x['a_ids']) for x in transitions),
            b_appearances=sum(bool(x['b_ids']) for x in transitions),
            continued=sum(bool(x['a_ids'] and x['b_ids']) for x in transitions),
            b_after_absent_a=sum(not x['a_ids'] and bool(x['b_ids']) for x in transitions),
            transitions=transitions))
    by_skill = {r['skill']: r for r in records}
    focused = [dict(id=q['id'], skill=q['skill'], score=q['confidence'],
        a=by_skill[q['skill']]['a_appearances'], b=by_skill[q['skill']]['b_appearances'],
        both=by_skill[q['skill']]['continued'], latest_a_ids=by_skill[q['skill']]['latest_a_ids'])
        for q in forecast if q['id'] in selected]
    assert len(focused) == len(selected)
    return dict(description='Retrospective partial manual evidence mapping. An absent mapping does not prove the skill was absent from the exam; counts are lower bounds and may be biased.', focused=focused, skills=records)

if __name__ == '__main__':
    def read(name): return json.loads((R/'data'/name).read_text(encoding='utf8'))
    audit = evaluate(read('bank.json')['questions'], read('pairs.json'), read('forecast.json'), read('forecast-best.json')['question_ids'])
    (R/'data/skill-transition-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(audit['focused'],ensure_ascii=False,indent=2))
