# Report: AmazonHelp AI Support Agent

## Problem Framing

**What "good" means for this brand:** given a customer's tweet, the system must
(1) correctly identify the underlying issue type from a taxonomy grounded in
real AmazonHelp traffic,
(2) draft a reply that reflects how Amazon has
actually resolved similar issues historically — not a generic, brand-agnostic
apology — and
(3) make a conservative, defensible auto/escalate call: auto
means the reply can fully resolve the issue or make safe, correct progress
without needing sensitive data or judgment; anything else escalates. This
last definition was decided explicitly rather than left implicit — early
review showed that most of Amazon's own historical replies are themselves
"please contact us" redirects, meaning a looser standard would have auto-
approved cases Amazon itself treats as needing a human.

**What I chose not to build:**
- Multi-language support (scoped to English, ~75% of traffic, see decision log)
- A fine-tuned classifier (few-shot prompting was sufficient and faster to iterate on for a one-week project)
- A vector database for retrieval (TF-IDF cosine similarity over ~61k historical pairs was sufficient at this scale)
- A UI/frontend (out of scope — this is a backend/evaluation exercise)
- Full multi-turn conversation handling for classification (classified on the opening customer message only, matching the assignment's framing of "classify each incoming message"; full thread history is used for retrieval/grounding instead)

## Results vs. Baselines

Evaluated on a 142-row held-out set (160 hand-labeled golden examples minus 18
used as few-shot examples, 2 per intent).

| Method | Accuracy |
|---|---|
| Trivial baseline (most frequent class) | 9.2% |
| Simple baseline (TF-IDF + Logistic Regression) | 23.2% |
| LLM classifier (Ollama, `llama3.2`, few-shot) | **49.3%** |

The LLM classifier more than doubles the simple baseline and is over 5x the
trivial baseline. Per-intent performance varies substantially — strongest on
`account_security` (0.83 precision) and `informational` (1.00 precision, but
only 0.40 recall), weakest on `delivery_delay` (0.24 F1), which is analyzed
in the Failure Analysis section below.

## Failure Analysis

Based on manual review of misclassified examples in `eval/classification_results.csv`.

### 1. Off-topic over-triggering
Genuine support messages were frequently misclassified as `off_topic` (16 of
142 held-out rows) — e.g. "@217158 BAOT delivery delayed. Will you call the
CEO of Amazon..." (true: `delivery_delay`) and "Stop Fake Orders Stop Used
Returns #HearUsAmazon" (true: `general_complaint`) were both called
`off_topic`. Precision on this category was only 0.24 despite perfect recall.
**Hypothesis:** the classifier's raw output sometimes fails to match a valid
label string cleanly, and the fallback logic in `classify.py`
(`return "off_topic"` on unparseable output) silently absorbs genuine parsing
failures as if they were real classification decisions. This is likely a
prompt-compliance issue with the local model rather than true semantic
confusion, and is a cheap, high-value fix candidate.

### 2. `delivery_delay` misread as `general_complaint` when tone is intense
Messages like "Every time I pay for 1 day shipping... Get your crap
together!" and "What is the point in preordering......." (both true:
`delivery_delay`) were classified as `general_complaint`. **Hypothesis:** the
classifier appears to weight emotional intensity/profanity over the
underlying factual category — treating "this person is very upset" as
sufficient evidence for `general_complaint`, even when the message clearly
names a concrete, categorizable problem (a delayed order).

### 3. `delivery_delay` vs. `delivery_not_received` boundary confusion
Confusion ran in both directions between these two categories (e.g., "package
arrived containing one item but not the other" true-labeled
`delivery_not_received`, predicted `delivery_delay`). **Hypothesis:** these
two categories are semantically adjacent by design — both concern "the
package isn't in the customer's hands" — and the distinction (still in
transit vs. should have arrived/is lost) is genuinely subtle in ambiguous
cases even for a human labeler, as noted during manual labeling.

### 4. `account_security` under-recognition (low frequency, high severity)
Several genuine security-relevant messages were missed: an unauthorized
address change ("I DID NOT REQUEST AN ADDRESS FORWARDING"), a phishing report,
an unfamiliar delivery a family member didn't order, and a locked account
with repeated "canned" responses were all classified into other categories
(recall on `account_security` was only 0.38). **This is the most operationally
risky failure type** despite being lower-frequency: a missed security case
means a potentially serious issue gets auto-handled or under-escalated
instead of receiving mandatory human review.

### 5. `informational` under-recognition (conservative bias)
Praise, pricing questions, and policy questions were frequently classified
into other categories rather than `informational` (recall only 0.40, despite
1.00 precision — the model is never wrong when it does guess this category,
but guesses it too rarely). **Hypothesis:** the classifier may be biased
toward assuming any message directed at a support account implies a problem
to resolve, under-weighting the possibility that a message is a pure
question or compliment with nothing to fix.

## What's Misleading About My Headline Number

