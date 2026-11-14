(() => {
  const letters = ['א', 'ב', 'ג', 'ד'];
  document.querySelectorAll('.study-options').forEach(list => {
    const items = [...list.children];
    const order = AnswerOrder.indices(items.length);
    order.forEach(i => list.append(items[i]));
    [...list.children].forEach((item, i) => {
      item.querySelector('.option-letter').textContent = letters[i] + '. ';
    });
    const accepted = JSON.parse(list.dataset.accepted);
    const correct = [...list.children].flatMap((item, i) =>
      accepted.includes(Number(item.dataset.optionIndex))
        ? [letters[i] + '. ' + item.querySelector('.option-text').textContent] : []);
    document.querySelectorAll('[data-answer-for]').forEach(key => {
      if (key.dataset.answerFor === list.id) {
        key.textContent = (accepted.length > 1 ? 'חלופות שהתקבלו בבדיקה: ' : 'התשובה הנכונה כאן: ') + correct.join(' / ');
      }
    });
  });
  const cards = [...document.querySelectorAll('.forecast-card')];
  const key = 'cyber-study-v2:mastered';
  let mastered = {};
  try { mastered = JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch { mastered = {}; }
  const search = document.querySelector('#forecast-search');
  const priority = document.querySelector('#forecast-priority');
  const pending = document.querySelector('#forecast-pending');
  function filter() {
    const term = (search?.value || '').trim().toLowerCase();
    let count = 0;
    for (const card of cards) {
      const show = (!term || card.textContent.toLowerCase().includes(term)) && (!priority.value || card.dataset.priority === priority.value) && (!pending.checked || !mastered[card.id]);
      card.hidden = !show;
      if (show) count++;
    }
    if (cards.length) {
      document.querySelector('#forecast-count').textContent = `${count} מתוך ${cards.length}`;
      document.querySelector('#forecast-empty').hidden = count !== 0;
    }
  }
  document.querySelectorAll('[data-mastered]').forEach(input => {
    input.checked = !!mastered[input.dataset.mastered];
    input.addEventListener('change', () => {
      mastered[input.dataset.mastered] = input.checked;
      try { localStorage.setItem(key, JSON.stringify(mastered)); } catch { /* Reading and practice remain usable without storage. */ }
      filter();
    });
  });
  [search, priority, pending].forEach(el => el?.addEventListener('input', filter));
  filter();
  let opened = [];
  addEventListener('beforeprint', () => {
    opened = [...document.querySelectorAll('details:not([open])')];
    opened.forEach(el => { el.open = true; });
  });
  addEventListener('afterprint', () => opened.forEach(el => { el.open = false; }));
  document.querySelector('#print-study')?.addEventListener('click', () => print());
})();
