"""Exploratory chronological comparison using retrospective, incomplete skill labels."""
from datetime import datetime

def evaluate(bank, forecast, pairs, report):
    matrix = report['exam_topics']
    byid = {q['id']: q for q in bank}
    date = lambda value: datetime.strptime(value, '%d/%m/%Y')
    support = {k: {s['date'] for qid in v['evidence'] for s in byid[qid]['sources'] if s.get('date')}
               for k, v in report['skills'].items()}
    rows = []
    for pair in pairs:
        a, b = pair['a'], pair['b']
        dates = sorted((d for d in matrix if date(d) <= date(a)), key=date)
        prior = [p for p in pairs if date(p['b']) < date(a)]
        summer = [p for p in prior if 'קיץ' in p['label']]
        assert b not in dates and all(date(p['b']) < date(a) for p in prior)
        scored = []
        for q in forecast:
            t, skill = q['topic'], q['skill']
            all_n = sum(t in matrix[d] for d in dates)
            a_n = sum(t in matrix[p['a']] for p in prior)
            b_n = sum(t in matrix[p['b']] for p in prior)
            both = sum(t in matrix[p['a']] and t in matrix[p['b']] for p in prior)
            summer_n = sum(t in matrix[p['b']] for p in summer)
            seen = sum(date(d) <= date(a) for d in support[skill])
            base = (15*(all_n+1)/(len(dates)+2) + 25*(b_n+1)/(len(prior)+2)
                    + 15*(both+1)/(a_n+2) + 15*(summer_n+1)/(len(summer)+2)
                    + 20*min(seen/6, 1))
            scored.append((q['id'], skill, base, q['confidence_basis']['extension_deduction'], a in support[skill]))
        def select(with_bonus):
            def score(row):
                raw = row[2] + (10 if row[4] else 0) if with_bonus else row[2]*100/90
                return max(1, min(100, round(raw-row[3])))
            seen, selected = set(), []
            for row in sorted(scored, key=lambda r: (-score(r), r[0])):
                if row[1] not in seen:
                    selected.append(row)
                    seen.add(row[1])
                if len(selected) == 10:
                    break
            assert len(selected) == 10
            return selected
        bonus, no_bonus = select(True), select(False)
        targets = sorted({q['skill'] for q in forecast if b in support[q['skill']]})
        rows.append(dict(a=a, b=b, history_dates=dates, prior_b=[p['b'] for p in prior],
            mapped_target_skills=targets,
            bonus_ids=[x[0] for x in bonus], no_bonus_ids=[x[0] for x in no_bonus],
            bonus_hits=sum(x[1] in targets for x in bonus),
            no_bonus_hits=sum(x[1] in targets for x in no_bonus)))
    return dict(description='Retrospective incomplete skill mappings; chronological score inputs only. Not prospective validation.',
                folds=rows, bonus_hits=sum(r['bonus_hits'] for r in rows),
                no_bonus_hits=sum(r['no_bonus_hits'] for r in rows))
