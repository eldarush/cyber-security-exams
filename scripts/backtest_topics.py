"""Chronological exploratory topic backtest; never trains on the target B exam."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))
def date(s):
    return datetime.strptime(s, '%d/%m/%Y')

def evaluate():
    report, pairs = read('forecast-confidence.json'), read('pairs.json')
    topics, matrix = sorted(report['topic_stats']), report['exam_topics']
    rows = []
    for pair in pairs:
        cutoff = date(pair['a'])
        earlier = [d for d in matrix if date(d) < cutoff]
        earlier_b = [p['b'] for p in pairs if date(p['b']) < cutoff]
        assert pair['b'] not in earlier and pair['b'] not in earlier_b
        # The first case has no prior history; smoothing yields tied rankings.
        a = matrix[pair['a']]
        def freq(dates, t):
            return (sum(t in matrix[d] for d in dates)+1)/(len(dates)+2)
        rankings = {
            'past_all': {t:freq(earlier,t) for t in topics},
            'past_b': {t:freq(earlier_b,t) for t in topics},
            'current_a': {t:int(t in a) for t in topics},
            'hybrid': {t:(freq(earlier,t)+freq(earlier_b,t)+int(t in a))/3 for t in topics},
        }
        target = matrix[pair['b']]
        metrics = {}
        for name, scores in rankings.items():
            # Equal allocation among ties makes evaluation independent of topic names.
            threshold = sorted(scores.values(),reverse=True)[4]
            above = {t for t in topics if scores[t] > threshold}
            tied = {t for t in topics if scores[t] == threshold}
            tie_weight = (5-len(above))/len(tied)
            weights = {t:1 if t in above else tie_weight if t in tied else 0 for t in topics}
            hit = sum(weights[t] for t in target)/len(target)
            covered = sum(weights[t]*n for t,n in target.items())/sum(target.values())
            metrics[name] = dict(topic_recall=round(hit,6), question_coverage=round(covered,6))
        rows.append(dict(a=pair['a'],b=pair['b'],prior_exams=len(earlier),prior_b=len(earlier_b),
                         target_topics=len(target),metrics=metrics))
    return rows

if __name__ == '__main__':
    rows = evaluate()
    out = {'description':'Exploratory chronological broad-topic ranking; not a frozen prospective forecast or skill-level validation.',
           'rules':'Only exams strictly before the A date are used as historical data; A itself is known. Top five topic slots; ties fractionally averaged. Primary-topic labels were assigned retrospectively.',
           'folds':rows,'macro_means':{method:{metric:round(sum(row['metrics'][method][metric] for row in rows)/len(rows),4)
               for metric in ('topic_recall','question_coverage')} for method in rows[0]['metrics']}}
    path = ROOT / 'data' / 'topic-backtest.json'
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out['macro_means'],ensure_ascii=False,indent=2))