The 49.3% classifier accuracy and the drafted-reply quality look like clean,
positive results — but several factors mean they should not be taken at
face value.

**1. The LLM-judge is not reliably measuring what it claims to measure.**
Manual validation against 30 hand-scored examples showed the judge agrees
well with a human on tone (73% exact match, 97% within one point) but poorly
on relevance (23% exact match) and groundedness (33% exact match) — the two
dimensions that matter most for "grounded in historical resolution." Any
reported average groundedness/relevance score from this judge should be
treated as noisy, not authoritative, until the rubric is recalibrated (e.g.,
with few-shot scoring examples or clearer per-level anchors).

**2. The golden set's escalate rate (44%, 70/160) likely overstates the true
rate across all AmazonHelp support traffic.** People who tweet at a brand's
support account skew toward already-frustrated, already-escalated situations
— someone whose delivery arrived on time rarely tweets about it. The full
population of AmazonHelp support contacts (most of which never becomes a
public tweet at all) probably contains a higher share of simple, mundane
requests than this sample suggests. An escalation-accuracy number computed on
this golden set may not generalize to the brand's real traffic mix.

**3. The taxonomy was derived from the same dataset it is evaluated on.**
Both the 8 intent categories and the golden set come from the same underlying
AmazonHelp Twitter corpus (different random samples, but the same population
and time period). A category system built to fit this specific data may not
generalize as cleanly to future traffic, seasonal shifts, or other channels
(email, chat) not represented here.

**4. English-only scope excludes ~25% of real traffic**, and the excluded
languages are not evenly distributed in complaint type — no direct evidence
either way, but it's untested whether the taxonomy or escalation rules would
even apply sensibly to, say, Japanese-language threads without translation.

**5. The classifier was tested with a local, ~3B-parameter model
(`llama3.2`) using only 2 few-shot examples per intent.** A frontier API
model, or more few-shot examples, would very likely score meaningfully
higher — this number reflects a specific low-cost configuration, not the
ceiling of what an LLM-based classifier could achieve on this task.

**6. The escalation policy's repeat-contact and distrust-tone rules are
keyword-based**, not true language understanding. Paraphrased versions of
these signals ("I've asked about this before" vs. "again") would be missed,
and the false-positive/false-negative rate of this keyword approach was not
separately measured against the golden set's `auto_or_escalate` labels in
this build — a gap worth closing before trusting this in production.

**7. Off-topic over-triggering (Failure Analysis #1) may be inflating or
deflating other categories' apparent performance.** If the fallback logic is
absorbing genuine parsing failures as `off_topic` rather than true model
confusion, the per-intent recall numbers for whichever categories those
messages actually belonged to are artificially lowered — the true classifier
capability on those categories may be somewhat better than reported.

## What I'd Do Next With One More Week

**Fix the off-topic over-triggering bug first** — cheapest, highest-leverage
fix identified. Add logging of raw (unparsed) LLM output before the fallback
kicks in, to confirm whether this is a parsing failure or genuine semantic
confusion, then either tighten the prompt or add a retry-with-clarification
step before defaulting to `off_topic`.

**Recalibrate the LLM-judge for relevance and groundedness.** Given the weak
human-agreement scores on these two dimensions, I'd add few-shot scoring
examples to the judge's prompt (showing what a 2 vs. a 4 looks like
concretely) and re-run the human-agreement check to see if it improves
before trusting the judge's output as a standalone metric.

**Test with a frontier API model (e.g., Claude) alongside the local model**,
using the same golden set and few-shot examples, to get a real comparison
point — both for classification accuracy and for reply quality — and report
the delta honestly rather than assuming it.

**Move the escalation policy from keyword matching to LLM-based tone/signal
detection.** Ask the model directly "does this message show signs of repeat
contact, distrust, or severity requiring human review?" rather than string
matching, and validate this against the golden set's `auto_or_escalate`
labels specifically (not yet measured as its own metric in this build).

**Expand the golden set with a second, independently-sampled batch** from a
different time period than the original data, to test whether the taxonomy
and classifier generalize beyond the specific slice of traffic they were
built and tuned on — directly addressing the taxonomy-circularity concern
raised above.

**Add a lightweight severity/tone score as a second signal alongside intent**,
since Failure Analysis and manual labeling both showed that intent category
alone is insufficient for escalation decisions — a "general_complaint" ranges
from mild disappointment to threats of legal action, and treating these
identically is a real gap.

**Investigate the multi-language subset** (~25% of traffic) at least
directionally — even a rough machine-translation-then-classify pass would
tell us whether the existing taxonomy transfers reasonably or needs
region-specific categories.

**Cache the retrieval index** (currently rebuilt from ~61k pairs on every run)
to disk, and consider embeddings instead of TF-IDF for retrieval quality —
not done in this build given the one-week time budget, since TF-IDF was
sufficient to demonstrate the grounding mechanism works.