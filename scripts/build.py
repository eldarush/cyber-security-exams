from pathlib import Path
from collections import Counter,defaultdict
from urllib.parse import quote
import json,re,html,hashlib
from content import LATEST,AUG,TOPICS
from forecast import NEW,PLAN,TOPIC_MAP,AUDIT,PAIRS,SOURCES
from forecast_review import apply_reviews
from forecast_expansion import EXTRA
from forecast_confidence import annotate
from forecast_presentation import confidence_summary, forecast_intro, confidence_page
from forecast_mock import select_mock, mock_page

R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
def write(p,t):
    p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8',newline='\n')
def save(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2))
def e(s):return html.escape(str(s))
def url(s):return quote(str(s).replace('\\','/'),safe='/#?=&')
def asset(name):return name+'?v='+hashlib.sha256((R/name).read_bytes()).hexdigest()[:12]
def clean(t):
    # Source documents contain only study markup. Strip scripts, inline handlers and
    # local document links; canonical source links are emitted separately.
    t=re.sub(r'<script\b.*?</script>','',t,flags=re.S|re.I)
    t=re.sub(r'\s+on\w+\s*=\s*([\"\']).*?\1','',t,flags=re.S|re.I)
    t=re.sub(r'</?a\b[^>]*>','',t)
    return t
def paragraphs(t):return '<p>'+e(t).replace('\n','</p><p>')+'</p>'

original=load('מאגר שאלות/bank.json')
legacy=load('data/legacy-solutions.json')
archive=load('data/archive-solutions.json')
old=load('data/old-forecast.json')
qbank=original['questions']
# The inherited topic classifier used distractor words in several questions.
# These corrections keep broad-topic counts aligned with the tested operation.
fix={'Q038':6,'Q048':4,'Q065':6,'Q066':8,'Q070':4,'Q080':4,'Q121':0,'Q123':1,'Q131':6,'Q172':7}
for q in qbank:
    q['accepted_indices']=[0,1,2,3] if q['id']=='Q013' else [0,1] if q['id'] in ['Q021','Q038','Q055'] else [0]
    if q['id'] in fix:q['topic']=TOPICS[fix[q['id']]]
    if q['id'] in AUG:
        q['answer_html']=AUG[q['id']];q['answer_origin']='פתרון חדש שנכתב ונבדק במסגרת עדכון נובמבר 2026'
    else:
        matches=[(s,legacy.get(Path(s['file']).name+'|'+str(s['num']))) for s in q['sources']]
        match=next(((s,a) for s,a in matches if a),None)
        assert match,q['id']
        q['answer_html']=clean(match[1]);q['answer_origin']='פתרון מפורט מהתיקייה organized exams · 17/10/2026'
        q['answer_source']=Path(match[0]['file']).name
for q in LATEST:
    q['accepted_indices']=[0]
    q['answer_origin']='פתרון חדש · המפתח הרשמי בקובץ: א׳ · ההסבר הוא חומר לימוד עצמאי'
    qbank.append(q)
assert len(qbank)==182
lookup={q['id']:q for q in qbank}

