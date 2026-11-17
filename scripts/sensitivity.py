"""Sensitivity of mock topic allocation with question scores held fixed."""
from html import escape
from forecast_mock import select_mock


def allocation_sensitivity(questions, report, pairs):
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
    return dict(base=base['question_ids'],scenarios=output,
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
    return body+'''</tbody></table></div><p>השאלה או השתיים שמוחלפות הן אפשרויות תרגול נוספות, לא הוכחה שתמהיל חלופי עדיף. מספר קטן של הבדלים תחת הבדיקה המוגבלת הזו אינו מבטיח שהבחינה תדמה לסימולציה; גם משקלים אחרים, סיווג אחר, שינוי במרצה או באופן השאלות יכולים לשנות את הבחירה. הסרת מועד אחד בודקת רגישות לנתון, ולא מאמתת תחזית עתידית.</p>
<p><a href="best-mock.html">הסימולציה הממוקדת ומקורותיה</a> · <a href="backtest.html">בדיקה בדיעבד לפי נושאים</a> · <a href="data/mock-sensitivity.json">נתוני התרחישים (JSON)</a></p>'''
