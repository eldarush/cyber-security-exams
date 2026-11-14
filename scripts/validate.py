"""Content-integrity checks for the generated public study site (stdlib only)."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from decimal import Decimal
import json,re,math,subprocess,tempfile

R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text(encoding='utf-8'))
bank=load('data/bank.json')['questions'];forecast=load('data/forecast.json');pairs=load('data/pairs.json')
assert len(bank)==182 and len(forecast)==30 and len(pairs)==7
assert len({q['id'] for q in bank+forecast})==212
assert all(sum(q['mock']==n for q in forecast)==10 for n in [1,2,3])
assert all(len(q['options'])==4 and len(set(q['options']))==4 for q in bank+forecast)
for q in bank+forecast:
    assert (R/q['solution']).exists(),q['id']
    assert len(re.sub('<[^>]*>',' ',q['answer_html']).split())>=85,q['id']
    for s in q['sources']: assert (R/s['file']).exists(),(q['id'],s)
    for ev in q.get('evidence',[]): assert any(x['id']==ev for x in bank),(q['id'],ev)
assert sum(len({(s['date'],s['num']) for s in q['sources'] if s.get('date')}) for q in bank)==186
assert all(not s.get('date') for q in forecast for s in q['sources'])
assert [p['b_in_a'] for p in pairs]==[8,8,9,6,8,10,7]
assert {q['id']:q['accepted_indices'] for q in bank if len(q['accepted_indices'])>1}=={'Q013':[0,1,2,3],'Q021':[0,1],'Q038':[0,1],'Q055':[0,1]}
assert sum(len(p['exact']) for p in pairs)==0
assert {k:sum(x['status']==k for x in load('data/forecast-audit.json')) for k in ['קרוב','חלקי','פער']}=={'קרוב':2,'חלקי':3,'פער':5}

def vig(p,k):return ''.join(chr((ord(ch)-65+ord(k[i%len(k)])-65)%26+65) for i,ch in enumerate(p))
assert vig('ATTACKATDAWN','LEMON')=='LXFOPVEFRNHR'
assert vig('HELLO','KEY')=='RIJVS'
assert [pow(x,3,33) for x in [16,25,13,5]]==[4,16,19,26]
assert [pow(x,5,35) for x in [32,2,3,5]]==[2,32,33,10]
assert 100*99//2==4950 and 20*19//2==190
assert Decimal('5')-Decimal('3')-Decimal('0.1')==Decimal('1.9')
assert Decimal('2')+Decimal('1.5')-Decimal('2.8')-Decimal('0.02')==Decimal('0.68')
assert pow(3,5,23)==13 and pow(3,3,23)==4 and pow(4,5,23)==pow(13,3,23)==12
assert bytes(a^b for a,b in zip(b'YES',b'NO!')).hex()=='170a72'
assert round(math.sqrt(2*math.log(2)*2**24))==4823
for key in [bytes([0,0,0]),bytes([255,128,17]),b'abc']:
    c=bytes(a^b for a,b in zip(b'YES',key))
    changed=bytes(a^b^d for a,b,d in zip(c,b'YES',b'NO!'))
    assert bytes(a^b for a,b in zip(changed,key))==b'NO!'

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for attr in ['href','src']:
            if attr in attrs:self.links.append(attrs[attr])

files=[R/f for f in ['index.html','latest.html','predictions.html','analysis.html','archive.html','old-forecast.html']]+list((R/'solutions').glob('*.html'))
parsed={}
for p in files:
    h=Links();h.feed(p.read_text(encoding='utf-8'));parsed[p.resolve()]=h
    assert len(h.ids)==len(set(h.ids)),('duplicate ID',p)
links=0
for p,h in parsed.items():
    for link in h.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        assert target.exists(),('missing local link',p,link)
        if u.fragment and target in parsed:
            if target.name=='index.html' and u.fragment in ['setup','bank','stats']:continue
            assert unquote(u.fragment) in parsed[target].ids,('missing anchor',p,link)
        links+=1

# Validate inline scripts as JavaScript without executing DOM or network code.
scripts=re.findall(r'<script>(.*?)</script>',(R/'index.html').read_text(encoding='utf-8'),re.S)
with tempfile.TemporaryDirectory() as t:
    p=Path(t)/'inline.js';p.write_text('\n'.join(scripts),encoding='utf-8')
    subprocess.run(['node','--check',str(p)],check=True,capture_output=True)
subprocess.run(['node','--check',str(R/'study.js')],check=True,capture_output=True)
subprocess.run(['node','--check',str(R/'answer-order.js')],check=True,capture_output=True)
subprocess.run(['node',str(R/'scripts/test-answer-order.cjs')],check=True)
for p in files:
    doc=p.read_text(encoding='utf-8')
    for attrs,body in re.findall(r'<ol (class="study-options"[^>]*)>(.*?)</ol>',doc,re.S):
        assert 'data-accepted=' in attrs and 'id="opts-' in attrs,p
        assert sorted(map(int,re.findall(r'data-option-index="(\d+)"',body)))==[0,1,2,3],p
        assert body.count('class="option-letter"')==4,p
        list_id=re.search(r'id="([^"]+)"',attrs)[1]
        assert 'data-answer-for="'+list_id+'"' in doc,p
        assert 'answer-order.js' in doc and 'study.js' in doc,p
print(json.dumps({'html_pages_checked':len(files),'local_links_checked':links,'past_questions':182,'forecast_questions':30,'pairs':7,'arithmetic':'passed','javascript_syntax':'passed'},indent=2))
