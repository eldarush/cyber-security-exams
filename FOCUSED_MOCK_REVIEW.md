# Focused mock: content and shuffled-answer audit

Reviewed 14 November 2026. Scope: the ten canonical questions in `data/forecast-best.json`, all 40 answer options, their derivations, distractor explanations, assumptions, and generated views. This audit checks answers; it does not validate prediction accuracy.

| Question | Single correct answer, identified by content | Review and distractor findings |
| --- | --- | --- |
| P02 | I₂'s public key | The direct issuer's signature is verified with its public key. Clarified that each entity has a distinct key pair and that the question asks about the issuer signature, rather than complete trust validation. The root, I₁'s private key, and the site's public key are not the requested key. |
| P11 | CT alone need not reject the misissued certificate; logging may enable detection | Clarified that the CA signature is mathematically valid but issuance is unauthorized. SCTs do not prove domain authorization, automatically revoke certificates, or require the site's private key. An SCT promises inclusion; it is not itself an inclusion proof. |
| P08 | Risk decreases with confirmation depth but does not become zero after a finite number | Corrected “risk is small” to a relative decrease. A positive attacker share below 50%, ordinary probabilistic mining, and no receiver isolation are explicit assumptions. Near 50%, risk can remain substantial. Six confirmations are not six miner signatures, mathematical finality, or access to private keys. |
| P04 | C XOR M XOR M′ | XOR cancellation proves the expression for all equal-length, distinct messages and every key. C XOR M′ fails generally, even though it works in the special case M=0; the stem explicitly asks for a guarantee for every pair. C XOR K XOR K leaves the original unchanged. One-time use provides no authentication. |
| P17 | A cross-site request may execute even when its response cannot be read | The ordinary form POST and the ability to send the authentication cookie are explicit. SOP does not block all such submissions; POST is not encryption; SOP is not a SQL-server mechanism. The option with the right “no” but a false SQL rationale remains false as a whole. |
| P01 | 32 | All candidates independently evaluated: 32⁵ mod 35=2; 2⁵ mod 35=32; 3⁵ mod 35=33; 5⁵ mod 35=10. Only 32 meets m=2. Here e=d=5 is valid because 25≡1 mod 24; this is not a general rule. Textbook RSA is explicitly a teaching model. |
| P15 | Second preimage resistance | Clarified that m₀ is supplied and cannot be chosen or changed, and that the question asks for the exact security experiment. A successful output also forms a collision; the explanation explicitly acknowledges that, rather than claiming second-preimage attacks cannot find collisions. The unrestricted two-message collision experiment, digest-only preimage experiment and OTP secrecy do not match this experiment. |
| P10 | RIJVS | HELLO + KEYKE modulo 26 gives 17,8,9,21,18. IFMMP is a fixed shift of one; RIJWT has two incorrect final characters; HELLO leaves the plaintext unchanged. Inverse subtraction recovers HELLO. |
| P20 | On-path network position without automatic TLS decryption | ARP forwarding can enable observation, dropping, delaying and packet changes. It neither supplies TLS secrets nor requires changing DNS. Correctly authenticated TLS protects application content, while availability and traffic metadata remain separate issues. |
| P09 | 2 | Independently computed A=5⁶ mod 23=8, B=5¹⁵ mod 23=19, and both B⁶ mod 23=A¹⁵ mod 23=2. The alternatives 8 and 19 are public values; 21 is a+b. Clarified that the question asks for the raw shared secret before KDF processing. |

## Primary references checked

- [RFC 5280, path validation](https://www.rfc-editor.org/rfc/rfc5280.html#section-6.1) — issuer public keys and separate path checks.
- [RFC 6962, log operation](https://www.rfc-editor.org/rfc/rfc6962.html#section-3) — SCT promise, log signature and public auditing.
- [Bitcoin whitepaper, section 11](https://bitcoin.org/bitcoin.pdf) — risk decreases with deficit when honest work exceeds attacker work; not a universal six-confirmation guarantee.
- [RFC 8017, RSAVP1](https://www.rfc-editor.org/rfc/rfc8017.html#section-5.2.2) — the RSA verification primitive.
- [NIST, second preimage](https://csrc.nist.gov/glossary/term/second_preimage) — fixed-message second-preimage definition.
- [OWASP, CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#disallowing-simple-requests) — ordinary cross-origin forms and separate CSRF protection.
- [RFC 8446, security properties](https://www.rfc-editor.org/rfc/rfc8446.html#appendix-E.1) — session-key secrecy and peer authentication.

## Exhaustive presentation checks

`scripts/test-focused-mock-order.cjs` executes the generated site's real functions against these ten actual records:

- All 24 permutations × 10 questions × all 4 selected choices = 960 grading cases.
- 960 result views and 960 immediate-feedback practice views: one correct marker, matching displayed letter/text, and all four unchanged, text-identified explanations.
- 240 print answer keys match the presented order.
- 480 reading-page shuffles cover both the forecast cards and standalone solutions, starting from each page's actual fallback order.
- Each explanation is bound to the full canonical option text and correct/incorrect flag. No explanation identifies an answer by a fixed Hebrew option letter.

Explanations intentionally identify options by text and may retain their explanatory order; they do not assume that the first displayed choice is correct. Canonical indices and question IDs are unchanged, preserving previous attempt history. The user-facing answer letters are derived from each attempt's permutation. Content reasoning and stated assumptions were reviewed separately: passing structural or rendering tests alone would not prove semantic correctness.
