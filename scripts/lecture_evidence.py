"""Manually checked local slide references, kept distinct from exam evidence.

Pages are PDF page numbers, not slide numbers. The files are not published and
their edition or complete correspondence to the current semester is unverified.
"""
LECTURES={
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
