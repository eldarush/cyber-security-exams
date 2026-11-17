"""Reproducible evidence-weighted study confidence, NOT calibrated probability.

Topic coverage uses every dated exam, with duplicate files collapsed by date.
Skill evidence is a conservative manual map of confirmed supporting questions;
it is not claimed to be an exhaustive label of every clause in mixed questions.
"""
from collections import Counter
from datetime import datetime

SKILLS = {
 'rsa-sign':('חתימות RSA: יצירה ואימות','Q020 Q034 Q100 Q105 Q113 Q175'),
 'rsa-verify':('אימות חתימה והתאמתה להודעה','Q020 Q034 Q113 Q175'),
 'rsa-create':('חישוב חתימת textbook RSA במפתח פרטי','Q100 Q105'),
 'rsa-gen':('RSA: פרמטרים, הופכי ומעריכים','Q100 Q104 Q138 Q155'),
 'key-roles':('תפקידי מפתחות: סודיות, חתימה ואמון','Q009 Q044 Q092 Q112 Q123 Q128'),
 'chain':('אימות תעודות ושרשרת אמון','Q010 Q023 Q070 Q114 Q174'),
 'ca-constraints':('הרשאת CA בתעודת ביניים — ללא סימוכין ישירים ממופים',''),
 'service-name':('התאמת שם השירות לתעודה — ללא סימוכין ישירים ממופים',''),
 'utxo':('UTXO, פלטים ותוקף הוצאה','Q058 Q117 Q162 Q176'),
 'utxo-change':('חישוב פלט עודף ועמלה','Q176'),
 'utxo-validity':('תוקף טרנזקציה וכללי הוצאה','Q050 Q176'),
 'utxo-outpoint':('זיהוי פלט לפי מזהה טרנזקציה ואינדקס — ללא סימוכין ישירים ממופים',''),
 'otp':('OTP, XOR וגבולות ההגנה','Q013 Q049 Q120 Q121 Q179'),
 'otp-malleability':('שינוי מבוקר של מסר OTP ידוע','Q179'),
 'otp-reuse':('סיכון שימוש חוזר במפתח OTP','Q049'),
 'xss-csrf':('XSS מול סשן וטוקן CSRF','Q022 Q076 Q115 Q118 Q157 Q180'),
 'xss-token':('XSS וקריאת טוקן מתוך הדף','Q118 Q157 Q180'),
 'cookie-flags':('מאפייני cookie: HttpOnly לעומת Secure','Q115 Q180'),
 'mac':('MAC וסדר הצפנה ואימות','Q015 Q057 Q078 Q116 Q133 Q143 Q153 Q163'),
 'mac-composition':('זיהוי סדר שילוב MAC והצפנה','Q057 Q116 Q133 Q143 Q163'),
 'birthday':('התנגשות ו-birthday','Q150 Q169 Q182'),
 'birthday-calc':('חישוב הסתברות התנגשות לפי יום הולדת','Q169'),
 'consensus':('אישורים, הוצאה כפולה וכוח כרייה','Q050 Q053 Q137 Q167 Q177'),
 'dh':('Diffie–Hellman: חישוב והנחות אבטחה','Q025 Q036 Q043 Q047 Q056 Q068 Q094 Q099 Q148 Q164'),
 'dh-calculation':('חישוב סוד משותף ב-Diffie–Hellman','Q036 Q068 Q099 Q148 Q164'),
 'dh-active':('תיווך פעיל ב-Diffie–Hellman לא מאומת — ללא סימוכין ישירים ממופים',''),
 'vigenere':('צופן Vigenère ומפתח חוזר','Q097 Q173'),
 'ct':('Certificate Transparency ותפקידי הלוג','Q024 Q048 Q063 Q073 Q077 Q098 Q129 Q139 Q149 Q156 Q181'),
 'ct-policy':('CT: שקיפות הנפקות ותנאי SCT בדפדפן','Q063 Q077 Q129 Q139 Q156 Q181'),
 'ct-promise':('SCT: התחייבות להכללה בתוך זמן — ללא סימוכין ישירים ממופים',''),
 'ct-split-view':('CT: ראיה לשתי תצוגות סותרות — ללא סימוכין ישירים ממופים',''),
 'ocsp':('סטטוס תעודה, ביטול ו-OCSP','Q021 Q059 Q073 Q101 Q108 Q110 Q119 Q170'),
 'cbc':('CBC ותלות בין בלוקים','Q168'),
 'merkle':('מרקל: נתיב, שורש והוכחת הכללה','Q106 Q152 Q159 Q165'),
 'hash':('תכונות hash וגבולות התנגשויות','Q067 Q082 Q130 Q140 Q150 Q169 Q182'),
 'second-preimage':('קדם־תמונה שנייה: הודעה מקורית נתונה','Q067 Q140'),
 'collision':('התנגשות: שתי הודעות שונות עם פלט זהה','Q150 Q182'),
 'csrf':('CSRF: תנאי התקפה ובדיקות שרת','Q004 Q022 Q074 Q076 Q091 Q111 Q157 Q180'),
 'csrf-cross-site':('CSRF חוצה אתרים: עוגיות, בקשה ואמצעי הגנה','Q004 Q022 Q074 Q091 Q111'),
 'p2pkh':('P2PKH והרשאת הוצאה','Q058 Q087 Q162'),
 'tls':('TLS: תמליל, חילוף וסודות','Q003 Q005 Q033 Q061 Q107 Q110 Q124 Q134 Q144 Q158'),
 'arp':('ARP, תיווך וגבולות היכולת','Q031 Q062 Q075 Q125 Q154 Q171'),
 'key-count':('ספירת מפתחות לכל זוג עובדים','Q178'),
 'ecb':('ECB ודפוסי בלוקים חוזרים','Q064 Q166'),
 'toy-hash':('מציאת התנגשות מבנית ב-hash חלש','Q182'),
 'password':('אחסון סיסמאות, salt ו-pepper','Q014 Q069 Q085 Q103 Q136'),
 'sop':('Same Origin Policy והפרדת מקורות','Q007 Q026 Q126 Q135 Q145'),
 'hsts':('HSTS וביקור ראשון','Q141 Q160'),
 'csp':('CSP והרשאת משאבים וסקריפטים','Q038 Q065 Q131 Q161'),
 'sql':('SQL injection והפרדה בין קוד לנתון','Q017 Q035 Q060 Q095'),
 'dns':('DNS, ניחוש ושינוי תשובות','Q016 Q019 Q030 Q037 Q052 Q171'),
 'dos':('DoS והתשת משאבים','Q002 Q028 Q032 Q041 Q054 Q172'),
 'escrow':('Escrow וספי חתימות','Q018 Q147'),
 'pow':('כרייה ו-Proof of Work','Q029 Q042 Q046 Q072'),
 '3des':('הרכבת הצפנה ופענוח ב-3DES','Q071 Q151'),
 'substitution':('צופן החלפה ותבניות חזרות','Q055 Q096 Q142'),
 'dom':('XSS והקשר פירוש הקלט','Q006 Q109 Q118 Q135 Q145'),
}
KEYS = ('rsa-verify chain utxo-change otp-malleability xss-token mac-composition birthday-calc consensus dh-calculation vigenere '
        'ct-policy ocsp cbc merkle second-preimage rsa-gen csrf-cross-site p2pkh tls arp '
        'key-count ecb toy-hash password sop hsts csp sql dns dos '
        'rsa-create rsa-gen key-roles rsa-gen service-name ca-constraints ocsp ct-promise ct-split-view utxo-validity '
        'utxo-outpoint escrow pow merkle otp-reuse cbc 3des substitution vigenere collision '
        'toy-hash hash mac password dh-active cookie-flags dom sql csrf tls').split()
