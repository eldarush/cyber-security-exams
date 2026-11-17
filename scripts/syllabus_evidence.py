"""Scope and supplemental exercise from the user-provided summer 2026 syllabus.

The source PDF is private and is not copied into the public build. The syllabus
is course scope, not a retake-specific exclusion list or prediction frequency.
"""
from html import escape
from lecture_evidence import LECTURES

QUESTION = {
    'id':'S01', 'accepted_indices':[0],
    'stem':'אתר בנק אינו מעוניין שדפיו יוצגו בתוך iframe של אתר אחר. תוקף מנסה להטעות משתמש ללחוץ על כפתור בדף הבנק המוטמע בשכבה מוסווית. איזו הגדרת תגובת HTTP מצד הבנק מיועדת למנוע את ההטמעה הזו בדפדפן שתומך בה?',
    'options':[
        "Content-Security-Policy: frame-ancestors 'none'",
        'Strict-Transport-Security: max-age=31536000',
        'הגדרת HttpOnly בעוגיית הסשן בלבד',
        'הוספת X-Frame-Options: DENY לתגובה של אתר התוקף בלבד',
    ],
    'reasons':[
        'הוראת frame-ancestors בתגובה של דף הבנק מגבילה מי רשאי להטמיע אותו. הערך none אוסר כל הורה מוטמע בדפדפן התומך בה, וכך חוסם את מסגרת התקיפה המתוארת.',
        'HSTS מכוון את הדפדפן להשתמש ב-HTTPS עבור האתר בהתאם למדיניותו; הוא אינו מגדיר אילו דפים רשאים להטמיע את דף הבנק ואינו חוסם clickjacking כשלעצמו.',
        'HttpOnly מגביל גישת JavaScript לעוגייה; הוא אינו מונע מאתר התוקף להציג iframe של דף הבנק ואינו מונע לחיצה של המשתמש על ממשק מוטעה.',
        'X-Frame-Options יכול להגביל הטמעה כשהוא נשלח בתגובה של הדף המוגן. כותרת בתגובת אתר התוקף בלבד אינה מגדירה את מדיניות ההטמעה של דף הבנק.',
    ],
}

