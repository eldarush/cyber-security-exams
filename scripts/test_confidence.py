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
by_forecast={q['id']:q for q in forecast}
assert by_forecast['P15']['skill']=='second-preimage' and 'Q182' not in report['skills']['second-preimage']['evidence']
assert by_forecast['P17']['skill']=='csrf-cross-site' and 'Q180' not in report['skills']['csrf-cross-site']['evidence']
assert not by_forecast['P15']['confidence_basis']['latest_a_skill']
assert not by_forecast['P17']['confidence_basis']['latest_a_skill']
assert by_forecast['P05']['confidence_basis']['latest_a_skill']
for qid in ['P31','P35','P45']:
    assert not by_forecast[qid]['confidence_basis']['latest_a_skill'], qid
for qid in ['P35','P40','P45','P49','P56']:
    assert by_forecast[qid]['confidence_basis']['extension_deduction']==20, qid
assert report['skills']['service-name']['evidence']==[]
assert report['skills']['utxo-change']['evidence']==['Q176']
assert report['skills']['utxo-validity']['evidence']==['Q050','Q176']
assert report['skills']['utxo-outpoint']['evidence']==[]
assert report['skills']['confirmation-risk']['evidence']==['Q137','Q177']
assert by_forecast['P08']['skill']=='confirmation-risk'
assert by_forecast['P08']['confidence_basis']['skill_dates']==['02/11/2025','19/10/2026']
assert report['skills']['issuer-key']['evidence']==['Q174']
assert report['skills']['vigenere-encryption']['evidence']==['Q173']
assert report['skills']['ocsp-stapling-benefits']['evidence']==['Q073','Q101','Q170']
assert report['skills']['ocsp-forgery']['evidence']==['Q059','Q119']
for qid,skill in [('P02','issuer-key'),('P10','vigenere-encryption'),('P12','ocsp-stapling-benefits'),('P37','ocsp-forgery')]:
    assert by_forecast[qid]['skill']==skill
assert by_forecast['P03']['skill']=='utxo-change'
assert by_forecast['P40']['skill']=='utxo-validity'
assert by_forecast['P41']['skill']=='utxo-outpoint'
assert not by_forecast['P41']['confidence_basis']['latest_a_skill']
assert 'Q051' not in report['skills']['chain']['evidence']
assert by_forecast['P11']['skill']=='ct-policy' and by_forecast['P11']['confidence_basis']['latest_a_skill']
assert report['skills']['dh-calculation']['evidence']==['Q036','Q068','Q099','Q148','Q164']
assert by_forecast['P09']['skill']=='dh-calculation' and not by_forecast['P09']['confidence_basis']['latest_a_skill']
assert by_forecast['P55']['skill']=='dh-active' and report['skills']['dh-active']['evidence']==[]
assert by_forecast['P55']['confidence_basis']['extension_deduction']==20
assert by_forecast['P01']['skill']=='rsa-verify-numeric'
assert report['skills']['rsa-verify-numeric']['evidence']==['Q113','Q175']
assert by_forecast['P01']['confidence_basis']['skill_dates']==['21/08/2025','19/10/2026']
assert report['skills']['rsa-verify']['evidence']==['Q020','Q034','Q113','Q175']
assert by_forecast['P04']['skill']=='otp-malleability'
assert report['skills']['otp-malleability']['evidence']==['Q179']
assert by_forecast['P05']['skill']=='xss-token'
assert report['skills']['xss-token']['evidence']==['Q118','Q157','Q180']
assert by_forecast['P20']['skill']=='arp-mitm' and 'Q154' in report['skills']['arp-mitm']['evidence']
assert report['skills']['dns-guess']['evidence']==['Q030','Q052']
assert report['skills']['slowloris']['evidence']==['Q002']
for qid in ['P20','P29','P30']:
    assert by_forecast[qid]['confidence_basis']['extension_deduction']==20
for qid,skill in [('P36','ca-constraints'),('P38','ct-promise'),('P39','ct-split-view')]:
    assert by_forecast[qid]['skill']==skill and report['skills'][skill]['evidence']==[]
    assert not by_forecast[qid]['confidence_basis']['latest_a_skill']
    assert by_forecast[qid]['confidence_basis']['extension_deduction']==20
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
# Independently reconstruct each reduced score from the original bank rather
# than using annotate(): no omitted date may contribute to any component.
for refit in load('data/mock-sensitivity.json')['refits']:
    omitted=refit['omitted_b']
    reduced_topics={d:t for d,t in topics.items() if d!=omitted}
    reduced_pairs=[p for p in pairs if p['b']!=omitted]
    reduced_summer=[p for p in reduced_pairs if 'קיץ' in p['label']]
    assert len(reduced_topics)==17 and len(reduced_pairs)==6
    for q in forecast:
        topic=q['topic']
        n_all=sum(topic in t for t in reduced_topics.values())
        n_a=sum(topic in reduced_topics[p['a']] for p in reduced_pairs)
        n_b=sum(topic in reduced_topics[p['b']] for p in reduced_pairs)
        n_both=sum(topic in reduced_topics[p['a']] and topic in reduced_topics[p['b']] for p in reduced_pairs)
        n_summer=sum(topic in reduced_topics[p['b']] for p in reduced_summer)
        support={s['date'] for qid in report['skills'][q['skill']]['evidence'] for s in by_id[qid]['sources']
                 if s.get('date') and s['date']!=omitted}
        score=round(15*(n_all+1)/(len(reduced_topics)+2) + 25*(n_b+1)/(len(reduced_pairs)+2)
            +15*(n_both+1)/(n_a+2)+15*(n_summer+1)/(len(reduced_summer)+2)
            +20*min(len(support)/6,1)+10*('19/10/2026' in support)-q['confidence_basis']['extension_deduction'])
        assert refit['scores'][q['id']]==max(1,min(100,score)),(omitted,q['id'])
print('Confidence: all 60 scores independently recomputed; 18 unique dates, 186 occurrences, seven pairs, three summer pairs verified.')
