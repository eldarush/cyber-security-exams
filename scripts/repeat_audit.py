"""Exact canonical-record matching against exams available by each A sitting."""
from collections import defaultdict
from datetime import datetime
from html import escape
import re

def date(d): return datetime.strptime(d,'%d/%m/%Y')
def key(q):
    clean=lambda s:re.sub(r'\s+',' ',s).strip()
    return clean(q['stem']),tuple(sorted(clean(o) for o in q['options']))

def repeated_questions(bank,pairs):
    folds=[]
    for label,a,b,_ in pairs:
        prior=defaultdict(set)
        for q in bank:
            for source in q['sources']:
                d=source.get('date')
                if d and date(d)<=date(a): prior[key(q)].add((q['id'],d))
        b_records={s['num']:q for q in bank for s in q['sources'] if s.get('date')==b}
        matches=[]
        for number,q in sorted(b_records.items()):
            hits=sorted(prior.get(key(q),set()), key=lambda x:(date(x[1]),x[0]))
            if hits:
                matches.append(dict(id=q['id'],number=number,prior=[dict(id=i,date=d) for i,d in hits]))
        folds.append(dict(label=label,a=a,b=b,count=len(b_records),matches=matches))
    return dict(method='Whitespace-normalized full stem plus sorted full option texts in the canonical bank; earlier source dates <= A date; no semantic or OCR matching.',
                count=sum(f['count'] for f in folds),match_count=sum(len(f['matches']) for f in folds),folds=folds)

def repeat_section(report):
    body='''<h2>האם שאלות ברירה חזרו ממבחנים קודמים?</h2><p>בכל זוג השווינו כל שאלה בב׳ לשאלות ברירה מתוארכות שהיו זמינות לכל המאוחר במועד א׳. בדיקה זו משתמשת ברשומה הקנונית של האתר: נוסח מלא וכל ארבע החלופות אחרי נרמול רווחים, ללא תלות בסדר החלופות. לא נכללו מקורות ללא תאריך או שאלות פתוחות. זו אינה השוואת PDF אוטומטית ואינה מזהה פרפרזה, שינוי פרמטרים או שינוי קטן אחר.</p>'''
    body+=f'<p>נמצאו {report["match_count"]} התאמות מתוך {report["count"]} הופעות של שאלות ברירה בשבעת מועדי ב׳; שתיהן באותו מועד ב׳. אלו אינם ניסויים בלתי תלויים ואין להסיק מהם הסתברות לחזרה בבחינה הבאה.</p><div class="study-table"><table><thead><tr><th>זוג</th><th>חזרות קנוניות</th><th>ראיות</th></tr></thead><tbody>'
    for f in report['folds']:
        links=' · '.join(f'<a href="solutions/{m["id"]}.html">{m["id"]}</a>' for m in f['matches']) or 'אין התאמה בבדיקה זו'
        body+=f'<tr><td>{escape(f["label"])}</td><td>{len(f["matches"])}/{f["count"]}</td><td>{links}</td></tr>'
    return body+'''</tbody></table></div><p>שני המקרים הם שאלות על ARP poisoning ועל ECB; שתיהן הופיעו במאי 2024 ובמועד ב׳ של אוקטובר 2024. אפשר לבדוק במסמכי המקור: <a href="2024/689156_31052024_0.docx%20%282%29.pdf#page=3">ECB במאי, עמוד 3</a> · <a href="2024/689156_31052024_0.docx%20%282%29.pdf#page=5">ARP במאי, עמוד 5</a> · <a href="2024/689156_04_20102024_0%203.pdf#page=4">שתיהן באוקטובר, עמוד 4</a>. המיון מחדש באתר נועד לתרגול; שינון אות התשובה אינו בדיקה של הבנת המנגנון.</p>
<h3>דוגמאות לחזרות קרובות שהספירה המדויקת מפספסת</h3><ul>
<li>מועד ב׳ בנובמבר 2025 ומועד ב׳ באוגוסט 2026 הציגו את אותו פסאודו־קוד של בדיקת MAC על ciphertext לפני פענוח, אך שינו את ניסוח השאלה ואת אחת החלופות. <a href="solutions/Q133.html">Q133</a> · <a href="solutions/Q163.html">Q163</a> · <a href="predictions.html#P06">P06 לתרגול המנגנון</a>.</li>
<li>מועד מיוחד בנובמבר 2025 ומועד ב׳ באוגוסט 2026 השתמשו באותם ערכי DH: מודולוס 23, בסיס 3 וערכים פומביים 13 ו-4. הניסוח ואחת החלופות השתנו. <a href="solutions/Q148.html">Q148 — מועד מיוחד</a> · <a href="solutions/Q164.html">Q164 — מועד ב׳</a> · <a href="predictions.html#P09">P09 לתרגול אותו חישוב</a>.</li>
<li>נוסח ארוך על אליס, בוב וחווה מאזינה חזר כמעט ללא שינוי מדצמבר 2022 לאוגוסט 2023, אבל החלופות השתנו: במקרה אחד האפשרות הלא בטוחה מצפינה במפתח הפומבי של השולח, ובאחר נשלח מפתח סימטרי בערוץ הגלוי. <a href="solutions/Q025.html">Q025 — דצמבר 2022</a> · <a href="solutions/Q056.html">Q056 — מועד ב׳ באוגוסט 2023</a> · <a href="predictions.html#P33">P33 — תפקידי מפתחות</a>. חשוב לבחון את האפשרויות בכל גרסה.</li>
<li>שאלה על אי־התכחשות הופיעה בנוסח דומה ב-2022 ובמועד ב׳ של אוקטובר 2024; אחת הגרסאות מתארת את התחום הרחב של קריפטוגרפיה פומבית והשנייה את המנגנון המסוים, חתימה דיגיטלית. <a href="solutions/Q009.html">Q009 — אוקטובר 2022</a> · <a href="solutions/Q092.html">Q092 — אוקטובר 2024</a> · <a href="predictions.html#P33">P33 לתרגול חתימה וסודיות</a>.</li>
</ul><p>אלה דוגמאות ידניות נבחרות ולא חיפוש ממצה של חזרות קרובות. לכן 2 מתוך 72 הוא מספר ההתאמות <strong>הזהות לפי הכלל המצומצם לעיל בלבד</strong>, ואינו מספר כל השאלות המבוססות על שאלה קודמת. גם מציאת שתי דוגמאות נוספות אינה אומדן אמין להסתברות שאלה בבחינה העתידית.</p><p><a href="data/repeat-audit.json">ההתאמות והגדרות הבדיקה (JSON)</a></p>'''