def syllabus_intro():
    return '''<p class="study-intro"><strong>בדיקת כיסוי לפי הסילבוס שסופק.</strong> המסמך מציין קורס 689156, תשפ״ו, סמסטר קיץ; תוכנית הנושאים בעמודים 2–3. הוא אינו רשימת שאלות עתידיות ואינו קובע שקלול נושאים או החרגות מיוחדות למועד ב׳.</p>
<h2>בדיקת דף הקורס ומאגר התרגול</h2><p>בבדיקה ב-17/11/2026, <a href="https://moodle.colman.ac.il/2026/course/section.php?id=33261">דף הקורס של סמסטר קיץ</a> הציג פורמט של 10 שאלות אמריקאיות, ללא חומר עזר. <a href="https://moodle.colman.ac.il/2026/mod/forum/discuss.php?d=50580">הודעת המרצה מ-15/10</a> תיארה שיעור חזרה לפני מועד א׳ המבוסס על מאגר שאלות ממבחני עבר. אין בכך הודעה מאומתת על תנאים או נושאים מיוחדים למועד ב׳.</p>
<p>רשימת 26 שמות הקבצים ב<a href="https://moodle.colman.ac.il/2026/mod/folder/view.php?id=111395">תיקיית התרגול בקורס</a> תאמה את 26 שמות הקבצים בתיקייה המקורית שסופקה. זו התאמת שמות בלבד: תכולת קובצי Moodle לא הושוותה בבייטים לעותקים המקומיים. לוח ההודעות שנבדק לא הכיל הודעה חדשה יותר בנושא מועד ב׳; ייתכן שקיים מידע בערוץ אחר. קישורי הקורס עשויים לדרוש הרשאת סטודנט.</p>
<p>מסמך הסילבוס עצמו נשאר אצל המשתמש; להלן סיכום הנושאים והפניות לתרגול. חזרתיות מילולית בטבלה שבסילבוס אינה נספרת כראיה למספר שאלות או כמשקל נפרד.</p>
<div class="study-table"><table><thead><tr><th>משפחת נושאים בסילבוס</th><th>תרגול באתר</th><th>גבולות ההסקה</th></tr></thead><tbody>
<tr><td>מודלי תוקף, כולל off-path ו-MITM</td><td><a href="predictions.html#P20">P20 — מיקום בתעבורה</a> · <a href="predictions.html#P55">P55 — DH לא מאומת</a></td><td>שני המונחים מופיעים בסילבוס; הוא לא אומר ששילוב מסוים יופיע בבחינה.</td></tr>
<tr><td>צפנים היסטוריים, הצפנה, חתימות ו-hash</td><td><a href="predictions.html#P10">P10</a> · <a href="predictions.html#P01">P01</a> · <a href="predictions.html#P15">P15</a></td><td>הסילבוס אינו מונה את כל האלגוריתמים או מבטיח נוסחה מסוימת.</td></tr>
<tr><td>Bitcoin ובלוקצ׳יין</td><td><a href="predictions.html#P03">P03</a> · <a href="predictions.html#P08">P08</a> · <a href="predictions.html#P14">P14</a></td><td>דוגמאות תרגול מתוך נושא רחב, לא התפלגות רשמית.</td></tr>
<tr><td>PKI, החלפת מפתחות ו-TLS</td><td><a href="predictions.html#P02">P02</a> · <a href="predictions.html#P09">P09</a> · <a href="predictions.html#P19">P19</a></td><td>הסילבוס אינו מציין באיזו גרסת TLS תעסוק שאלה מסוימת.</td></tr>
<tr><td>Web: עוגיות, SOP, SQL injection, XSS, XSRF ו-clickjacking</td><td><a href="predictions.html#P05">P05</a> · <a href="predictions.html#P17">P17</a> · <a href="predictions.html#P28">P28</a> · שאלה משלימה בהמשך</td><td>clickjacking מופיע במפורש בסילבוס; בבנק ההיסטורי שמופה אין שאלה ייעודית מזוהה עליו.</td></tr>
<tr><td>ARP, DNS, TCP, DoS/DDoS, botnets וכלים</td><td><a href="predictions.html#P20">P20</a> · <a href="predictions.html#P29">P29</a> · <a href="predictions.html#P30">P30</a></td><td>התרגול אינו מכסה בהכרח כל כלי או וריאציה, כולל הנושאים המוזכרים בסילבוס.</td></tr>
</tbody></table></div>
<h2 id="lecture-evidence">סימוכין במצגות מהתיקייה המקומית</h2><p>הקבצים הבאים נמצאו בתיקייה שסופקה. מספרי העמודים הם עמודי PDF, לא מספרי שקופית. מהדורת המצגות והתאמתן המלאה לסמסטר הנוכחי לא אומתו. המצגות נשארות מקומיות ואינן מועלות לאתר. הן ראיה לכך שהנושא מופיע בחומר, לא הופעה בבחינת עבר ולא תדירות צפויה; ציוני הבחינות לא שונו על בסיסן.</p><ul>'''+''.join(
    '<li><a href="predictions.html#'+escape(qid)+'">'+escape(qid)+'</a> — '+escape(item['file'])+' · עמ׳ PDF '+escape(item['pages'])+' — '+escape(item['relation'])+'</li>'
    for qid,item in LECTURES.items())+'''</ul>
<p><a href="index.html?set=forecast-lecture#setup">תרגול השאלות עם סימוכין במצגות</a></p>
<p>בפרט, ציון נמוך של שאלה מפני שלא מופתה לה הופעה ישירה בבחינות אינו אומר שהיא מחוץ לחומר. לא נבדקו כך כל המצגות או כל 60 השאלות.</p>
<h2>תרגול משלים ממועדי עבר</h2><p>בבדיקה של חומרי התרגול של הקורס נמצאו גם נושאים הנכללים במאגר בחינות העבר, אך אינם מנוסחים כשאלות עצמאיות בתוך 60 התחזיות. אפשר לתרגל את השאלות המקוריות עם פתרונות ועם סדר תשובות משתנה. חומרי התרגול אינם בחינת מועד ב׳ נוספת ואינם ראיות בלתי תלויות לאותה שאלה.</p><ul><li><a href="solutions/Q074.html">Q074 — SameSite=Strict והגנה חלקית מ-CSRF</a>; השוו לתנאים ההפוכים ב-<a href="predictions.html#P17">P17</a>.</li><li><a href="solutions/Q072.html">Q072 — שינוי כללי קונצנזוס ו-hard fork</a>; הבחינו בינו לבין חישוב יעד במודל של <a href="predictions.html#P43">P43</a>.</li><li><a href="solutions/Q086.html">Q086 — מפתחות בשני כיוונים ו-reflection</a>.</li></ul><p>ההתאמות הללו תומכות בתרגול מושגים, אך אינן קובעות את תמהיל מועד ב׳ או מוכיחות ששאלה כלשהי תחזור.</p>
<h2>השלמת פער: Clickjacking</h2><p>זו שאלת בחירה משלימה שנכתבה לפי נושא המופיע בסילבוס, מעבר ל-60 התחזיות. אין לה ציון ביטחון מספרי: הסילבוס מאשר נושא לימוד בלבד, ולא תדירות או סיכוי להופעה. במאגר הבחינות Q022 ו-Q102 מזכירות X-Frame-Options בהקשר של SQL injection, אך אינן שואלות ישירות על מניעת clickjacking.</p>'''

def explanation(q):
    body='<h3>למה כל חלופה נכונה או שגויה</h3><p>החלופות מזוהות לפי תוכנן; סדרן משתנה בכל פתיחת העמוד.</p>'
    for i,(option,reason) in enumerate(zip(q['options'],q['reasons'])):
        body+='<div class="option-review"><h4>'+('נכונה' if i==0 else 'שגויה')+' — '+escape(option)+'</h4><p>'+escape(reason)+'</p></div>'
    return body+'''<h3>גבולות ההגנה</h3><p>הכותרת צריכה להגיע בתגובה של הדף המוגן, והדפדפן צריך לתמוך בה. frame-ancestors מגביל מי רשאי להטמיע את הדף; frame-src עוסק במשאבים שהדף עצמו רשאי להטמיע. ההגדרה שנשאלה אינה תחליף לכל הגנת Web אחרת ואינה טענה להגנה מכל מתקפה אפשרית.</p><p><a href="https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html">OWASP — Clickjacking Defense</a> · <a href="https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors">MDN — frame-ancestors</a> · <a href="solutions/Q022.html">Q022 — אזכור X-Frame-Options</a> · <a href="solutions/Q102.html">Q102 — אזכור נוסף</a></p>'''
