const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const AnswerOrder = require('../answer-order.js');
const source = fs.readFileSync(path.join(root, 'index.html'), 'utf8');

// Exercise every Fisher-Yates branch for four choices, including the identity
// permutation, which remains a legitimate random outcome.
const permutations = new Map();
for (let a = 0; a < 4; a++) for (let b = 0; b < 3; b++) for (let c = 0; c < 2; c++) {
  const draws = [(a + .5) / 4, (b + .5) / 3, (c + .5) / 2];
  const order = AnswerOrder.indices(4, () => draws.shift());
  assert.deepEqual([...order].sort(), [0, 1, 2, 3]);
  permutations.set(order.join(), order);
}
assert.equal(permutations.size, 24);

const helpers = source.match(/function isCorrect\(q,index\)\{[\s\S]*?(?=function solutionDetails)/)[0];
const finish = source.match(/function finish\(timeUp\)\{[\s\S]*?(?=\/\* ---------- results)/)[0];
const makeItems = source.match(/function makeItems\(qs, r\)\{[\s\S]*?(?=function start\()/)[0];
const context = vm.createContext({ AnswerOrder, LET: ['א','ב','ג','ד'], Date,
  clearInterval() {}, timerId: null, go() {}, store: { get() { return []; }, set() {} }, S: {} });
vm.runInContext(helpers + finish + makeItems, context);
for (const order of permutations.values()) for (const accepted of [[0], [0, 1], [0, 1, 2, 3]]) {
  const q = { id: 'test', topic: 'test', options: ['a', 'b', 'c', 'd'], accepted_indices: accepted };
  for (let selected = 0; selected < 4; selected++) {
    context.S.exam = { mode: 'digital', start: Date.now(), items: [{ q, order, ans: selected }] };
    vm.runInContext('finish(false)', context);
    assert.equal(context.S.result.score, accepted.includes(order[selected]) ? 100 : 0);
    context.item = { q, order };
    const expectedLetters = order.flatMap((oi, j) => accepted.includes(oi) ? ['אבגד'[j]] : []).join(' / ');
    assert.equal(vm.runInContext('correctLetters(item)', context), expectedLetters);
  }
}
// Persisted legacy shuffle:false and fixed_order fields cannot bypass shuffling.
let called = false;
context.AnswerOrder = { indices() { called = true; return [3, 2, 1, 0]; } };
context.S.cfg = { shuffle: false };
context.questions = [{ options: ['a','b','c','d'], fixed_order: true }];
assert.equal(vm.runInContext('makeItems(questions)[0].order.join()', context), '3,2,1,0');
assert(called);
assert(!source.includes('id="f-shuffle"'));
console.log('Answer ordering: all 24 permutations, 288 grading cases, matching answer keys, mandatory shuffling passed.');

// Check the real generation functions with a mixed fixture, so the current
// all-choice bank cannot conceal a missing filter in a generation route.
const state = source.match(/const S = \{[\s\S]*?(?=function pool\()/)[0];
const pool = source.match(/function pool\(\)\{[\s\S]*?(?=\/\* ---------- tabs)/)[0];
const start = source.match(/function start\(ids\)\{[\s\S]*?(?=\/\* ---------- exam)/)[0];
const generation = vm.createContext({
  store: { get(key, fallback) { return key === 'cfg' ? { n: 10 } : fallback; } },
  QS: [{id:'choice', question_type:'multiple-choice'}, {id:'open', question_type:'open'}],
  rng() {}, shuffle: items => items.slice(), makeItems: items => items.map(q => ({q})),
  go() {}, startTimer() {}, Date, Math
});
vm.runInContext(state + pool + start, generation);
assert.equal(vm.runInContext('S.cfg.onlyMultipleChoice', generation), true);
assert.equal(vm.runInContext('pool().map(q=>q.id).join()', generation), 'choice');
for (const mode of ['digital', 'practice', 'print']) {
  vm.runInContext(`S.cfg.mode='${mode}'; start();`, generation);
  assert.equal(vm.runInContext(mode === 'print'
    ? 'S.print.versions.every(v=>v.length===1 && v[0].q.id==="choice")'
    : 'S.exam.items.length===1 && S.exam.items[0].q.id==="choice"', generation), true);
}
vm.runInContext('start(["choice","open"])', generation);
assert.equal(vm.runInContext('S.exam.items.map(x=>x.q.id).join()', generation), 'choice');
vm.runInContext('S.cfg.onlyMultipleChoice=false', generation);
assert.equal(vm.runInContext('pool().length', generation), 2);
console.log('Exam setup: default-on choice filter excludes open questions in digital, practice, print and retry generation.');
