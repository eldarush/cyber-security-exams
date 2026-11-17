"""Sensitivity of mock topic allocation with question scores held fixed."""
from html import escape
from copy import deepcopy
from forecast_mock import select_mock
from forecast_confidence import annotate


def allocation_sensitivity(questions, report, pairs, bank):
    base=select_mock(questions,report,pairs)
    scenarios=[('ללא מועד ב׳ '+b,[p for p in pairs if p[2]!=b]) for _,_,b,_ in pairs]
    scenarios.append(('רק שלושת זוגות הקיץ',[p for p in pairs if 'קיץ' in p[0]]))
    output=[]
    for label,subset in scenarios:
        alternate=select_mock(questions,report,subset)
        output.append(dict(label=label,b_dates=[p[2] for p in subset],
            removed=sorted(set(base['question_ids'])-set(alternate['question_ids'])),
            added=sorted(set(alternate['question_ids'])-set(base['question_ids'])),
            quotas=alternate['quotas']))
    # Remove every occurrence from that date (including duplicate source files),
    # then recompute topic statistics and skill-support dates, as well as quotas.
    # Other dated occurrences of a shared canonical question are retained.
    refits=[]
    for pair in pairs:
        excluded=pair[2]
        reduced_bank=deepcopy(bank)
        for q in reduced_bank:
            q['sources']=[s for s in q['sources'] if s.get('date') != excluded]
        reduced_pairs=[p for p in pairs if p[2]!=excluded]
        reduced_questions=deepcopy(questions)
        new_report=annotate(reduced_questions,reduced_bank,reduced_pairs)
        assert excluded not in new_report['dates'] and len(new_report['dates'])==len(report['dates'])-1
        assert all(excluded not in q['confidence_basis']['skill_dates'] for q in reduced_questions)
        alternate=select_mock(reduced_questions,new_report,reduced_pairs)
        new_scores={q['id']:q['confidence'] for q in reduced_questions}
        old_scores={q['id']:q['confidence'] for q in questions}
        refits.append(dict(omitted_b=excluded,removed=sorted(set(base['question_ids'])-set(alternate['question_ids'])),
            added=sorted(set(alternate['question_ids'])-set(base['question_ids'])),
            scores=new_scores,changed_score_count=sum(new_scores[k]!=old_scores[k] for k in new_scores)))
    return dict(base=base['question_ids'],scenarios=output,refits=refits,
        scope='Topic allocation only; current question scores, mappings and historical counts used in scores are held fixed. Not a full refit.')


def sensitivity_page(data,questions):
    titles={q['id']:q['title'] for q in questions}
    def linked(ids):
        return ' · '.join(f'<a href="predictions.html#{i}">{i} — {escape(titles[i])}</a>' for i in ids) if ids else 'ללא שינוי'
    body='''<p class="study-intro"><strong>בדיקת רגישות לתמהיל הנושאים, לא מדידת הסתברות או דיוק.</strong> מטרתה להראות עד כמה בחירת עשר השאלות תלויה בשבעת מועדי ב׳ שעליהם מבוססת הקצאת המקומות.</p>
<h2>מה בדקנו?</h2><p>חישבנו מחדש את ממוצע הנושאים ואת עיגול עשרת המקומות, פעם לאחר הסרת כל אחד משבעת מועדי ב׳, ופעם תוך שימוש בשלושת מועדי ב׳ של קיץ בלבד. בכל תרחיש נבחרות השאלות בעלות הציון הגבוה לפי אותו כלל ובאותו מנגנון הכרעת תיקו של הסימולציה הממוקדת.</p>
<p><strong>מגבלה מהותית:</strong> ציוני השאלות והמיפוי נשארים קבועים בכל התרחישים, והם עצמם מחושבים מכל 18 הבחינות ושבעת הזוגות. לכן תרחיש ״ללא מועד״ מסיר אותו רק מחישוב התמהיל; הוא אינו מסיר את השפעתו מהציונים ואינו בדיקת leave-one-out מלאה של המודל.</p>
<div class="study-table"><table><thead><tr><th>תרחיש לתמהיל בלבד</th><th>שאלות מהסט הרגיל שלא נבחרות</th><th>שאלות נוספות שנבחרות</th></tr></thead><tbody>'''
    for row in data['scenarios']:
        body+=f'<tr><td>{escape(row["label"])}</td><td>{linked(row["removed"])}</td><td>{linked(row["added"])}</td></tr>'
    body+='''</tbody></table></div><h2>חישוב מחדש של הציונים והתמהיל יחד</h2><p>כאן הסרנו כל מועד ב׳ בנפרד מכל מקורות השאלות המתוארכים, כולל עותקי מקור כפולים, וגם הסרנו את הזוג שלו מהחישוב. חישבנו מחדש את שכיחויות הנושאים, מועדי הסימוכין למיומנויות, ציוני כל 60 השאלות והקצאת הנושאים. מועד א׳ של אותו זוג נשאר במאגר הכללי; זוג א׳/ב׳ אינו נספר בהיעדר ב׳. התרחישים משמרים את משקלי הנוסחה, מפת המיומנויות שנקבעה בדיעבד, הנחות המודל ומועד א׳ האחרון. זהו ניתוח רגישות לנתונים, לא חיזוי שהוקפא לפני הבחינה ולא בדיקת דיוק.</p>
<div class="study-table"><table><thead><tr><th>מועד ב׳ שהוסר גם מהציונים</th><th>שאלות שהוחלפו</th><th>שאלות שנוספו</th><th>ציונים שהשתנו מתוך 60</th></tr></thead><tbody>'''
    for row in data['refits']:
        body+=f'<tr><td>{escape(row["omitted_b"])}</td><td>{linked(row["removed"])}</td><td>{linked(row["added"])}</td><td>{row["changed_score_count"]}</td></tr>'
    return body+'''</tbody></table></div><p>החלופות הן אפשרויות תרגול נוספות, לא הוכחה שתמהיל חלופי עדיף. גם יציבות בשני סוגי הבדיקה אינה מבטיחה שהבחינה תדמה לסימולציה; משקלים אחרים, תיוג אחר ושינויים בבחינה יכולים לשנות את הבחירה.</p>
<p><a href="best-mock.html">הסימולציה הממוקדת ומקורותיה</a> · <a href="backtest.html">בדיקה בדיעבד לפי נושאים</a> · <a href="data/mock-sensitivity.json">נתוני התרחישים (JSON)</a></p>'''
