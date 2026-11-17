"""Manually reviewed examples of operation changes in the last three A/B pairs."""
from html import escape

# These are selected examples, not exhaustive coding of all 30 B questions.
EXAMPLES = [
 ('יולי→אוגוסט 2025','Q105','Q113','אותם פרמטרי RSA פרטיים: יצירת חתימה בא׳ מול חיפוש ההודעה המקורית מחתימה בב׳.','P01 P31'),
 ('יולי→אוגוסט 2025','Q108','Q119','שאלת א׳ עוסקת בתפקיד OCSP stapling; שאלת ב׳ עוסקת בהמשך קבלת תעודה שבוטלה בעת בעיית תקשורת. הקשר הוא בדיקת סטטוס, ולא אותה השאלה.','P12 P37'),
 ('אוקטובר→נובמבר 2025','Q129','Q139','ממטרת שקיפות הרישום של CT לתנאי SCT שבאמצעותו דפדפן אוכף CT.','P11 P38'),
 ('אוקטובר→נובמבר 2025','Q130','Q140','מהגדרת preimage עבור digest נתון להגדרת second preimage עבור הודעה מקורית נתונה.','P15 P50'),
 ('אוקטובר→נובמבר 2025','Q127','Q137','ממגבלות לקוח ביטקוין בהתמודדות עם fork לשאלת אישורים ו-double spending; קשר רחב של קונצנזוס ולא תרגיל זהה.','P08'),
 ('יולי→אוגוסט 2026','Q153','Q163','מתפקיד MAC לשלמות ואימות מקור לזיהוי Encrypt-then-MAC לפי סדר הבדיקה והפענוח.','P06'),
 ('יולי→אוגוסט 2026','Q159','Q165','מספירת hashes בהוכחת מרקל למטרה של הוכחת הכללה ללקוח קל.','P14 P44'),
 ('יולי→אוגוסט 2026','Q154','Q171','מהיכולת שמתקבלת בהרעלת ARP לפעולה שתוקף בעל יכולת MITM יכול לבצע. ב׳ אינו דורש שה-MITM הושג דווקא באמצעות ARP.','P20'),
 ('יולי→אוגוסט 2026','Q156','Q170','מאכיפת CT באמצעות SCT לפרטיות מול OCSP stapling: שני מנגנונים שונים בתשתית התעודות, לא חזרה על אותה מיומנות.','P11 P12'),
]

def operation_page(bank,forecast):
    known={q['id'] for q in bank}; predicted={q['id'] for q in forecast}
    body='''<p class="study-intro"><strong>דוגמאות שנבחרו ידנית משלושת הזוגות האחרונים, לא רשימה מלאה ולא מדידת דיוק.</strong> הקשר בין השאלות משתנה: לפעמים אותה פעולה מתהפכת, לפעמים מדובר במנגנונים שונים באותו תחום.</p>
<p>כל שורת תרגול היא המלצה ללימוד המנגנון, לא טענה שהנוסח או המספרים יופיעו שוב. הקישורים פותחים את השאלות והפתרונות באתר; סדר התשובות מתערבב.</p><div class="study-table"><table><thead><tr><th>זוג</th><th>מועד א׳</th><th>מועד ב׳</th><th>מה השתנה</th><th>תרגול</th></tr></thead><tbody>'''
    for pair,a,b,description,exercise in EXAMPLES:
        assert a in known and b in known
        assert set(exercise.split())<=predicted
        links=' · '.join(f'<a href="predictions.html#{id}">{id}</a>' for id in exercise.split())
        body+=f'<tr><td>{escape(pair)}</td><td><a href="solutions/{a}.html">{a}</a></td><td><a href="solutions/{b}.html">{b}</a></td><td>{escape(description)}</td><td>{links}</td></tr>'
    return body+'''</tbody></table></div><p>הדוגמאות נבחרו לאחר צפייה בשאלות א׳ וב׳. אין לספור אותן כשכיחות של כל סוגי השאלות או להסיק מהן ציון ביטחון מכויל. בפרט, שאלת ב׳ יכולה לבדוק גם נושאים שכלל לא הופיעו בא׳.</p><p><a href="analysis.html">ניתוח כל שבעת הזוגות</a> · <a href="backtest.html">בדיקה בדיעבד ומגבלותיה</a> · <a href="index.html?set=forecast-best#setup">הסימולציה הממוקדת</a></p>'''
