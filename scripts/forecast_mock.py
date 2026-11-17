"""A single, reproducible ten-question forecast with historical B-exam balance."""
from fractions import Fraction
from html import escape

# Editorial comparisons distinguish a similar operation from a broad family.
# They are not independently scored or claims of future recurrence.
FOCUSED_EVIDENCE = {
    'P01': ('אימות חתימה מספרית דומה הופיע בא׳ האחרון; שאר המקורות כוללים גם יצירת חתימה והסברים כלליים.', ['Q175','Q105']),
    'P02': ('בחירת מפתח המנפיק הופיעה בא׳ האחרון; שאר המקורות עוסקים בשרשרת או במידע בתעודה, ולא כולם באותה פעולה.', ['Q174','Q114']),
    'P04': ('שינוי מבוקר של OTP כשהמסר ידוע הופיע בא׳ האחרון. חומרי OTP היסטוריים אחרים כוללים סודיות וחילוף מסרים, ואינם כולם אותה התקפה.', ['Q179','Q120']),
    'P05': ('שילוב XSS וקריאת טוקן הופיע בא׳ האחרון ובמועד א׳ מיולי 2026; לא הוכח שיחזור בב׳ הקרוב.', ['Q180','Q157']),
    'P06': ('זיהוי Encrypt-then-MAC הופיע בב׳ בנובמבר 2025 ובב׳ באוגוסט 2026; המיפוי כולל גם סדרי שילוב אחרים.', ['Q133','Q163']),
    'P08': ('אישורים והוצאה כפולה הופיעו בא׳ האחרון ובב׳ בנובמבר 2025; מקורות אחרים דנים בכללי שרשרת או ב-51%.', ['Q177','Q137']),
    'P09': ('אותם פרמטרים ותוצאת DH הופיעו ב-24/11/2024, מועד מיוחד — לא מועד ב׳; מספרים זהים בעבר אינם ראיה שיחזרו.', ['Q099']),
    'P10': ('חישוב Vigenère הופיע בא׳ האחרון; מקור קודם בוחן הסתברות בצופן ולא חישוב ciphertext זהה.', ['Q173','Q097']),
    'P11': ('א׳ האחרון בחן היעדר SCT; כאן נבדק מה CT אינו מבטיח כאשר SCT קיים. קיץ 2025 מדגים מעבר ממטרת CT לאכיפת SCT.', ['Q181','Q129','Q139']),
    'P20': ('התקפת ARP ועמדת MITM נבחנו בעבר; שאלת התחזית מוסיפה את מגבלת פענוח TLS.', ['Q125','Q154']),
}

def select_mock(questions, report, pairs):
    # Equal weight per B exam; normalize the 12-choice 2022 paper to ten.
    dates = [b for _, _, b, _ in pairs]
    matrix = report['exam_topics']
    targets = {
        topic: sum((Fraction(10 * matrix[d].get(topic, 0), sum(matrix[d].values()))
                    for d in dates), Fraction()) / len(dates)
        for topic in report['topic_stats']
    }
    quotas = {topic: int(target) for topic, target in targets.items()}
    # Largest remainders preserve the total of ten without subjective rounding.
    for topic in sorted(targets, key=lambda t: (-(targets[t] - quotas[t]), t))[:10 - sum(quotas.values())]:
        quotas[topic] += 1
    selected = []
    for topic, count in quotas.items():
        skills = set()
        for q in sorted((q for q in questions if q['topic'] == topic),
                        key=lambda q: (-q['confidence'], q['id'])):
            if len(skills) == count:
                break
            if q['skill'] not in skills:
                selected.append(q)
                skills.add(q['skill'])
        assert len(skills) == count, (topic, count)
    selected.sort(key=lambda q: (-q['confidence'], q['id']))
    assert len(selected) == 10 and len({q['skill'] for q in selected}) == 10
    return dict(id='forecast-best', question_ids=[q['id'] for q in selected],
                b_dates=dates, quotas=quotas,
                target_counts={t: round(float(v), 4) for t, v in targets.items()},
                method='Equal-weight B exams normalized to ten; largest-remainder topic quotas; '
                       'highest confidence per topic with distinct skills; ID breaks ties.')