# Explicit editorial deduction for a wider extrapolation of a documented skill.
EXTENSIONS = {32,35,36,38,39,40,41,43,45,49,52,53,54,55,56,57,59,60}
EXTENSION_DEDUCTION = 20

def annotate(questions, bank, pairs):
    lookup={q['id']:q for q in bank}
    dated={}
    for q in bank:
        for s in q['sources']:
            if s.get('date'):
                dated.setdefault(s['date'],{})[s['num']]=q
    dates=sorted(dated,key=lambda d:datetime.strptime(d,'%d/%m/%Y'))
    summer=[p for p in pairs if 'קיץ' in p[0]]
    topics=sorted({q['topic'] for q in bank})
    matrix={d:Counter(q['topic'] for q in dated[d].values()) for d in dates}
    stats={}
    for topic in topics:
        stats[topic]=dict(exams=sum(topic in matrix[d] for d in dates),
            a=sum(topic in matrix[a] for _,a,b,_ in pairs),
            b=sum(topic in matrix[b] for _,a,b,_ in pairs),
            both=sum(topic in matrix[a] and topic in matrix[b] for _,a,b,_ in pairs),
            summer_b=sum(topic in matrix[b] for _,a,b,_ in summer))
    # Sensitivity analyses remove a dated sitting and its pair; the production
    # build validates the 18-date corpus separately.
    assert len(questions)==len(KEYS)==60 and len(dates)>0 and len(pairs)>0
    for i,(q,key) in enumerate(zip(questions,KEYS),1):
        name,ids=SKILLS[key]; ids=ids.split()
        evidence=sorted(set(ids+q['evidence']))
        support=sorted({s['date'] for qid in ids for s in lookup[qid]['sources'] if s.get('date')},key=lambda d:datetime.strptime(d,'%d/%m/%Y'))
        t=stats[q['topic']]
        components={
            'all_exams':15*(t['exams']+1)/(len(dates)+2),
            'b_exams':25*(t['b']+1)/(len(pairs)+2),
            'a_to_b':15*(t['both']+1)/(t['a']+2),
            'summer_b':15*(t['summer_b']+1)/(len(summer)+2),
            'skill_support':20*min(len(support)/6,1),
            'latest_a':10*int('19/10/2026' in support),
        }
        deduction=EXTENSION_DEDUCTION if i in EXTENSIONS else 0
        score=max(1,min(100,round(sum(components.values())-deduction)))
        q.update(confidence=score,confidence_kind='skill-confidence-not-probability',skill=key,
            skill_label=name,evidence=evidence,
            confidence_basis=dict(topic_counts=t,total_exams=len(dates),total_pairs=len(pairs),
                summer_pairs=len(summer),skill_dates=support,skill_evidence=ids,
                latest_a_skill='19/10/2026' in support,components={k:round(v,4) for k,v in components.items()},
                extension_deduction=deduction),
            priority='ליבה' if score>=70 else 'משלים' if score>=55 else 'ממוקד' if score>=45 else 'רשת ביטחון')
        q['confidence_reason']=(f"משפחת הנושא הופיעה ב-{t['exams']}/{len(dates)} מועדים וב-{t['b']}/{len(pairs)} מועדי ב׳; "
            f"נמשכה מא׳ לב׳ ב-{t['both']}/{t['a']} זוגות שבהם הופיעה בא׳; "
            f"במועדי ב׳ של קיץ: {t['summer_b']}/{len(summer)}. "
            f"למיומנות המתועדת יש סימוכין ב-{len(support)} תאריכים שונים. "
            +('משפחת המיומנות ממופה גם באוקטובר 2026; יש לבדוק את השאלה המקורית כדי להבחין בין פעולה זהה למושג קרוב. ' if '19/10/2026' in support else 'אין סימוכין למיומנות הזו באוקטובר 2026 במיפוי המסוים. ')
            +(f'הופחתו {deduction} נקודות כי השאלה מרחיבה את המיומנות למקרה שלא תועד באותו אופן בבחינות.' if deduction else 'השאלה מתרגלת וריאציה של מיומנות מתועדת; המספר אינו סיכוי לניסוח המדויק.'))
    return dict(version='2026-11-14-60',kind='heuristic-study-confidence-not-probability',
        weights=dict(all_exams=15,b_exams=25,a_to_b=15,summer_b=15,skill_support=20,latest_a=10),
        smoothing='(successes+1)/(trials+2); skill contribution capped at six distinct supporting dates',
        extension_deduction=EXTENSION_DEDUCTION,dates=dates,year_exam_counts=dict(Counter(d[-4:] for d in dates)),
        exam_topics={d:dict(matrix[d]) for d in dates},topic_stats=stats,
        skills={k:dict(label=v[0],evidence=v[1].split()) for k,v in SKILLS.items()},
        questions=[dict(id=q['id'],score=q['confidence'],skill=q['skill'],basis=q['confidence_basis']) for q in questions])
