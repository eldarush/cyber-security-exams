const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const extract = (from, to) => source.slice(source.indexOf(from), source.indexOf(to, source.indexOf(from)));
const state = extract('const S = {', '/* ---------- tabs');
const generation = extract('function makeItems(', '/* ---------- exam');
const finish = extract('function finish(', '/* ---------- results');
const helpers = extract('function isCorrect(', '/* ---------- seeded random');
const random = extract('function rng(', '/* ---------- state');
const review = extract('function reviewItem(', '/* ---------- print');
const clear = extract('function clearHistory()', 'function bindHistoryMini(');
const historyBinding = extract('function bindHistoryMini(', '/* ---------- bank browser');
const initialize = extract("if ((S.cfg.collection || '')", 'tabFromHash();\nrender();');

function harness(set = '', initial = {}) {
  const storage = new Map(Object.entries(initial).map(([key, value]) => ['cyber-study-v2:' + key, JSON.stringify(value)]));
  const button = {};
  const context = vm.createContext({
    URLSearchParams, location: { search: set ? '?set=' + set : '' },
    localStorage: {getItem: k => storage.get(k) ?? null, setItem: (k,v) => storage.set(k,v)},
    document: { querySelector: () => button },
    AnswerOrder: require('../answer-order.js'), Date, Math, timerId: null,
    clearInterval() {}, startTimer() {}, go() {}, render() {},
    rich: text => text,
    confirmModal(message, label, callback) { context.confirmation = {message, label, callback}; }
  });
  vm.runInContext(extract('const BANK = ', '/* ---------- rich text') + helpers + random + state + generation + finish + review + clear + historyBinding + initialize, context);
  return {context, storage, button, run: expression => vm.runInContext(expression, context)};
}

for (const [set, count] of [['',182], ['latest',10], ['forecast-all',30], ['forecast-1',10], ['forecast-2',10], ['forecast-3',10]]) {
  const h = harness(set, { cfg: {collection: 'old-source', years:['2022'], topics:['old-topic'], skipNoted:true, wrongOnly:true, n:10} });
  assert.equal(h.run('QS.length'), count);
  assert.equal(h.run('pool().length'), count);
  assert.equal(h.run('S.cfg.onlyMultipleChoice'), true);
  h.run('start()');
  assert.equal(h.run('S.exam.items.length'), 10);
  assert.equal(h.run('S.exam.items.every(x => x.order.length===4 && new Set(x.order).size===4)'), true);
  if (set.startsWith('forecast')) {
    assert.equal(h.run('S.exam.items.every(x=>x.q.id.startsWith("P"))'), true);
    // The forecast disclaimer must not be mistaken for a cancelled exam question.
    h.run('S.cfg.skipNoted=true');
    assert.equal(h.run('pool().length'), count);
  }
}

const h = harness('forecast-all');
h.run('S.cfg.n=2; start(); S.exam.items[0].ans=S.exam.items[0].order.indexOf(0); S.exam.items[1].ans=S.exam.items[1].order.indexOf(1); finish(false);');
assert.equal(h.run('S.result.score'), 50);
assert.equal(h.run('S.result.exam.items.map(reviewItem).join("").match(/class="option-review"/g).length'), 8);
assert.equal(h.run('S.result.exam.items.map(reviewItem).join("").match(/<details class="answer-detail">/g).length'), 2);
const wrongId = h.run('S.exam.items[1].q.id');
h.run('S.cfg.wrongOnly=true');
assert.equal(h.run('pool().map(q=>q.id).join()'), wrongId);
// Save and reload: a forecast URL must not silently reset the wrong-only setting.
h.run("store.set('cfg', S.cfg)");
const reload = harness('forecast-all', {cfg: JSON.parse(h.storage.get('cyber-study-v2:cfg')), history: JSON.parse(h.storage.get('cyber-study-v2:history'))});
assert.equal(reload.run('S.cfg.wrongOnly'), true);
assert.equal(reload.run('pool().map(q=>q.id).join()'), wrongId);
reload.run('start(); S.exam.items[0].ans=S.exam.items[0].order.indexOf(0); finish(false);');
assert.equal(reload.run('S.result.score'), 100);
assert.equal(reload.run('pool().length'), 0);
// With no matching questions, start must not create an empty attempt.
assert.equal(reload.run('const completed=S.exam; start(); S.exam===completed'), true);

// Last result wins, collections remain separate, skipped practice is ignored.
const mixed = harness('forecast-all', {history: [
  {answers:[{id:'P01',ok:false},{id:'P02',ok:true},{id:'Q001',ok:false}]},
  {answers:[{id:'P01',ok:true},{id:'P02',ok:false}]}
]});
mixed.run('S.cfg.wrongOnly=true');
assert.equal(mixed.run('pool().map(q=>q.id).join()'), 'P02');
mixed.run('S.cfg.mode="practice"; start(); finish(false)');
assert.equal(mixed.run('pool().map(q=>q.id).join()'), 'P02');
mixed.run('S.cfg.wrongOnly=false; S.cfg.n=1; S.cfg.mode="digital"; S.cfg.seed="100"; start(); finish(false)');
assert.equal(mixed.run('wrongQuestionIds().has(S.exam.items[0].q.id)'), true);

// Exercise the real clear-button handler: opening/cancelling does not erase data.
mixed.run('bindHistoryMini(document)');
const before = mixed.storage.get('cyber-study-v2:history');
mixed.button.onclick();
assert.equal(mixed.storage.get('cyber-study-v2:history'), before);
assert.equal(mixed.context.confirmation.label, 'מחק');
mixed.run('S.cfg.wrongOnly=true');
mixed.context.confirmation.callback();
assert.equal(mixed.storage.get('cyber-study-v2:history'), '[]');
assert.equal(JSON.parse(mixed.storage.get('cyber-study-v2:cfg')).wrongOnly, false);
assert.equal(mixed.run('pool().length'), 30);
assert.equal(mixed.run('wrongQuestionIds().size'), 0);
console.log('Exam flow: six sources; forecast-only attempts; shuffled grading and explanations; wrong-only latest results; reload; clear-history confirmation and recovery passed.');
