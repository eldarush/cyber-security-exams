"""Exploratory chronological assessment of ten-slot topic allocations."""
from datetime import datetime
from fractions import Fraction


def evaluate(report, pairs):
    matrix = report['exam_topics']
    topics = sorted(report['topic_stats'])
    date = lambda value: datetime.strptime(value, '%d/%m/%Y')

    def distribution(d):
        counts = matrix[d]
        total = sum(counts.values())
        return {topic: Fraction(10 * counts.get(topic, 0), total) for topic in topics}

    def apportion(values):
        quota = {topic: int(values[topic]) for topic in topics}
        order = sorted(topics, key=lambda topic: (-(values[topic] - quota[topic]), topic))
        for topic in order[:10 - sum(quota.values())]:
            quota[topic] += 1
        assert sum(quota.values()) == 10
        return quota

    rows = []
    for pair in pairs:
        earlier = sorted((p['b'] for p in pairs if date(p['b']) < date(pair['a'])), key=date)
        if not earlier:
            continue
        assert pair['b'] not in earlier and all(date(d) < date(pair['a']) for d in earlier)
        history = {t: sum((distribution(d)[t] for d in earlier), Fraction()) / len(earlier) for t in topics}
        current_a = distribution(pair['a'])
        combined = {t: (history[t] + current_a[t]) / 2 for t in topics}
        methods = {'history': history, 'recent': distribution(earlier[-1]),
                   'current_a': current_a, 'combined': combined}
        actual = distribution(pair['b'])
        quotas = {name: apportion(values) for name, values in methods.items()}
        overlap = {name: round(float(sum(min(Fraction(q[t]), actual[t]) for t in topics)) / 10, 6)
                   for name, q in quotas.items()}
        rows.append({'a': pair['a'], 'b': pair['b'], 'training_b': earlier,
                     'actual': {t: float(actual[t]) for t in topics}, 'quotas': quotas, 'overlap': overlap})
    assert rows
    means = {name: round(sum(row['overlap'][name] for row in rows)/len(rows), 6) for name in rows[0]['overlap']}
    return {'folds': rows, 'means': means,
            'description': 'Exploratory retrospective topic-count overlap, not question or skill prediction accuracy.'}
