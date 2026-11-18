// Exercise the focused mock plus four reviewed questions through the generated functions.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const ids = [...JSON.parse(read('data/forecast-best.json')).question_ids, 'P47', 'P52', 'P13', 'P57'];
const questions = JSON.parse(read('data/forecast.json')).filter(q => ids.includes(q.id)).concat(JSON.parse(read('data/forecast-set2.json')));
const source = read('index.html');
const slice = (from, to) => {
  const start = source.indexOf(from), end = source.indexOf(to, start);
  assert(start >= 0 && end > start, from);
  return source.slice(start, end);
};
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const decode = s => s.replace(/&#x27;|&quot;|&lt;|&gt;|&amp;/g, c => ({'&#x27;':"'",'&quot;':'"','&lt;':'<','&gt;':'>','&amp;':'&'}[c]));
const text = s => decode(s.replace(/<[^>]*>/g, ''));
function perms(values) {
  return values.length ? values.flatMap((v,i) => perms(values.filter((_,j)=>j!==i)).map(p=>[v,...p])) : [[]];
}
const orders = perms([0,1,2,3]);
const context = vm.createContext({LET:'אבגד', Date, esc, rich:esc, srcLabel:q=>q.id,
  clearInterval(){}, timerId:null, go(){}, store:{get:()=>[],set(){}}, S:{},
  PRINT_ENABLED:true, $:()=>({}), window:{print(){}},timerText:()=>({text:'0:00'})});
vm.runInContext(slice('function isCorrect(', '/* ---------- seeded random') +
  slice('function renderExam(', "document.addEventListener('keydown'") +
  slice('function finish(', '/* ---------- results') +
  slice('function reviewItem(', '/* ---------- history'), context);
assert.equal(questions.length, 74);
let graded = 0, rendered = 0, practiceRendered = 0, printed = 0, readingOrders = 0;
for (const q of questions) {
  assert.deepEqual(q.accepted_indices, [0], q.id);
  assert.equal(new Set(q.options).size, 4);
  assert.deepEqual(q.option_explanations.map(x=>x.option), q.options);
  assert.deepEqual(q.option_explanations.map(x=>x.correct), [true,false,false,false]);
  // Each explanation names its actual option, never a fixed display letter.
  assert(!/(?:חלופה|תשובה)\s+[אבגד]['׳.]/u.test(text(q.answer_html)), q.id);
  const explanations = [...q.answer_html.matchAll(/<div class="option-review" data-option-review="(\d)"><h4>(.*?)<\/h4><p>(.*?)<\/p><\/div>/gs)];
  assert.equal(explanations.length, 4);
  for (const [i, explanation] of explanations.entries()) {
    assert.equal(Number(explanation[1]), i);
    assert.equal(text(explanation[2]), (i===0?'נכונה':'שגויה')+' — '+q.options[i]);
    assert.equal(text(explanation[3]), q.option_explanations[i].reason);
  }
  for (const order of orders) {
    for (let selected=0; selected<4; selected++) {
      const correctPosition = order.indexOf(0);
      context.item = {q, order, ans:selected};
      context.S.exam = {mode:'digital', start:Date.now(), items:[context.item]};
      vm.runInContext('finish(false)', context);
      assert.equal(context.S.result.score, selected===correctPosition?100:0, q.id);
      assert.equal(vm.runInContext('correctLetters(item)',context), 'אבגד'[correctPosition]);
      const html = vm.runInContext('reviewItem(item,0)', context);
      assert.equal((html.match(/class="opt ok"/g)||[]).length, 1);
      const displayedCorrect = html.match(/<div class="opt ok"><span class="bub">(.*?)<\/span><span class="t">(.*?)<\/span>/s);
      assert.equal(displayedCorrect[1], 'אבגד'[correctPosition]);
      assert.equal(text(displayedCorrect[2]), q.options[0]);
      assert.equal((html.match(/class="opt bad"/g)||[]).length, selected===correctPosition?0:1);
      assert(html.includes(q.answer_html), q.id+' changed explanation after shuffle');
      assert.equal((html.match(/data-option-review=/g)||[]).length, 4);
      context.S.exam = {mode:'practice',items:[context.item],cur:0,seed:123};
      context.app = {querySelectorAll:()=>[]};
      vm.runInContext('renderExam(app)',context);
      const practice = context.app.innerHTML;
      const practiceCorrect = practice.match(/<button class="opt ok"[^>]*><span class="bub">(.*?)<\/span><span class="t">(.*?)<\/span>/s);
      assert.equal(practiceCorrect[1],'אבגד'[correctPosition]);
      assert.equal(text(practiceCorrect[2]),q.options[0]);
      assert.equal((practice.match(/class="opt ok"/g)||[]).length,1);
      assert(practice.includes(q.answer_html));
      assert(practice.includes(selected===correctPosition?'✓ נכון.':'התשובה הנכונה: '+'אבגד'[correctPosition]+'.'));
      practiceRendered++;
      graded++;
      rendered++;
    }
    context.S.print = {seed:123,versions:[[{q,order,ans:null}]]};
    context.app = {};
    vm.runInContext('renderPrint(app)',context);
    const key = context.app.innerHTML.match(/<td><b>(.*?)<\/b> <span[^>]*>(P\d+|B2-\d+)<\/span><\/td>/);
    assert.equal(key[1], 'אבגד'[order.indexOf(0)]);
    assert.equal(key[2], q.id);
    printed++;
  }
  // Run study.js's real reading-page shuffle over both generated surfaces.
  for (const file of [q.parent_id ? 'predictions-2.html' : 'predictions.html','solutions/'+q.id+'.html']) {
    const html = read(file);
    assert(html.includes(q.answer_html), file+' explanation differs from canonical record');
    const listMatch = html.match(new RegExp('<ol [^>]*id="opts-'+q.id+'"[^>]*>(.*?)</ol>','s'));
    assert(listMatch, file);
    const records = [...listMatch[1].matchAll(/<li data-option-index="(\d)"><b class="option-letter">(.*?)<\/b><span class="option-text">(.*?)<\/span><\/li>/gs)];
    assert.equal(records.length,4);
    const study = read('study.js');
    const shuffleReading = study.slice(study.indexOf('  const letters ='),study.indexOf('  const cards ='));
    for (const order of orders) {
      const items = records.map(r=>{
        const letter = {textContent:text(r[2])}, option = {textContent:text(r[3])};
        assert.equal(option.textContent,q.options[Number(r[1])]);
        return {dataset:{optionIndex:r[1]},querySelector:s=>s==='.option-letter'?letter:option};
      });
      const list = {id:'opts-'+q.id,dataset:{accepted:'[0]'},children:[...items],append(item){this.children=this.children.filter(x=>x!==item);this.children.push(item);}};
      const key = {dataset:{answerFor:list.id},textContent:''};
      vm.runInNewContext(shuffleReading, {AnswerOrder:{indices:()=>order},document:{querySelectorAll:s=>s==='.study-options'?[list]:[key]}});
      const correctPosition = list.children.findIndex(item=>item.dataset.optionIndex==='0');
      assert.equal(key.textContent,'התשובה הנכונה כאן: '+'אבגד'[correctPosition]+'. '+q.options[0]);
      list.children.forEach((item,i)=>assert.equal(item.querySelector('.option-letter').textContent,'אבגד'[i]+'. '));
      readingOrders++;
    }
  }
}
assert.equal(graded,7104);
assert.equal(printed,1776);
assert.equal(readingOrders,3552);
assert.equal(practiceRendered,7104);
console.log(`Focused mock, four reviewed questions and Set 2: ${graded} actual-answer grading cases, ${rendered} result and ${practiceRendered} practice explanation renders, ${printed} print keys, ${readingOrders} reading-page shuffles passed (all 24 orders for 74 questions).`);

// The syllabus supplement is intentionally outside the 60-question forecast,
// but its displayed answer key must follow the same real page shuffle.
const supplemental = read('syllabus-coverage.html');
const supplementalList = supplemental.match(/<ol [^>]*id="opts-S01"[^>]*>(.*?)<\/ol>/s);
assert(supplementalList);
const supplementalRecords = [...supplementalList[1].matchAll(/<li data-option-index="(\d)"><b class="option-letter">(.*?)<\/b><span class="option-text">(.*?)<\/span><\/li>/gs)];
assert.equal(supplementalRecords.length,4);
assert.equal((supplemental.match(/class="option-review"/g)||[]).length,4);
const supplementalCorrect=text(supplementalRecords.find(r=>r[1]==='0')[3]);
for (const order of orders) {
  const items=supplementalRecords.map(r=>{
    const letter={textContent:text(r[2])},option={textContent:text(r[3])};
    return {dataset:{optionIndex:r[1]},querySelector:s=>s==='.option-letter'?letter:option};
  });
  const list={id:'opts-S01',dataset:{accepted:'[0]'},children:[...items],append(item){this.children=this.children.filter(x=>x!==item);this.children.push(item);}};
  const key={dataset:{answerFor:list.id},textContent:''};
  const study=read('study.js');
  vm.runInNewContext(study.slice(study.indexOf('  const letters ='),study.indexOf('  const cards =')),
    {AnswerOrder:{indices:()=>order},document:{querySelectorAll:s=>s==='.study-options'?[list]:[key]}});
  const position=list.children.findIndex(item=>item.dataset.optionIndex==='0');
  assert.equal(key.textContent,'התשובה הנכונה כאן: '+'אבגד'[position]+'. '+supplementalCorrect);
}
console.log('Syllabus supplement: all 24 displayed answer orders have the matching answer key and four option explanations.');
