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
    # Exploratory weight perturbation: remove one component and rescale the
    # others proportionally to sum to 100; keep the extension penalty unchanged.
    # Components were saved to four decimal places by the production model.
    weight_tests=[]
    for component in ('latest_a','summer_b','skill_support'):
        weight=report['weights'][component]
        alternate_questions=deepcopy(questions)
        for q in alternate_questions:
            basis=q['confidence_basis']
            retained=sum(value for key,value in basis['components'].items() if key!=component)
            q['confidence']=max(1,min(100,round(retained*100/(100-weight)-basis['extension_deduction'])))
        alternate=select_mock(alternate_questions,report,pairs)
        weight_tests.append(dict(omitted_component=component,old_weight=weight,
            removed=sorted(set(base['question_ids'])-set(alternate['question_ids'])),
            added=sorted(set(alternate['question_ids'])-set(base['question_ids'])),
            scores={q['id']:q['confidence'] for q in alternate_questions}))
    return dict(base=base['question_ids'],scenarios=output,refits=refits,weight_tests=weight_tests,
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
    body+='''</tbody></table></div><h2>מה אם משנים את משקלי הציון?</h2><p>כדי לבדוק תלות בהנחות, הסרנו בכל פעם רכיב אחד מהציון וחילקנו מחדש את משקלו בין יתר הרכיבים באופן יחסי, כך שסך המשקלים נשאר 100. השתמשנו ברכיבי הציון שנשמרו בארבע ספרות אחרי הנקודה; ניכוי ההרחבה נשאר כפי שהיה. תמהיל הנושאים ושאר הנתונים נשארו קבועים. אלו שלושה תרחישים לדוגמה, לא חיפוש ממצה של כל המשקלים האפשריים.</p>
<div class="study-table"><table><thead><tr><th>רכיב שהוסר מהציון</th><th>מחוץ לסט החלופי</th><th>נוסף לסט החלופי</th></tr></thead><tbody>'''
    names={'latest_a':'בונוס מועד א׳ האחרון','summer_b':'שכיחות בשלושת מועדי ב׳ בקיץ','skill_support':'מספר תאריכי הסימוכין למיומנות'}
    for row in data['weight_tests']:
        body+=f'<tr><td>{escape(names[row["omitted_component"]])}</td><td>{linked(row["removed"])}</td><td>{linked(row["added"])}</td></tr>'
    return body+'''</tbody></table></div><p><a href="index.html?set=forecast-no-latest#setup">תרגול השאלות שנוספות כשמסירים את בונוס מועד א׳</a> · מספר השאלות עשוי להשתנות אם הציונים או המיפוי יעודכנו. זהו סט משלים, לא מבחן מלא או ראיה שהשיטה הזו טובה יותר.</p><p>התרחישים אינם מראים איזה משקל נכון יותר או מנבאים ציון בחינה. השאלות שמוחלפות הן אפשרויות גיבוי ללמידה. גם יציבות בבדיקות אלה אינה מבטיחה שהבחינה תדמה לסימולציה; תיוג אחר, משקלים נוספים או שינוי בבחינה יכולים לשנות את הבחירה.</p>
<p><a href="best-mock.html">הסימולציה הממוקדת ומקורותיה</a> · <a href="backtest.html">בדיקה בדיעבד לפי נושאים</a> · <a href="data/mock-sensitivity.json">נתוני התרחישים (JSON)</a></p>'''
