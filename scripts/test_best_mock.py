"""Verify the fixed mock against canonical historical data and all candidates."""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))

mock = load('forecast-best.json')
forecast = load('forecast.json')
lookup = {q['id']: q for q in forecast}
chosen = [lookup[qid] for qid in mock['question_ids']]
assert set(mock['question_ids']) == {'P01','P02','P04','P05','P06','P08','P09','P10','P11','P20'}
assert len(chosen) == len({q['skill'] for q in chosen}) == 10
assert all(q['question_type']=='multiple-choice' and len(q['options'])==4 for q in chosen)
dates = [pair['b'] for pair in load('pairs.json')]
assert mock['b_dates'] == dates and len(set(dates)) == 7
exams = {date: {} for date in dates}
for q in load('bank.json')['questions']:
    for source in q['sources']:
        if source.get('date') in exams:
            exams[source['date']][source['num']] = q
targets = {}
for topic in mock['quotas']:
    targets[topic] = sum((Fraction(10 * sum(q['topic']==topic for q in exam.values()), len(exam))
                          for exam in exams.values()), Fraction()) / 7
quotas = {topic: int(value) for topic, value in targets.items()}
remaining = 10 - sum(quotas.values())
for topic in sorted(targets, key=lambda t: (-(targets[t]-quotas[t]), t))[:remaining]:
    quotas[topic] += 1
assert quotas == mock['quotas']
assert dict(Counter(q['topic'] for q in chosen)) == {t:n for t,n in quotas.items() if n}
assert mock['target_counts'] == {t:round(float(v),4) for t,v in targets.items()}
for topic, quota in quotas.items():
    # Independent reduction: highest-rated candidate per distinct skill first.
    best_by_skill = {}
    for q in forecast:
        if q['topic'] != topic:
            continue
        prior = best_by_skill.get(q['skill'])
        if prior is None or (-q['confidence'],q['id']) < (-prior['confidence'],prior['id']):
            best_by_skill[q['skill']] = q
    expected = sorted(best_by_skill.values(),key=lambda q:(-q['confidence'],q['id']))[:quota]
    assert {q['id'] for q in chosen if q['topic']==topic} == {q['id'] for q in expected}
print('Balanced mock: 10 fixed, distinct skills; seven B exams independently normalized; topic quotas and highest-confidence choices verified.')
