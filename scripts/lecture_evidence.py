"""Manually checked local slide references, kept distinct from exam evidence.

Pages are PDF page numbers, not slide numbers. The files are not published and
their edition or complete correspondence to the current semester is unverified.
"""
LECTURES={
 'P06':dict(file='4_1_Integrity_and_Authenticity.pdf',pages='29',relation='השקופית מבחינה בין שלושת סדרי השילוב ומתארת Encrypt-then-MAC כהצפנה ואחריה MAC על ה-ciphertext. השאלה מוסיפה במפורש בדיקת התג לפני הפענוח.'),
 'P09':dict(file='R (1) (1) (2).pdf',pages='30–31',relation='במצגת התרגול מופיע חישוב סוד DH מתוך מעריכים פרטיים נתונים, עם פרמטרים אחרים ופתרון 16. תאריך המצגת והתאמתה לסמסטר הנוכחי לא אומתו.'),
 'P10':dict(file='Crypto1.pdf',pages='95, 99',relation='השקופיות מתארות חזרה על המפתח והזזת אותיות לפי המפתח, ומציגות את מספור האותיות; המילים והחישוב בשאלה חדשים.'),
 'P45':dict(file='Crypto1.pdf',pages='127, 145, 151',relation='המצגת מגדירה OTP עם XOR ומפתח לשימוש אחד ומציגה את בעיית השימוש החוזר; שחזור הבית בהינתן הודעה ידועה הוא תרגיל נוסף.'),
 'P26':dict(file='6_1_PKI.pdf',pages='124–125',relation='השקופיות מציגות את בעיית הביקור הראשון ואת HSTS preload; אין בכך הוכחה ששאלת מועד ב׳ תעסוק בכך.'),
 'P29':dict(file='Network_security (2) (1).pdf',pages='37–42',relation='השקופיות מתארות התאמת TXID בגודל 16 ביט ופורט מקור במענה DNS. התרגיל מציב במפורש ניחוש יחיד ופורט ידוע.'),
 'P30':dict(file='Network_security (2) (1).pdf',pages='66–67',relation='השקופיות מתארות Slowloris וחיבורי HTTP איטיים; התרגיל מוסיף גם בחירת אמצעי הגנה.'),
 'P38':dict(file='6_1_PKI.pdf',pages='135–137',relation='השקופיות מגדירות SCT כהתחייבות להוסיף תעודה לעץ בתוך Maximum Merge Delay. זה מקור ללימוד המנגנון, לא הופעה ממופה בבחינת עבר.'),
 'P39':dict(file='6_1_PKI.pdf',pages='187–193',relation='השקופיות מציגות Split World עם תצוגות לוג שונות. התרגיל מוסיף במפורש ראשי עץ באותו גודל והנחת היעדר התנגשות.'),
 'P55':dict(file='3_1_Asymmetric_cryptography.pdf',pages='122, 126',relation='השקופיות מציינות רגישות ל-MITM ומציגות חילוף Diffie–Hellman עם תוקף פעיל. לא מופה תרגיל בחינה ישיר זהה.'),
}

def attach(questions):
    for q in questions:
        if q['id'] in LECTURES:
            q['lecture_evidence']=dict(LECTURES[q['id']])
