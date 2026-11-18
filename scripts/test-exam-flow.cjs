const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const extract = (from, to) => source.slice(source.indexOf(from), source.indexOf(to, source.indexOf(from)));
const state = extract('const S = {', '/* ---------- tabs');
const generation = extract('function set2History(', '/* ---------- exam');
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

for (const [set, count] of [['',182], ['latest',10], ['forecast-all',60], ['forecast-focus',20], ['forecast-best',10], ['forecast-set2',60], ['forecast-lecture',10], ['forecast-no-latest',6], ['forecast-1',10], ['forecast-2',10], ['forecast-3',10], ['forecast-4',10], ['forecast-5',10], ['forecast-6',10]]) {
  const h = harness(set, { cfg: {collection: 'old-source', years:['2022'], topics:['old-topic'], skipNoted:true, wrongOnly:true, n:10} });
  assert.equal(h.run('QS.length'), count);
  assert.equal(h.run('pool().length'), count);
  assert.equal(h.run('S.cfg.onlyMultipleChoice'), true);
  h.run('start()');
  assert.equal(h.run('S.exam.items.length'), Math.min(count, 10));
  assert.equal(h.run('S.exam.items.every(x => x.order.length===4 && new Set(x.order).size===4)'), true);
  if (set.startsWith('forecast')) {
    assert.equal(h.run('S.exam.items.every(x=>x.q.id.startsWith("P") || x.q.id.startsWith("B2-"))'), true);
    // The forecast disclaimer must not be mistaken for a cancelled exam question.
    h.run('S.cfg.skipNoted=true');
    assert.equal(h.run('pool().length'), count);
    if (set === 'forecast-focus') {
      assert.equal(h.run('QS.map(q=>q.id).join() === [...FORECAST].sort((a,b)=>b.confidence-a.confidence || a.id.localeCompare(b.id)).slice(0,20).map(q=>q.id).join()'), true);
    } else if (set === 'forecast-best') {
      assert.equal(h.run('QS.map(q=>q.id).join() === BEST_MOCK.question_ids.join()'), true);
    } else if (set === 'forecast-lecture') {
      assert.equal(h.run('QS.map(q=>q.id).sort().join()'), 'P06,P09,P10,P26,P29,P30,P38,P39,P45,P55');
      assert.equal(h.run('QS.every(q=>q.lecture_evidence)'), true);
    } else if (set === 'forecast-no-latest') {
      const expected = JSON.parse(fs.readFileSync(path.join(root, 'data/mock-sensitivity.json'), 'utf8')).weight_tests.find(x => x.omitted_component==='latest_a').added;
      assert.equal(h.run('QS.map(q=>q.id).join()'), expected.join());
      assert.equal(h.run('QS.every(q=>!BEST_MOCK.question_ids.includes(q.id))'), true);
    } else if (/forecast-[1-6]$/.test(set)) {
      assert.equal(h.run(`QS.every(q=>q.mock===${Number(set.slice(-1))})`), true);
    }
  }
}

// Sensitivity alternatives reset the source configuration and grade by shuffled index.
const alternative = harness('forecast-no-latest', {cfg:{collection:'forecast-best',mode:'practice',n:2,wrongOnly:true,minutes:5}});
alternative.run('start()');
assert.equal(alternative.run('S.exam.mode'), 'digital');
assert.equal(alternative.run('S.exam.limit'), 48*60);
alternative.run('S.exam.items.forEach((x,i)=>x.ans=x.order.indexOf(i===0?1:0)); finish(false)');
assert.equal(alternative.run('S.result.score'), 83);
assert.equal(alternative.run('S.result.exam.items.map(reviewItem).join("").match(/class="option-review"/g).length'), 24);

// A saved short practice configuration must not turn the fixed mock into two questions.
const best = harness('forecast-best', {cfg:{collection:'forecast-all',mode:'practice',n:2,topics:['old'],years:['2022'],wrongOnly:true,minutes:5}});
best.run('start()');
assert.equal(best.run('S.exam.mode'), 'digital');
assert.equal(best.run('S.exam.limit'), 80*60);
assert.equal(best.run('S.exam.items.map(x=>x.q.id).sort().join()'), 'P01,P02,P04,P05,P06,P08,P09,P10,P11,P20');
best.run('S.exam.items.forEach((x,i)=>x.ans=x.order.indexOf(i===0?1:0)); finish(false)');
assert.equal(best.run('S.result.score'), 90);
assert.equal(best.run('S.result.exam.items.map(reviewItem).join("").match(/class="option-review"/g).length'), 40);
const bestWrong = best.run('S.exam.items[0].q.id');
best.run('S.cfg.wrongOnly=true');
assert.equal(best.run('pool().map(q=>q.id).join()'), bestWrong);
best.run('start(); S.exam.items[0].ans=S.exam.items[0].order.indexOf(0); finish(false)');
assert.equal(best.run('pool().length'), 0);

