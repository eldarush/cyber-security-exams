"""Independent arithmetic and structural checks for the 30 reviewed exercises."""
from decimal import Decimal
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit
import json
import math

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = {q['id']: q for q in json.loads((ROOT/'data/forecast.json').read_text(encoding='utf-8'))}

assert len(QUESTIONS) == 30
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

vig = ''.join(chr(65+(ord(p)-65+ord('KEY'[i%3])-65)%26) for i, p in enumerate('HELLO'))
assert QUESTIONS['P10']['options'][0] == vig == 'RIJVS'

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
print('Forecast review: 30 multiple-choice questions, 120 option explanations, arithmetic and boundary checks passed.')
