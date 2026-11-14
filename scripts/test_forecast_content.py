"""Independent arithmetic and structural checks for the 60 reviewed exercises."""
from decimal import Decimal
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit
import json
import math

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = {q['id']: q for q in json.loads((ROOT/'data/forecast.json').read_text(encoding='utf-8'))}

assert len(QUESTIONS) == 60
for q in QUESTIONS.values():
    assert q['question_type'] == 'multiple-choice'
    assert q['accepted_indices'] == [0]
    assert len(q['options']) == len(set(q['options'])) == 4
    assert q['reviewed'] == '2026-11-14'
    reasons = q['option_explanations']
    assert [r['option'] for r in reasons] == q['options'], q['id']
    assert [r['correct'] for r in reasons] == [True, False, False, False]
    assert all(len(r['reason'].split()) >= 8 for r in reasons), q['id']
    assert q['answer_html'].count('data-option-review=') == 4
    assert 'העמקה ודוגמה נוספת מהבחינה המקורית' not in q['answer_html']

# RSA: evaluate every offered signature, not only the keyed answer.
assert [pow(int(s), 5, 35) == 2 for s in QUESTIONS['P01']['options']] == [True, False, False, False]
assert [(3*int(d)) % ((5-1)*(11-1)) == 1 for d in QUESTIONS['P16']['options']] == [True, False, False, False]
assert Decimal('2')+Decimal('1.5')-Decimal('2.8')-Decimal('.02') == Decimal('.68')
assert QUESTIONS['P03']['options'][0].startswith('0.68 ')

# OTP: all byte keys, several distinct source/target messages, including zero.
for m in [0, 1, 7, 128, 255]:
    for target in [0, 1, 7, 128, 255]:
        if m == target:
            continue
        for key in range(256):
            c = m ^ key
            assert (c ^ m ^ target) ^ key == target
            assert (c ^ target) ^ key == m ^ target
            assert (c ^ key ^ key) ^ key == m

# Exact birthday probability distinguishes the approximation from its threshold.
n = 2**24
prob = lambda k: -math.expm1(sum(math.log1p(-i/n) for i in range(k)))
assert prob(4822) < .5 <= prob(4823)
assert round(math.sqrt(2*math.log(2)*n)) == 4823
assert QUESTIONS['P07']['options'][0] == 'כ-4,823'

a, b = pow(5, 6, 23), pow(5, 15, 23)
assert (a, b) == (8, 19)
shared = pow(b, 6, 23)
assert shared == pow(a, 15, 23) == 2
assert QUESTIONS['P09']['options'][0] == str(shared)
assert [int(option)==shared for option in QUESTIONS['P09']['options']] == [True,False,False,False]

vig = ''.join(chr(65+(ord(p)-65+ord('KEY'[i%3])-65)%26) for i, p in enumerate('HELLO'))
assert QUESTIONS['P10']['options'][0] == vig == 'RIJVS'
assert [option==vig for option in QUESTIONS['P10']['options']] == [True,False,False,False]

# P08: deficit catch-up probabilities illustrate why "smaller" is not
# necessarily "small". Deficit z is NOT automatically the confirmation count.
for attacker in [.1,.3,.49]:
    probabilities = [(attacker/(1-attacker))**z for z in range(1,11)]
    assert all(0<later<earlier<1 for earlier,later in zip(probabilities,probabilities[1:]))
assert (.49/.51)**6 > .7
assert 'פוחת' in QUESTIONS['P08']['options'][0]
assert 'קטן מ-50%' in QUESTIONS['P08']['stem']
assert 'אינו רשאי לבחור או לשנות' in QUESTIONS['P15']['stem']

# CBC dependency wiring using an invertible toy byte permutation. This checks
# which blocks change; it does not claim to measure AES's avalanche properties.
enc = lambda value: (197*value+101) % 256
dec = lambda value: (pow(197, -1, 256)*(value-101)) % 256
plain, iv = [17, 66, 203, 91, 4, 189], 37
cipher = []
previous = iv
for value in plain:
    previous = enc(value ^ previous)
    cipher.append(previous)
for bit in range(8):
    changed = cipher.copy()
    changed[3] ^= 1 << bit
    recovered = [dec(value) ^ (iv if i == 0 else changed[i-1]) for i, value in enumerate(changed)]
    assert [i+1 for i, (x,y) in enumerate(zip(plain,recovered)) if x != y] == [4,5]
    assert recovered[4] == plain[4] ^ (1 << bit)
assert 'לפחות חמישה בלוקים' in QUESTIONS['P13']['stem']

# Build actual Merkle paths; each sibling list has 11 hashes and reconstructs
# the trusted root. An altered sibling fails the check.
leaves = [sha256(str(i).encode()).digest() for i in range(2048)]
levels = [leaves]
while len(levels[-1]) > 1:
    row = levels[-1]
    levels.append([sha256(row[i]+row[i+1]).digest() for i in range(0,len(row),2)])