pred=[]
for i,(key,priority,ev) in enumerate(PLAN,1):
    if isinstance(key,str):
        item=NEW[key]
        q=dict(stem=item['stem'],options=item['options'],topic=TOPICS[item['topic']],answer_html=item['answer'],title=item['title'],guide=item['guide'])
        origin='וריאציה חדשה לצורך תרגול מועד ב׳'
    else:
        oq=next(x for x in old['questions'] if x['id']==key)
        correct=oq['options'][oq['answer_index']]
        # Drop the old question heading and answer letter: the practice UI shuffles
        # options, and the substantive explanation must not imply a stale letter.
        body=re.search(r'<div class="answer-body">(.*)</div><p class="muted">',old['answers'][key-1],re.S)[1]
        q=dict(stem=oq['stem'],options=[correct]+[s for j,s in enumerate(oq['options']) if j!=oq['answer_index']],topic=TOPICS[TOPIC_MAP[oq['topic']]],answer_html=clean(body),title=oq['topic'],old_number=key)
        origin=f'תרגיל {key} מהמאגר שנכתב ב-17/10/2026; נבחר מחדש לפי ההשוואה המעודכנת'
    q.update(id=f'P{i:02}',year='תרגול',note='תחזית לימודית, לא שאלה שנצפתה בבחינה עתידית',sources=[dict(file='predictions.html',date=None,num=i)],flags=[],fixed_order=False,exclude=False,exam_count=0,in_sample_exam=False,variant_group=None,priority=priority,evidence=ev,mock=(i-1)//10+1,answer_origin=origin,accepted_indices=[0])
    pred.append(q)

pred.extend(EXTRA)
apply_reviews(pred)
confidence_report=annotate(pred,qbank,PAIRS)
save('data/forecast-confidence.json',confidence_report)
best_mock=select_mock(pred,confidence_report,PAIRS)
save('data/forecast-best.json',best_mock)
for q in qbank+pred:
    q['question_type']='multiple-choice'
    q['solution']='solutions/'+q['id']+'.html'
    # Main app is at root; its links must differ from standalone solution links.
    q['answer_html']=q['answer_html'].replace('href="Q','href="solutions/Q')

original['meta']['topics']={t:{'count':sum(q['topic']==t for q in qbank)} for t in TOPICS}
original['meta']['updated']='2026-11-14'
original['questions']=qbank
save('data/bank.json',original);save('data/forecast.json',pred)

css=re.search(r'<style>(.*?)</style>',(R/'scripts/index.template.html').read_text(encoding='utf-8'),re.S)[1]
extra='''
.top a.brand{color:var(--ink);text-decoration:none}
html{scroll-behavior:smooth}a{color:var(--accent)}.study-nav{display:flex;flex-wrap:wrap;gap:9px 18px;padding:14px 0}.study-nav a{text-decoration:none}.reading{max-width:1000px;margin:30px auto;padding:0 20px 60px}.reading h1{font:30px/1.5 var(--f-display);margin:20px 0 12px}.reading h2{font-size:23px;margin:30px 0 12px}.reading h3{font-size:19px;margin:22px 0 10px}.reading h4{font-size:17px}.reading p{font-size:17px;line-height:1.95;max-width:88ch}.reading li{line-height:1.9}.reading pre{direction:ltr;text-align:left;white-space:pre-wrap;overflow-wrap:anywhere;padding:18px;background:var(--code);border-radius:8px;font:15px/1.8 var(--f-mono)}.study-intro{border-right:4px solid var(--accent);padding:18px 22px;background:var(--surface);border-radius:8px;margin:24px 0}.study-actions{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.study-actions a{display:inline-block;padding:10px 16px;border:1px solid var(--line);border-radius:8px;text-decoration:none;background:var(--surface)}.study-actions a.primary{background:var(--accent);color:var(--accent-ink)}.study-table{overflow:auto;margin:22px 0}.study-table table{border-collapse:collapse;width:100%;min-width:650px}.study-table th,.study-table td{border-bottom:1px solid var(--line);padding:12px;text-align:right;vertical-align:top}.study-table th{background:var(--surface-2)}.study-card{padding:22px;background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:18px 0;scroll-margin-top:120px}.study-card>h2,.study-card>h3{margin-top:6px}.answer-detail{padding:14px 18px;margin-top:16px;background:var(--surface-2);border:1px solid var(--line);border-radius:8px;overflow-wrap:anywhere}.answer-detail summary{cursor:pointer;color:var(--accent);font-weight:600}.answer-detail p{font-size:16px;line-height:1.9}.answer-detail h2{font-size:21px}.answer-detail h3{font-size:19px}.answer-detail h4{font-size:17px}.answer-detail pre{white-space:pre-wrap;overflow-wrap:anywhere}.answer-section{break-inside:auto}.reading .muted{color:var(--muted);font-size:14px}.reading .options{padding-right:25px}.reading .correct{border-right:3px solid var(--good);padding:14px 18px;background:var(--good-soft)}.study-footer{margin-top:40px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted);font-size:13px}.study-filter{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.study-filter input,.study-filter select{padding:10px;border:1px solid var(--line);background:var(--surface);border-radius:8px;max-width:100%}.study-banner{padding:16px 20px;background:var(--accent-soft);border-bottom:1px solid var(--line)}.study-banner .wrap{display:flex;flex-wrap:wrap;gap:12px;align-items:center}.study-banner a{font-weight:600}.skip-link{position:absolute;top:-100px}.skip-link:focus{top:10px;z-index:99;background:var(--surface);padding:10px}nav.tabs{flex-wrap:wrap}.study-controls{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin:14px 0}.study-controls label{cursor:pointer}.study-options li{padding:8px 0}.study-source{font-size:14px;color:var(--muted)}[hidden]{display:none!important}
@media(max-width:600px){.reading{padding:0 15px 40px;margin-top:18px}.reading h1{font-size:26px}.reading p{font-size:16px}.study-card{padding:16px}.study-intro{padding:14px}.top .wrap{gap:6px}.brand small{display:block}.study-nav{gap:8px 14px}.answer-detail{padding:12px}.reading pre{font-size:13px}}
@media print{.top,.study-nav,.study-actions,.study-filter,.study-controls,.study-banner,.skip-link{display:none!important}.reading{max-width:none;margin:0;padding:0}.reading p{font-size:12pt}.study-card{border:0;break-before:page;padding:0}.answer-detail{border:0;background:white}.study-table table{min-width:0;font-size:9pt}.study-footer{font-size:9pt}details>summary{display:none}.correct{background:white!important;color:black!important}a{color:black!important}body{background:white!important;color:black!important}}
'''
write('study.css',css+extra+'\nhtml.only-multiple-choice [data-question-type="open"]{display:none!important}.option-review{padding:8px 0;border-bottom:1px solid var(--line)}.option-review h4{margin:10px 0}.question-type-filter{padding:14px 18px;margin:18px 0;background:var(--surface);border:1px solid var(--line);border-radius:8px}.question-type-filter label{cursor:pointer}.question-type-filter p{margin:6px 0;font-size:14px}\n')
NAV=[('index.html#setup','תרגול אינטראקטיבי'),('latest.html','מועד א׳ 2026'),('predictions.html','תחזית מועד ב׳'),('analysis.html','בדיקת התחזית'),('archive.html','כל הפתרונות')]

def question_type_filter():
    return '<div class="question-type-filter"><label><input type="checkbox" id="only-multiple-choice" checked> בלי שאלות פתוחות</label><p>הסינון מסתיר סעיפים פתוחים במסמכי הארכיון. התרגול האינטראקטיבי והתחזית כוללים רק שאלות בחירה בכל מצב.</p><p role="status" data-question-filter-status></p></div>'
def page(path,title,body,depth=0):
    prefix='../'*depth
    nav=''.join(f'<a href="{prefix}{p}">{label}</a>' for p,label in NAV)
    doc=f'''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · מבחני סייבר</title><link rel="stylesheet" href="{prefix}study.css"><meta name="description" content="מבוא לאבטחת סייבר 689156 — מבחנים, פתרונות מפורטים ותרגול מועד ב׳ עם ניתוח ראיות."></head><body><a class="skip-link" href="#main">דלג לתוכן</a><header class="top"><div class="wrap"><a class="brand" href="{prefix}index.html">מבחני סייבר <small>מבוא לאבטחת סייבר · 689156</small></a></div><nav class="wrap study-nav" aria-label="ניווט ראשי">{nav}</nav></header><main id="main" class="reading"><h1>{e(title)}</h1>{body}<footer class="study-footer">עודכן 14/11/2026 · חומר לימוד עצמאי, לא פתרון רשמי ולא מידע על שאלון עתידי. שאלות הבחינות נשמרות לפי המקורות; הסברים חדשים מסומנים. האתר הוא fork של <a href="https://github.com/salimkh25/cyber-security-exams">salimkh25/cyber-security-exams</a>. <a href="https://github.com/eldarush/cyber-security-exams">קוד האתר</a>.</footer></main><script src="{prefix}study.js" defer></script></body></html>'''
    fonts='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Hebrew:wght@400;500;600;700&family=Suez+One&display=swap">'
    doc=doc.replace('</head>',fonts+f'<script src="{prefix}{asset("answer-order.js")}"></script></head>')
    doc=doc.replace('study.js"',asset('study.js')+'"')
    doc=doc.replace('href="'+prefix+'study.css"','href="'+prefix+asset('study.css')+'"')
    doc=doc.replace('<html lang="he"', '<html class="only-multiple-choice" lang="he"')
    if 'class="study-options"' in body:
        doc=doc.replace('<h1>'+e(title)+'</h1>', '<h1>'+e(title)+'</h1><p class="study-source">סדר החלופות מתערבב בכל פתיחת עמוד. המפתח המוצג מתאים לסדר הנוכחי. אותיות בתוך הסברים מיובאים מתייחסות לשאלון המקורי — יש לזהות את התשובה לפי תוכנה.</p>')
    write(path,doc)

def srclinks(q,prefix=''):
    ss=[];seen=set()
    for s in q['sources']:
        if not s.get('date') or (s['date'],s['num']) in seen:continue
        seen.add((s['date'],s['num']))
        ss.append(f'<a href="{prefix}{url(s["file"])}">{e(s["date"])} · שאלה {s["num"]} · PDF</a>')
    return ' · '.join(ss)
def qlinks(ids,prefix=''):
    return ' · '.join(f'<a href="{prefix}solutions/{i}.html">{e(i)} — {e(lookup[i]["sources"][0]["date"])} ש׳ {lookup[i]["sources"][0]["num"]}</a>' for i in ids)
def answer(q,prefix=''):
    a=q['answer_html']
    if prefix:a=a.replace('href="solutions/','href="'+prefix+'solutions/')
    return '<p class="study-source">'+e(q['answer_origin'])+'</p>'+a
def option_order(q):
    # Varied static fallback; the browser reshuffles independently on each visit.
    return sorted(range(len(q['options'])),key=lambda i:hashlib.sha256(f'{q["id"]}:{i}'.encode()).digest())
def options(q):
    return '<ol class="study-options" style="list-style:none" id="opts-'+q['id']+'" data-accepted="'+e(json.dumps(q['accepted_indices']))+'">'+''.join('<li data-option-index="'+str(i)+'"><b class="option-letter">'+'אבגד'[j]+'. </b><span class="option-text">'+e(q['options'][i]).replace('\n','<br>')+'</span></li>' for j,i in enumerate(option_order(q)))+'</ol>'
def answer_key(q):
    keys=['אבגד'[j]+'. '+q['options'][i] for j,i in enumerate(option_order(q)) if i in q['accepted_indices']]
    label='חלופות שהתקבלו בבדיקה: ' if len(keys)>1 else 'התשובה הנכונה כאן: '
    return '<p class="correct" data-answer-for="opts-'+q['id']+'">'+e(label+' / '.join(keys))+'</p>'
for q in qbank+pred:
    body='<p class="muted">'+e(q['id']+' · '+q['topic'])+'</p>'+paragraphs(q['stem'])+options(q)
    if q.get('confidence'):body=confidence_summary(q,'../')+body
    body+=answer_key(q)
    if len(q['accepted_indices'])>1:
        body+='<p class="study-intro">הניקוד מכבד את החלופות שהתקבלו בבדיקה המקורית. הפתרון מסביר את ההסתייגות המקצועית.</p>'
    if q.get('note'):body+='<p class="study-intro">'+e(q['note'])+'</p>'
    body+=answer(q,'../')+'<p>'+srclinks(q,'../')+'</p>'
    if q['id'].startswith('P'):body+='<h2>למה לתרגל?</h2><p>עדיפות: '+q['priority']+' — שילוב של חזרתיות במשפחת הנושא, וריאציות במועדי ב׳ ופערים שנחשפו במועד א׳. אין זו הסתברות להופעת השאלה.</p><p>'+qlinks(q['evidence'],'../')+'</p><p><a href="../predictions.html#'+q['id']+'">חזרה לתחזית</a></p>'
    page(q['solution'],q.get('title',q['id']+' — פתרון מפורט'),body,1)

# Preserve all open subparts and duplicate/source variants from the local archive.
archive_links=[]
for i,doc in enumerate(archive,1):
    p=next((p for p in R.glob('*/*.pdf') if p.name==doc['file']),None)
    assert p,doc['file']
    fn=f'solutions/archive-{i:02}.html'
    sections=[];open_count=0
    for article in doc['articles']:
        is_open=bool(re.search(r'<h[23]>שאלה א\.',article))
        kind='open' if is_open else 'multiple-choice'
        open_count+=is_open
        sections.append(clean(article).replace('<article ', '<article data-question-type="'+kind+'" ',1))
    body='<p class="study-intro">פתרונות מהתיקייה שסופקה. סעיפים פתוחים, אם קיימים, מוסתרים כברירת מחדל. עותקים שונים של אותו מועד אינם מבחנים עצמאיים בניתוח.</p>'+question_type_filter()+'<p><a href="../'+url(p.relative_to(R))+'">שאלון המקור PDF — הקובץ המקורי אינו מסונן</a></p>'+''.join(sections)
    page(fn,'פתרונות מלאים · '+doc['file'],body,1)
    archive_links.append((doc['file'],fn,len(doc['articles']),open_count))

# Frozen historical practice, retained separately from the new ranking.
for i,(q,a) in enumerate(zip(old['questions'],old['answers']),1):
    shown=dict(q,id=f'old-p{i:02}',accepted_indices=[q['answer_index']])
    explanation=re.search(r'<div class="answer-body">(.*)</div><p class="muted">',a,re.S)[1]
    page(f'solutions/old-p{i:02}.html',f'התחזית הישנה · תרגיל {i}', '<p class="study-intro">ארכיון: נכתב 17/10/2026, לפני בחינת 19/10/2026. אינו תחזית מועד ב׳ המעודכנת.</p>'+paragraphs(q['stem'])+options(shown)+answer_key(shown)+clean(explanation),1)
report=re.search(r'<body>(.*)</body>',old['report'],re.S)[1]
report=re.sub(r'<nav\b.*?</nav>','',report,flags=re.S)
page('old-forecast.html','ארכיון התחזית מ-17/10/2026','<p class="study-intro">הדוח ההיסטורי נשמר להשוואה. הנתונים שבו משקפים את הניתוח הישן בלבד, שלא כלל את אוגוסט 2026. <a href="analysis.html">לבדיקת התחזית מול הבחינה בפועל</a></p>'+clean(report)+'<h2>50 התרגילים המקוריים</h2><ol>'+''.join(f'<li><a href="solutions/old-p{i:02}.html">תרגיל {i}: {e(q["topic"])}</a></li>' for i,q in enumerate(old['questions'],1))+'</ol>')

latest_body='''<p class="sub">19/10/2026 · סמסטר קיץ תשפ״ו · 10 שאלות · 80 דקות · 10 נקודות לשאלה.</p><div class="study-intro">הקובץ שסופק מציין בעמוד 2 שכל תשובות א׳ נכונות. להלן תמלול קריא ופתרון עצמאי לכל שאלה; ה-PDF המקורי הוא המקור הקובע לנוסח. בתרגול הדיגיטלי סדר החלופות מתערבב.</div><div class="study-actions"><a class="primary" href="index.html?set=latest">תרגלו את 10 שאלות מועד א׳</a><a href="2026/File_0_689156_19102026_0.pdf">פתיחת הבחינה המקורית</a><a href="analysis.html">איך התחזית הקודמת התאימה?</a></div>'''
for q in LATEST:
    latest_body+=f'<article class="study-card" id="q{q["sources"][0]["num"]}"><h2>שאלה {q["sources"][0]["num"]} · {e(q['title'])}</h2>'+paragraphs(q['stem'])+options(q)+'<details class="answer-detail"><summary>הצגת התשובה וההסבר המפורט</summary>'+answer_key(q)+answer(q)+'</details><p><a href="'+q['solution']+'">פתרון בעמוד נפרד</a></p></article>'
latest_body=latest_body.replace('בתרגול הדיגיטלי סדר החלופות מתערבב.', 'באתר סדר החלופות מתערבב בכל פתיחת שאלה או ניסיון חדש; האות א׳ שבקובץ אינה מפתח לסדר המוצג כאן.')
page('latest.html','מועד א׳ האחרון — שאלות ופתרונות',latest_body)

# Use one dated exam-question occurrence regardless of duplicate PDF copies.
bydate=defaultdict(dict)
for q in qbank:
    for s in q['sources']:
        if s.get('date'):bydate[s['date']][s['num']]=q
pairdata=[]
for label,a,b,note in PAIRS:
    aq=list(bydate[a].values());bq=list(bydate[b].values())
    at=set(q['topic'] for q in aq);bt=set(q['topic'] for q in bq)
    # Exact repeat: whitespace-normalized full stem and all options (order ignored).
    def norm(q):return (re.sub(r'\s+',' ',q['stem']).strip(),tuple(sorted(re.sub(r'\s+',' ',o).strip() for o in q['options'])))
    exact=[q['id'] for q in bq if norm(q) in {norm(x) for x in aq}]
    pairdata.append(dict(label=label,a=a,b=b,a_count=len(aq),b_count=len(bq),a_topics=sorted(at),b_topics=sorted(bt),shared=sorted(at&bt),b_in_a=sum(q['topic'] in at for q in bq),exact=exact,note=note))
save('data/pairs.json',pairdata)
save('data/forecast-audit.json',AUDIT)

intro=forecast_intro(pred)+'<div id="forecast-questions">'
for q in sorted(pred,key=lambda q:(-q['confidence'],q['id'])):
    intro+=f'<article class="study-card forecast-card" id="{q["id"]}" data-priority="{q["priority"]}" data-confidence="{q["confidence"]}"><p class="muted">{q["id"]} · סימולציה {q["mock"]} · {q["priority"]} · {e(q["topic"])}</p><h3>{e(q["title"])}</h3>'+paragraphs(q['stem'])
    intro+=confidence_summary(q)+options(q)
    intro+='<details class="answer-detail"><summary>בדקו תשובה והסבר</summary>'+answer_key(q)+answer(q)+'</details>'
    intro+='<p class="study-source">הראיות לבחירה: '+qlinks(q['evidence'])+'</p>'
    intro+=f'<div class="study-controls"><label><input type="checkbox" data-mastered="{q["id"]}"> שולט/ת בשאלה ובנימוק</label><a href="{q["solution"]}">פתרון בעמוד נפרד</a></div></article>'
intro+='</div>'
page('confidence.html','איך דירגנו את 60 שאלות התחזית?',confidence_page(confidence_report,pred))
page('best-mock.html','הסימולציה הממוקדת למועד ב׳ — 10 שאלות',mock_page(best_mock,pred))
page('predictions.html','לקראת מועד ב׳ — תחזית ותרגול',intro)

audit='''<p class="sub">בדיקה בדיעבד של התחזית הישנה, ואחריה ניתוח א׳→ב׳ לצורך תכנון הלמידה הבא.</p><div class="study-intro"><strong>לא נחשב ״דיוק״ לפי שם הנושא בלבד.</strong><p>ב-50 התרגילים שנכתבו לפני אוקטובר מצאנו 2 התאמות קרובות, 3 התאמות חלקיות ו-5 פערים ביחס ל-10 שאלות הבחינה. זהו סיווג ידני של כיסוי מיומנות, לא ציון צפוי ולא אומדן סטטיסטי של דיוק. תחזית רחבה של 50 שאלות אינה שקולה לניבוי של מבחן בן 10.</p></div><p><a href="old-forecast.html">התחזית הישנה והתרגילים המקוריים</a> · <a href="latest.html">בחינת אוקטובר בפועל</a></p><h2>התחזית מול כל שאלה בפועל</h2><p>״קרוב״: מנגנון הפתרון המרכזי תורגל במפורש. ״חלקי״: אותה משפחת מושגים, אך פעולה או הנחה חשובה השתנתה. ״פער״: אין תרגיל ישיר במיומנות בסט הישן. חומר הסבר רחב עשוי להזכיר יותר נושאים; הטבלה אינה טוענת שהמושג נעדר מכל מסמך בתיקייה.</p><div class="study-table"><table><thead><tr><th>שאלה בפועל</th><th>סיווג</th><th>תרגול ישן</th><th>מה למדנו</th></tr></thead><tbody>'''
for row in AUDIT:
    q=LATEST[row['num']-1]
    refs=' · '.join(f'<a href="solutions/old-p{i:02}.html">{i}</a>' for i in row['old']) or '—'
    audit+=f'<tr><td><a href="{q["solution"]}">{row["num"]} · {e(q["title"])}</a></td><td>{row["status"]}</td><td>{refs}</td><td>{e(row["why"])}</td></tr>'
audit+='''</tbody></table></div><h2>מה השתנה בגישה</h2><p>התחזית הישנה שמה דגש ניכר על TLS, HSTS, CSP ומרקל, שלא הופיעו כשאלות ישירות באוקטובר. היא גם לא כללה בניתוח את בחינת 09/08/2026 שהייתה קיימת באוסף המעודכן. הפעם נכלל הזוג הזה, התרגול מתמקד בפעולה שנבחנת ולא רק בשם נושא, ונוסף כיסוי לספירת מפתחות, אימות RSA ושינוי פעיל של OTP.</p><p>לא ניתן להסיק מהחומר מדוע התקבל ציון מסוים: אין כאן דף תשובות אישי או פירוט בדיקת הנבחן. אין לייחס את כל הפער לתחזית, ואין לטעון שכיסוי נושאים היה מבטיח ציון.</p><h2>שבעה זוגות א׳/ב׳ מאומתים</h2><p>השיוך נבדק מול שערי השאלונים: אותה שנה אקדמית ואותו סמסטר, מועד א׳ מול מועד ב׳. לא מצמידים את אוקטובר 2026 לאוגוסט 2026: אלה סמסטרים שונים, ואוגוסט קודם לאוקטובר. מועדים מיוחדים אינם נספרים כמועד ב׳. עותקים כפולים באותו תאריך נספרים פעם אחת.</p><p>בטבלה, ״כיסוי רחב״ הוא מספר שאלות ב׳ שהנושא הראשי שלהן הופיע לפחות פעם בא׳. זהו מדד גס ולא חזרת שאלות. ״זהות מלאה״ משווה את נוסח השאלה וכל החלופות לאחר נרמול רווחים; שינויים קטנים בניסוח לא נספרים בזהות.</p><div class="study-table"><table><thead><tr><th>זוג</th><th>מועדים ומקורות</th><th>כיסוי רחב של ב׳ מנושאי א׳</th><th>זהות מלאה</th><th>תובנה</th></tr></thead><tbody>'''
for p in pairdata:
    qa=next(iter(bydate[p['a']].values()));qb=next(iter(bydate[p['b']].values()))
    sa=next(s for s in qa['sources'] if s['date']==p['a']);sb=next(s for s in qb['sources'] if s['date']==p['b'])
    audit+=f'<tr><td>{p["label"]}</td><td><a href="{url(sa["file"])}">א׳ {p["a"]}</a><br><a href="{url(sb["file"])}">ב׳ {p["b"]}</a></td><td>{p["b_in_a"]}/{p["b_count"]}</td><td>{len(p["exact"])}/{p["b_count"]}</td><td>{e(p["note"])}</td></tr>'
audit+='</tbody></table></div><h2>חזרת משפחות נושאים</h2><p>לכל נושא: בכמה משבעת מועדי א׳ הופיע; בכמה מועדי ב׳; ובכמה זוגות שבהם הופיע בא׳ חזר גם בב׳. כל שאלה משויכת לנושא ראשי יחיד, ולכן שאלות משולבות מאבדות מידע. סיווגי CSP ונעילת חשבון שתויגו אוטומטית לא נכון באתר המקורי תוקנו. המדגם קטן ונבחר מראש, ולכן המספרים אינם הסתברויות לבחינה הבאה.</p><div class="study-table"><table><thead><tr><th>נושא</th><th>א׳ מתוך 7</th><th>ב׳ מתוך 7</th><th>חזרה בב׳ כשנכח בא׳</th><th>דוגמה ממועד ב׳</th></tr></thead><tbody>'
topicstats=[]
for topic in TOPICS:
    ac=sum(topic in p['a_topics'] for p in pairdata);bc=sum(topic in p['b_topics'] for p in pairdata);both=sum(topic in p['shared'] for p in pairdata)
    examples=[q['id'] for p in reversed(pairdata) for q in bydate[p['b']].values() if q['topic']==topic][:2]
    topicstats.append(dict(topic=topic,a=ac,b=bc,both=both))
    audit+=f'<tr><td>{e(topic)}</td><td>{ac}</td><td>{bc}</td><td>{both}/{ac} זוגות</td><td>{qlinks(examples)}</td></tr>'
audit+='</tbody></table></div><h2>מגבלות והסקה</h2><p>18 מועדים מתוארכים כלולים במאגר המעודכן; שבעה זוגות בלבד מתאימים להשוואת א׳/ב׳. ניתוח הכיסוי נעשה על שאלות ברירה בלבד: 186 הופעות לפי תאריך, המאוחדות ל-182 נוסחים ייחודיים באתר. אין כאן בחינה של תחזית קפואה מראש על כמה מחזורי א׳/ב׳, ולכן לא נטען שהשיטה החדשה כבר הוכחה כמדויקת יותר. בחירת התרגילים היא שיקול לימודי לאחר צפייה בכל החומר, עם קישורים לראיות.</p><p>תבנית שימושית היא חזרה על משפחת מושגים תוך החלפת פעולה: יצירת חתימה מול אימותה, preimage מול second preimage, מטרת CT מול תנאי אכיפתו. תבנית זו מצדיקה ללמוד מנגנון והנחות, לא לשנן אות תשובה או להמר על ניסוח.</p><h2>מקורות טכניים להשלמה</h2><p>השאלונים והפתרונות המקומיים הם בסיס הניתוח. המקורות הבאים משמשים לבדיקת מנגנונים ומגבלות, לא לחיזוי שאלות. שאלות TLS ההיסטוריות עשויות להשתמש במודל RSA key exchange ישן; אין להחיל אותו על TLS 1.3.</p><ul>'+''.join('<li><a href="'+u+'">'+e(t)+'</a></li>' for t,u in SOURCES)+'</ul><p><a href="data/pairs.json">נתוני הזוגות JSON</a> · <a href="data/forecast-audit.json">מיפוי התחזית הישנה JSON</a></p>'
summer=[p for p in pairdata if 'קיץ' in p['label']]
summertext='<h2>מה רואים דווקא בסמסטר קיץ?</h2><p>הבחינה האחרונה היא מסמסטר קיץ. לכן כדאי להסתכל גם על שלושת זוגות הקיץ בלבד (2022, 2024, 2025), ולא להניח שכל סמסטר זהה. בשלושת מועדי ב׳ האלה הופיעו PKI, ביטקוין, הצפנה סימטרית/קלאסית, Web ו-RSA/חתימות לפי הסיווג הרחב. זהו מדגם של שלושה בלבד, וב-2022 מבנה הבחינה שונה; אין להצמיד ל-3/3 הסתברות של 100%.</p><p>הניתוח של כלל שבעת הזוגות מצביע גם על DH ורשתות כתוספת אפשרית. ביולי→אוגוסט 2026 נעלמו שאלות Web ו-TLS ישירות למרות הופעתן בא׳. לכן סדר הלמידה משלב עדיפות למשפחות החוזרות בקיץ עם תרגול גיבוי, ואינו מעתיק את תמהיל אוקטובר.</p>'
assert len(summer)==3
assert all(all(TOPICS[i] in p['b_topics'] for i in [0,1,4,6,8]) for p in summer)
audit=audit.replace('<h2>מגבלות והסקה</h2>',summertext+'<h2>מגבלות והסקה</h2>')
page('analysis.html','בדיקת התחזית וניתוח מועדי א׳/ב׳','<p><a href="confidence.html">חדש: ציוני ביטחון ל-60 שאלות, עם ראיות מכל 18 המועדים</a></p>'+audit)
save('data/topic-stats.json',topicstats)

arch='<p>כל 182 שאלות המאגר מקושרות לפתרון מפורט. 162 פתרונות מבוססים על קובצי התיקייה שסופקה; נוספו 10 פתרונות לאוגוסט 2026 ו-10 לאוקטובר 2026. הסעיפים הפתוחים של 2022 זמינים גם הם במסמכים המלאים למטה. הפתרונות הם חומר לימוד עצמאי, גם כאשר מפתח התשובות מגיע מהבחינה.</p><div class="study-actions"><a href="index.html#bank">חיפוש במאגר</a><a href="latest.html">אוקטובר 2026</a><a href="old-forecast.html">תחזית אוקטובר המקורית</a></div><h2>לפי מועד — ללא כפילות קבצים</h2>'
for date,qq in sorted(bydate.items(),key=lambda it:tuple(reversed(it[0].split('/'))),reverse=True):
    arch+='<details class="study-card"><summary>'+date+' · '+str(len(qq))+' שאלות ברירה</summary><ol>'+''.join('<li><a href="'+q['solution']+'">שאלה '+str(num)+' · '+e(q.get('title',q['topic']))+'</a></li>' for num,q in sorted(qq.items()))+'</ol></details>'
arch=question_type_filter()+arch
arch+='<h2>מסמכי פתרונות לפי קובץ מקור</h2><ul>'+''.join(f'<li data-archive-document data-mc-count="{n-o}" data-open-count="{o}"><a href="{p}"><bdi>{e(name)}</bdi></a> · <span data-archive-count>{n-o} שאלות בחירה</span></li>' for name,p,n,o in archive_links)+'</ul>'
page('archive.html','ארכיון בחינות ופתרונות מלאים',arch)

template=(R/'scripts/index.template.html').read_text(encoding='utf-8')
template=template.replace('__BANK_JSON__',json.dumps(original,ensure_ascii=False,separators=(',',':')))
template=template.replace('__BEST_MOCK_JSON__',json.dumps(best_mock,ensure_ascii=False,separators=(',',':')))
template=template.replace('const QS = BANK.questions.filter(q => !q.exclude);', '''const FORECAST = '''+json.dumps(pred,ensure_ascii=False,separators=(',',':'))+''';
const requestedSet = new URLSearchParams(location.search).get('set') || '';
const selectedSet = ['latest','forecast-all','forecast-focus','forecast-best',...Array.from({length:6},(_,i)=>'forecast-'+(i+1))].includes(requestedSet) ? requestedSet : '';
const isForecast = /^forecast-([1-6]|all|focus|best)$/.test(selectedSet);
const rankedForecast = [...FORECAST].sort((a,b)=>b.confidence-a.confidence || a.id.localeCompare(b.id));
const QS = selectedSet==='forecast-best' ? BEST_MOCK.question_ids.map(id=>FORECAST.find(q=>q.id===id)) : isForecast ? (selectedSet==='forecast-focus' ? rankedForecast.slice(0,20) : FORECAST.filter(q => q.question_type==='multiple-choice' && (selectedSet==='forecast-all' || q.mock===Number(selectedSet.slice(-1))))) : BANK.questions.filter(q => q.question_type==='multiple-choice' && !q.exclude && (selectedSet!=='latest' || q.sources.some(s=>s.date==='19/10/2026')));
const collectionName = selectedSet==='forecast-best' ? 'הסימולציה הממוקדת למועד ב׳ — 10 שאלות בתמהיל היסטורי' : isForecast ? 'תרגול תחזית מועד ב׳ — שאלות שחוברו לתרגול' : selectedSet==='latest' ? 'מועד א׳ · 19/10/2026' : 'מאגר הבחינות';''')
template=template.replace('</head>','<link rel="stylesheet" href="'+asset('study.css')+'"><script src="'+asset('answer-order.js')+'"></script></head>')
template=template.replace('אותו קוד = אותו מבחן', 'אותו קוד = אותן שאלות; סדר התשובות מתחדש')
template=template.replace('</body>', '<script src="'+asset('study.js')+'" defer></script></body>')
template=template.replace('<main ', '<main ',1)
template=template.replace('<body>','<body><a class="skip-link" href="#app">דלג לתוכן</a>')
template=template.replace('</header>','''</header><div class="study-banner"><div class="wrap"><a href="predictions.html">תחזית מועד ב׳ · 60 שאלות ופתרונות</a><a href="latest.html">בחינת אוקטובר 2026</a><a href="analysis.html">בדיקת התחזית הקודמת</a><a href="archive.html">כל הפתרונות</a><a href="index.html#setup">כל מאגר הבחינות</a></div></div>''',1)
template=template.replace('function renderStats(app){', '''function renderStats(app){
  if(isForecast){app.innerHTML='<div class="panel stack"><h2>תחזית אינה נתון היסטורי</h2><p>השאלות בסט הזה נבחרו לתרגול. אין להציג אותן כהופעות במבחני עבר.</p><a href="analysis.html">ניתוח א׳/ב׳ והראיות לבחירה</a><a href="index.html#stats">סטטיסטיקת מאגר הבחינות</a></div>';return;}''')
template=template.replace('בוחרים שאלות מתוך ${QS.length} השאלות שנאספו מ-${countExams()} מבחנים, מערבבים, ומתחילים.', '${esc(collectionName)} · ${QS.length} שאלות זמינות. בוחרים מצב, מערבבים ומתחילים. לכל שאלה פתרון מפורט לאחר המענה.')
# Isolate history from other GitHub Pages applications sharing the eldarush origin.
template=template.replace('localStorage.getItem(k)', "localStorage.getItem('cyber-study-v2:'+k)").replace('localStorage.setItem(k,', "localStorage.setItem('cyber-study-v2:'+k,")
template=template.replace('function srcLabel(q){', "function srcLabel(q){ if(q.id.startsWith('P')) return 'תרגיל תחזית '+q.id+' · אינו שאלת בחינה מקורית';")
template=template.replace("/* ---------- seeded random ---------- */",'''function solutionDetails(q){return `<details class="answer-detail"><summary>פתרון מפורט — הסבר וניתוח הטעויות</summary><p class="correct"><b>התשובה הנכונה:</b> ${esc(q.options[0])}</p><p class="study-source">${esc(q.answer_origin || '')} · אותיות בפתרון מיובא מתייחסות למקור, ולא לסדר שהוגרל.</p>${q.answer_html}<p><a href="${q.solution}" target="_blank" rel="noopener">פתרון בעמוד נפרד</a></p></details>`;}
/* ---------- seeded random ---------- */''')
template=template.replace('function solutionDetails(q){', '''function isCorrect(q,index){return (q.accepted_indices || [0]).includes(index);}
function correctLetters(item){return item.order.map((oi,j)=>isCorrect(item.q,oi)?LET[j]:null).filter(Boolean).join(' / ');}
function confidenceBadge(q){return q.confidence ? `<p class="study-source"><b>ביטחון במיומנות: ${q.confidence}/100</b> · מדד שיפוטי, לא הסתברות לניסוח המדויק · <a href="confidence.html" target="_blank" rel="noopener">שיטת הדירוג</a></p>` : '';}
function solutionDetails(q){''')
template=template.replace('<p class="correct"><b>התשובה הנכונה:</b> ${esc(q.options[0])}</p>', '<p class="correct">${q.accepted_indices?.length>1 ? `<b>הערת בדיקה: ${esc(q.note)}</b> · ההסבר מפרט את ההסתייגות; הניקוד מכבד את החלופות שהתקבלו.` : `<b>התשובה הנכונה:</b> ${esc(q.options[0])}`}</p>')
for oldexpr,newexpr in [
 ('x.order[x.ans] === 0','isCorrect(x.q,x.order[x.ans])'),
 ('x.order[x.ans]===0','isCorrect(x.q,x.order[x.ans])'),
 ('x.order[x.ans] !== 0','!isCorrect(x.q,x.order[x.ans])'),
 ('x.order[x.ans]!==0','!isCorrect(x.q,x.order[x.ans])'),
 ('it.order[it.ans]===0','isCorrect(it.q,it.order[it.ans])'),
 ('x.order[j]===0','isCorrect(x.q,x.order[j])'),
 ('oi===0','isCorrect(q,oi)'),
 ('B.show&&i===0','B.show&&isCorrect(q,i)'),
 ('LET[it.order.indexOf(0)]','correctLetters(it)'),
 ('LET[items[i].order.indexOf(0)]','correctLetters(items[i])')]:
    template=template.replace(oldexpr,newexpr)
template=template.replace("mark='<span class=\"mark okm\">✓ נכונה</span>';", "mark=q.accepted_indices.length>1?'<span class=\"mark okm\">✓ מתקבלת</span>':'<span class=\"mark okm\">✓ נכונה</span>';")
template=template.replace("isCorrect(q,oi) ? '<span class=\"mark okm\">✓ נכונה</span>'", "isCorrect(q,oi) ? (q.accepted_indices.length>1?'<span class=\"mark okm\">✓ מתקבלת</span>':'<span class=\"mark okm\">✓ נכונה</span>')")
template=template.replace("isCorrect(it.q,it.order[it.ans]) ? '✓ נכון.'", "isCorrect(it.q,it.order[it.ans]) ? (q.accepted_indices.length>1?'✓ התשובה התקבלה בבדיקה המקורית.':'✓ נכון.')")
template=template.replace("</div>` : ''}\n        <div class=\"qnav\">", "</div>${solutionDetails(q)}` : ''}\n        <div class=\"qnav\">")
template=template.replace('<span class="mono">${q.id}</span></div>','<span class="mono">${q.id}</span></div>${solutionDetails(q)}')
template=template.replace("${q.note?`<div class=\"meta-line\">${esc(q.note)}</div>`:''}","${q.note?`<div class=\"meta-line\">${esc(q.note)}</div>`:''}${solutionDetails(q)}")
template=template.replace('tabFromHash();\nrender();', '''if ((S.cfg.collection || '') !== selectedSet) {
  S.cfg = {...S.cfg, collection:selectedSet, mode:selectedSet==='forecast-best'?'digital':S.cfg.mode, n:selectedSet==='forecast-best'?10:Math.min(S.cfg.n,QS.length),topics:[],years:[],wrongOnly:false,skipNoted:false,minutes:null,shuffle:true,onlyMultipleChoice:true};
  store.set('cfg', S.cfg);
}
tabFromHash();
render();''')
assert template.count('solutionDetails(q)')>=4
write('index.html',template)
# Retire inherited HTML copies that could bypass the current answer shuffling.
# Original source PDFs stay intact as archival evidence.
legacy_pages=['מאגר שאלות/app.html','מאגר שאלות/exams/answer_key.html','מאגר שאלות/exams/exam_v1.html','מאגר שאלות/exams/exam_v2.html','מאגר שאלות/exams/exam_v3.html','מאגר שאלות/exams/practice/answer_key.html','מאגר שאלות/exams/practice/practice_v1.html']
for path in legacy_pages:
    target='../'*(len(Path(path).parts)-1)+'index.html#setup'
    write(path,'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url='+target+'"><title>תרגול מעודכן</title></head><body><p>התרגול וההדפסה זמינים בגרסה המעודכנת, עם ערבוב אוטומטי ומפתח תואם.</p><a href="'+target+'">פתיחת התרגול המעודכן</a></body></html>')
write('.nojekyll','')
save('data/build-summary.json',dict(actual_questions=len(qbank),dated_occurrences=sum(len(v) for v in bydate.values()),dated_exams=len(bydate),paired_exams=len(pairdata),predicted_questions=len(pred),reused_answers=162,new_answers=20,archive_documents=len(archive),built='2026-11-14'))
print(json.dumps(load('data/build-summary.json')))
