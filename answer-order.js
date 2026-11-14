// Shared by quiz, bank, print layouts, and reading pages. Answers retain their
// source indices; only presentation order changes.
(function (root) {
  function indices(length, random = Math.random) {
    const order = Array.from({ length }, (_, i) => i);
    for (let i = length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [order[i], order[j]] = [order[j], order[i]];
    }
    return order;
  }
  const api = { indices };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AnswerOrder = api;
})(typeof window === 'undefined' ? globalThis : window);
