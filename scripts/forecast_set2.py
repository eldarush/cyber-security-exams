"""Build the second forecast bank from newly written variants and dated evidence."""
from html import escape

from forecast_set2_questions import questions


RECENT_YEARS = {'2024', '2025', '2026'}


def build_set2(original, pairs):
    parents = {q['id']: q for q in original}
    recent_pairs = [(a, b) for _, a, b, _ in pairs if b[-4:] in RECENT_YEARS]
    items = []

    def add(parent_id, title, stem, options, correct, derivation, reasons):
        parent = parents[parent_id]
        basis = parent['confidence_basis']
        dates = set(basis['skill_dates'])
        recent = sorted(d for d in dates if d[-4:] in RECENT_YEARS)
        recent_b = [b for _, b in recent_pairs if b in dates]
        transitions = [(a, b) for a, b in recent_pairs if a in dates and b in dates]
        latest = basis['latest_a_skill']
        score = parent['confidence']
        assert score > 60 and len(set(options)) == len(reasons) == 4
        order = [correct] + [i for i in range(4) if i != correct]
        options, reasons = [options[i] for i in order], [reasons[i] for i in order]
        correct = 0
        number = len(items) + 1
        qid = f'B2-{number:02}'
        reviews = [dict(option=option, correct=i == correct, reason=reasons[i]) for i, option in enumerate(options)]
        body = '<section class="forecast-review"><h3>דרך הפתרון</h3><p>'+escape(derivation)+'</p>'
        body += '<h3>בדיקת החלופות</h3>'
        for i, review in enumerate(reviews):
            label = 'נכונה' if review['correct'] else 'שגויה'
            body += f'<div class="option-review" data-option-review="{i}"><h4>{label} — {escape(review["option"])}</h4><p>{escape(review["reason"])}</p></div>'
        items.append(dict(id=qid, title=title, stem=stem, options=options,
            accepted_indices=[correct], option_explanations=reviews, answer_html=body+'</section>',
            topic=parent['topic'], skill=parent['skill'], parent_id=parent_id,
            history_ids=[parent_id, *basis['skill_evidence']], year='תרגול',
            recent_skill_dates=recent, recent_b_dates=recent_b, skill_transitions=transitions,
            latest_a_skill=latest, topic_transitions=basis['topic_counts']['both'],
            confidence=score, confidence_kind=parent['confidence_kind'],
            selection_score=score + len(recent) + 2*len(recent_b) + 2*len(transitions) + 3*latest,
            question_type='multiple-choice', exclude=False, flags=[], fixed_order=False,
            sources=[dict(file='predictions-2.html', date=None, num=number)],
            answer_origin='סט 2 · שאלת תרגול מקורית בסגנון הבחינות',
            solution=f'solutions/{qid}.html'))

    questions(add)
    assert len(items) == len({q['stem'] for q in items}) == 60
    return items


def evidence_line(q, prefix=''):
    recent = ', '.join(q['recent_skill_dates']) or 'אין מיפוי ישיר'
    latest = 'מופיעה גם במועד א׳ של אוקטובר 2026' if q['latest_a_skill'] else 'מתועדת במועדים אחרים'
    return (f'<p class="study-source">ציון המיומנות <b>{q["confidence"]}/100</b> · '
            f'{latest} · תאריכי מיומנות ממופים ב-2024–2026: {recent} · '
            f'{len(q["recent_b_dates"])} מועדי ב׳ מתועדים ו-{len(q["skill_transitions"])} מעברי מיומנות בתוך זוג א׳/ב׳. '
            f'<a href="{prefix}solutions/{q["parent_id"]}.html">התרגיל הראשון ומקורות המיפוי</a></p>')