def mock_page(mock, questions):
    lookup = {q['id']: q for q in questions}
    body = '''<p class="study-intro"><strong>סימולציה אחת של 10 שאלות — התחזית הממוקדת שלי למועד ב׳.</strong>
השאלות נבחרו לפי ציוני הביטחון, בתוך תמהיל נושאים שמבוסס על מועדי ב׳ קודמים. זו בחירה לימודית מנומקת, לא ידיעה של השאלון העתידי.</p>
<div class="study-actions"><a class="primary" href="index.html?set=forecast-best#setup">פתיחת הסימולציה בהגדרות המבחן</a></div>
<h2>איך נקבע התמהיל?</h2><p>כל אחד משבעת מועדי ב׳ קיבל משקל שווה. מספר שאלות הברירה בכל נושא נורמל למבחן בן 10 שאלות; כך 12 שאלות הברירה ב-2022 אינן מקבלות משקל יתר. לקחנו את החלק השלם של כל ממוצע, ואז חילקנו את המקומות שנותרו לפי השאריות הגדולות ביותר, עד לסך של 10.</p>
<p>בתוך כל נושא נבחרו השאלות בעלות הציון הגבוה ביותר, עם מיומנות שונה בכל מקום. בשוויון ציונים נבחר מזהה השאלה הקטן יותר. לכן נבחרו שרשרת תעודות ו-CT במקום שתי שאלות על שרשרת אמון, ו-OTP ו-Vigenère במקום שתי שאלות OTP. שאלת DH בעלת ציון נמוך יותר נכללת כדי לשמור על התמהיל ההיסטורי.</p>
<p>תמהיל הנושאים מבוסס על שבעת מועדי ב׳; ציוני השאלות עצמם מבוססים על כל 18 המועדים ועל מועד א׳ האחרון. אין כאן כיול הסתברותי או בדיקת דיוק על בחינות עתידיות.</p>
<div class="study-table"><table><thead><tr><th>נושא</th><th>ממוצע שאלות ל-10 במועדי ב׳</th><th>בסימולציה</th></tr></thead><tbody>'''
    for topic, count in mock['quotas'].items():
        body += f'<tr><td>{escape(topic)}</td><td>{mock["target_counts"][topic]:.2f}</td><td>{count}</td></tr>'
    body += '''</tbody></table></div><p>אין שאלת TLS ייעודית בסימולציה: הממוצע ההיסטורי שלה במועדי ב׳ הוא כ-0.29 מתוך 10, והיא לא קיבלה מקום בעיגול. אין בכך הבטחה שלא תופיע; שאלות TLS נשארות במאגר התחזית הרחב. איזון לפי נושא ראשי אינו סופר מחדש כל תת-נושא בתוך שאלה.</p>
<h2>עשר השאלות שנבחרו</h2><p>זהו סט קבוע: סדר השאלות והתשובות מתערבב בכל ניסיון. המבחן המלא כולל את כל העשר, 80 דקות כברירת מחדל ופתרונות מפורטים לאחר ההגשה. בחירת פחות שאלות או סינון נושאים/טעויות יוצרים תרגול חלקי שאינו שומר על התמהיל המלא.</p><ol>'''
    for qid in mock['question_ids']:
        q = lookup[qid]
        explanation, sources = FOCUSED_EVIDENCE[qid]
        references = ' · '.join(f'<a href="solutions/{source}.html">{source}</a>' for source in sources)
        body += f'<li><a href="predictions.html#{qid}">{qid} — {escape(q["title"])}</a> · <strong>{q["confidence"]}/100</strong> · {escape(q["topic"])}<p>{escape(explanation)} סימוכין: {references}.</p></li>'
    body += '</ol><p>מועדי ב׳ שנכללו: ' + ' · '.join(mock['b_dates']) + '.</p>'
    return body + '''<p><a href="sensitivity.html">מה משתנה אם מסירים מועד אחד מהתמהיל?</a> · <a href="confidence.html">שיטת ציוני הביטחון והראיות</a> · <a href="analysis.html">זוגות א׳/ב׳ וההשוואה</a> · <a href="data/forecast-best.json">נתוני הבחירה והתמהיל</a></p>'''