for leaf in [0, 1, 1023, 2047]:
    index = leaf
    proof = []
    for row in levels[:-1]:
        proof.append((row[index ^ 1], index % 2))
        index //= 2
    assert len(proof) == int(QUESTIONS['P14']['options'][0]) == 11
    def verify(path):
        value = leaves[leaf]
        for sibling, right in path:
            value = sha256(sibling+value if right else value+sibling).digest()
        return value == levels[-1][0]
    assert verify(proof)
    assert not verify([(bytes(32),proof[0][1])]+proof[1:])

assert len(list(combinations(range(20), 2))) == 190
assert QUESTIONS['P21']['options'][0].startswith('190 ')
assert all(enc(p) == enc(p) and (p == q or enc(p) != enc(q)) for p in range(256) for q in range(256))
h = lambda s: sum(ord(c)-ord('a') for c in s) % 26
assert h('ab') == h('ba') == 1
assert [h(s) for s in ['a','b','c']] == [0,1,2]
assert all(h(s+'a') == h(s) for s in ['a','bc','test','xyz'])

def origin(url):
    parsed = urlsplit(url)
    return parsed.scheme, parsed.hostname, parsed.port or {'http':80,'https':443}[parsed.scheme]
pairs = [option.split(' וכן ') for option in QUESTIONS['P25']['options']]
assert [origin(a) == origin(b) for a,b in pairs] == [True,False,False,False]
assert QUESTIONS['P29']['options'][0] == f'1/{2**16}'
# New variations: evaluate every numerical answer, not only the expected key.
assert [pow(int(x),3,55)==9 for x in QUESTIONS['P31']['options']] == [True,False,False,False]
assert pow(9,27,55)==4 and [pow(x,3,55) for x in [4,9,14,27]]==[9,14,49,48]
assert [pow(int(x),3,55)==8 for x in QUESTIONS['P32']['options']] == [True,False,False,False]
assert pow(8,27,55)==2
assert [math.gcd(int(x),60)==1 and 1<int(x)<60 for x in QUESTIONS['P34']['options']] == [True,False,False,False]
assert 7*43 % 60 == 1
assert Decimal('.6')+Decimal('.5') > Decimal('1')
assert set(combinations('ABT',2)) == {('A','B'),('A','T'),('B','T')}

# Enumerate a small ideal PoW output space: reducing T reduces success rate
# linearly, rather than by the square-root birthday relationship.
from fractions import Fraction
p=Fraction(sum(h<128 for h in range(256)),256)
p_small=Fraction(sum(h<8 for h in range(256)),256)
assert (1/p_small)/(1/p)==16
assert QUESTIONS['P43']['options'][0]=='גדל פי 16'

def merkle_levels(leaves):
    levels=[[sha256(x).digest() for x in leaves]]
    while len(levels[-1])>1:
        last=levels[-1]
        levels.append([sha256(last[i]+last[i+1]).digest() for i in range(0,len(last),2)])
    return levels
leaves=[bytes([i]) for i in range(32)]
original=merkle_levels(leaves)
for pos in range(32):
    changed=leaves.copy();changed[pos]=b'changed'+changed[pos]
    after=merkle_levels(changed)
    differences=[sum(a!=b for a,b in zip(x,y)) for x,y in zip(original,after)]
    assert differences == [1,1,1,1,1,1] # one changed leaf, five internal ancestors
assert QUESTIONS['P44']['options'][0]=='5'

assert [int(x,16)==(0xA6^0x3C^0x55) for x in QUESTIONS['P45']['options']] == [True,False,False,False]
assert 0x55^0xF3==0xA6 and 0xCF^0xF3==0x3C
# Dependency check using an independently constructed invertible byte cipher;
# this verifies CBC wiring, not the security of a real block cipher.
enc=lambda x:(197*x+31)%256
dec=lambda x:((x-31)*pow(197,-1,256))%256
plain=[10,20,30,40];iv=71;cipher=[];previous=iv
for value in plain:
    previous=enc(value^previous);cipher.append(previous)
for bit in range(8):
    prev=iv^(1<<bit);decoded=[]
    for value in cipher:
        decoded.append(dec(value)^prev);prev=value
    assert decoded==[plain[0]^(1<<bit),*plain[1:]]
for message in range(256):
    assert enc(dec(enc(message)))==enc(message) # EDE equal-key identity
def pattern(s):
    return tuple(s.index(ch) for ch in s)
assert [pattern(x)==pattern('ABBA') for x in QUESTIONS['P48']['options']]==[True,False,False,False]
def encrypt_vigenere(plain,key):
    return ''.join(chr(65+(ord(c)-65+ord(key[i%len(key)])-65)%26) for i,c in enumerate(plain))
assert [encrypt_vigenere('ATTACK',key)=='DHZDQQ' for key in QUESTIONS['P49']['options']]==[True,False,False,False]
assert [int(x)%256==42 for x in QUESTIONS['P51']['options']]==[True,False,False,False]
assert 2**40>2**24
import hmac
tag=hmac.digest(b'example-test-key',b'command','sha256')
assert hmac.compare_digest(tag,hmac.digest(b'example-test-key',b'command','sha256'))
assert not hmac.compare_digest(tag,hmac.digest(b'example-test-key',b'changed-command','sha256'))
assert len({q['stem'] for q in QUESTIONS.values()})==60
print('Forecast review: 60 multiple-choice questions, 240 option explanations, arithmetic and boundary checks passed.')