// Switching to the lecture-backed set starts all ten in a timed, shuffled exam.
const lecture = harness('forecast-lecture', {cfg:{collection:'forecast-all',mode:'practice',n:2,topics:['old'],wrongOnly:true,minutes:5}});
lecture.run('start()');
assert.equal(lecture.run('S.exam.mode'), 'digital');
assert.equal(lecture.run('S.exam.limit'), 80*60);
assert.equal(lecture.run('S.exam.items.length'), 10);
lecture.run('S.exam.items.forEach((x,i)=>x.ans=x.order.indexOf(i===0?1:0)); finish(false)');
assert.equal(lecture.run('S.result.score'), 90);
assert.equal(lecture.run('S.result.exam.items.map(reviewItem).join("").match(/class="option-review"/g).length'), 40);
assert.equal(lecture.run('S.result.exam.items.map(reviewItem).join("").match(/<details class="answer-detail">/g).length'), 10);

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

// Attempts for the former P09 must not become attempts for the revised question.
const revisions = harness('forecast-all', {history:[{t:1,answers:[{id:'P09',ok:false},{id:'P47',ok:false},{id:'P52',ok:false},{id:'P01',ok:false}]}]});
revisions.run('S.cfg.wrongOnly=true');
assert.equal(revisions.run('pool().map(q=>q.id).join()'), 'P01');
const preserved = revisions.storage.get('cyber-study-v2:history');
revisions.run('S.cfg.wrongOnly=false; start(["P09"]); S.exam.items[0].ans=S.exam.items[0].order.indexOf(1); finish(false)');
assert.equal(JSON.parse(revisions.storage.get('cyber-study-v2:history'))[1].answers[0].revision, 2);
assert.equal(JSON.parse(revisions.storage.get('cyber-study-v2:history'))[0].answers[0].ok, JSON.parse(preserved)[0].answers[0].ok);
revisions.run('S.cfg.wrongOnly=true');
assert.equal(revisions.run('pool().map(q=>q.id).join()'), 'P01,P09');
revisions.run('start(["P09"]); S.exam.items[0].ans=S.exam.items[0].order.indexOf(0); finish(false)');
assert.equal(revisions.run('pool().map(q=>q.id).join()'), 'P01');
revisions.run('S.cfg.wrongOnly=false; start(["P52"]); S.exam.items[0].ans=S.exam.items[0].order.indexOf(1); finish(false); S.cfg.wrongOnly=true');
assert.equal(revisions.run('pool().map(q=>q.id).join()'), 'P01,P52');
assert.equal(JSON.parse(revisions.storage.get('cyber-study-v2:history')).at(-1).answers[0].revision, 2);
revisions.run('S.cfg.wrongOnly=false; start(["P47"]); S.exam.items[0].ans=S.exam.items[0].order.indexOf(1); finish(false); S.cfg.wrongOnly=true');
assert.equal(revisions.run('pool().map(q=>q.id).join()'), 'P01,P47,P52');
assert.equal(JSON.parse(revisions.storage.get('cyber-study-v2:history')).at(-1).answers[0].revision, 2);

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
assert.equal(mixed.run('pool().length'), 60);
assert.equal(mixed.run('wrongQuestionIds().size'), 0);
console.log('Exam flow: fourteen sources; lecture-backed set; full balanced mock; shuffled grading and explanations; wrong-only latest results; reload; clear-history confirmation and recovery passed.');

// Fixed seed lets us compare the effect of local history on the exact same pool.
const set2Cfg = {collection:'forecast-set2', mode:'digital', n:10, seed:'251932'};
const localSet2 = harness('forecast-set2', {cfg:set2Cfg});
localSet2.run('start()');
assert.equal(localSet2.run('new Set(S.exam.items.map(x=>x.q.skill)).size'), 10);
assert.equal(localSet2.run('new Set(S.exam.items.map(x=>x.q.topic)).size'), 6);
const baselineSkills = localSet2.run('S.exam.items.map(x=>x.q.skill).sort().join()');
function mockWithHistory(answers, enabled=true) {
  const h = harness('forecast-set2', {cfg:{...set2Cfg, prioritizeSet2Errors:enabled}, history:[{answers}]});
  h.run('start()');
  return h;
}
const skills = localSet2.run('FORECAST_SET2.map(q=>q.skill).join()');
assert(skills.includes('password'));
const history = ['P24','Q014','Q085','Q103','Q136'].map(id=>({id, ok:false}));
const personal = mockWithHistory(history);
assert.equal(personal.run('set2History().size'), history.length);
assert.notEqual(personal.run('S.exam.items.map(x=>x.q.skill).sort().join()'), baselineSkills);
assert.equal(personal.run('S.exam.items.some(x=>x.q.skill==="password")'), true);
assert.equal(mockWithHistory(history,false).run('S.exam.items.map(x=>x.q.skill).sort().join()'), baselineSkills);
assert.equal(mockWithHistory(history.concat(history.map(a=>({...a,ok:true})))).run('S.exam.items.map(x=>x.q.skill).sort().join()'), baselineSkills);
assert.equal(mockWithHistory([{id:'P52',ok:false},{id:'unknown',ok:false}]).run('set2History().size'), 0);
personal.run('S.cfg.n=60; start(); S.exam.items.forEach(x=>x.ans=x.order.indexOf(0)); finish(false)');
assert.equal(personal.run('S.result.total'), 60);
assert.equal(personal.run('S.result.score'), 100);
console.log('Set 2: balanced digital exam, local mistake priority, latest-answer recovery, stale history exclusion and full 60-question grade passed.');
