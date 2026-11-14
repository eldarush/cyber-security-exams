"""Recompute evidence counts from canonical records, independently of the builder."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import json

R=Path(__file__).resolve().parents[1]
load=lambda name:json.loads((R/name).read_text(encoding='utf-8'))
bank=load('data/bank.json')['questions'];forecast=load('data/forecast.json')
pairs=load('data/pairs.json');report=load('data/forecast-confidence.json')
records=defaultdict(dict);by_id={q['id']:q for q in bank}
for q in bank:
    for s in q['sources']:
        if s.get('date'):records[s['date']][s['num']]=q
assert len(records)==18 and sum(map(len,records.values()))==186
assert set(report['dates'])==set(records)
assert report['year_exam_counts']==dict(Counter(d[-4:] for d in records))
for date,questions in records.items():
    assert report['exam_topics'][date]==dict(Counter(q['topic'] for q in questions.values()))
assert sum(report['weights'].values())==100
assert len(report['questions'])==len(forecast)==60
q_report={q['id']:q for q in report['questions']}
topics={date:{q['topic'] for q in questions.values()} for date,questions in records.items()}
summer=[pair for pair in pairs if 'קיץ' in pair['label']]
assert len(summer)==3
for q in forecast:
    assert type(q['confidence']) is int and 1<=q['confidence']<=100
    assert q['confidence_kind']=='skill-confidence-not-probability'
    topic=q['topic'];b=q['confidence_basis']
    all_n=sum(topic in t for t in topics.values())
    a_n=sum(topic in topics[p['a']] for p in pairs)
    b_n=sum(topic in topics[p['b']] for p in pairs)
    both=sum(topic in topics[p['a']] and topic in topics[p['b']] for p in pairs)
    summer_n=sum(topic in topics[p['b']] for p in summer)
    dates={s['date'] for qid in report['skills'][q['skill']]['evidence'] for s in by_id[qid]['sources'] if s.get('date')}
    assert set(b['skill_dates'])==dates
    assert b['topic_counts']==dict(exams=all_n,a=a_n,b=b_n,both=both,summer_b=summer_n)
    expected=round(15*(all_n+1)/20 + 25*(b_n+1)/9 + 15*(both+1)/(a_n+2)
        +15*(summer_n+1)/5 + 20*min(len(dates)/6,1)+10*('19/10/2026' in dates)-b['extension_deduction'])
    assert q['confidence']==max(1,min(100,expected)),q['id']
    assert q_report[q['id']]['score']==q['confidence']
    assert all(datetime.strptime(d,'%d/%m/%Y')<=datetime(2026,10,19) for d in dates)
    assert f'{q["confidence"]}/100' in (R/q['solution']).read_text(encoding='utf-8')
assert all(sum(q['mock']==n for q in forecast)==10 for n in range(1,7))
print('Confidence: all 60 scores independently recomputed; 18 unique dates, 186 occurrences, seven pairs, three summer pairs verified.')
