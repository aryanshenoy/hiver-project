# Decision Log

Plain list of non-obvious decisions made while building this project, and why.

1. **Chose AmazonHelp as the brand** — highest tweet volume in the dataset (~170k
   replies), giving enough data per intent for a real taxonomy and golden set.
   Diverse but bounded issue types (delivery, refunds, item quality, account
   access) suit a small taxonomy well.

2. **Restricted scope to English-only threads** — measured first, then decided:
   74.8% of AmazonHelp threads are English (via `langdetect` on the customer's
   opening message); the largest other language (Japanese) is only 8%, with no
   single language large enough to justify multi-language support in a
   one-week project.

3. **Reconstructed threads structurally, not by text-mention matching** — walked
   `in_response_to_tweet_id`/`response_tweet_id` chains from true conversation
   roots (`in_response_to_tweet_id` is NaN) forward, rather than filtering by
   `@AmazonHelp` text mentions, since text-mention matching misses mid-thread
   replies that don't re-tag the handle.

4. **8-intent taxonomy derived from manually reading real data**, not assumed
   upfront and not borrowed from Banking77 (wrong domain — banking intents
   don't transfer to e-commerce support). Read ~150 randomly sampled English
   threads (seed=42).

5. **`off_topic` treated as an exclusion category, not a real intent** — some
   fraction of any real Twitter dataset is noise (unrelated mentions, spam,
   ambiguous fragments); classifying it explicitly is more honest than
   silently dropping it, but it's excluded from auto/escalate evaluation since
   that decision doesn't apply to non-support messages.

6. **Golden set sampled independently from the taxonomy-derivation sample**
   (seed=7 vs. seed=42) — avoids evaluating the system against the same
   examples used to define its own categories, which would inflate results.

7. **Golden set size: 160, not the full 150-250 range** — stopped once pattern
   variety across labeling batches showed clear saturation (no new taxonomy
   edge cases in the final few batches), and 160 comfortably clears the
   assignment's stated floor.

8. **Adopted a strict definition of "auto-handle"**: a reply must either fully
   resolve the issue with information already in the message, or make correct,
   safe progress by asking for the specific next piece of info Amazon's own
   historical pattern shows is needed — without exposing sensitive data or
   requiring a judgment call on money, fraud, or exceptions. This was decided
   explicitly after noticing that most of Amazon's own real replies
   are themselves "please contact us to resolve" redirects, meaning a naive
   "auto = plausible-sounding reply" standard would auto-approve cases Amazon
   itself treats as needing a human.

9. **`account_security` always escalates by policy**, regardless of message
   content or classifier confidence — the cost of a wrong auto-response
   (exposing/mishandling account access) is asymmetric and high; not worth
   trusting to a confidence threshold.

10. **Escalation also triggers on repeat-contact and distrust-tone signals**,
    not just intent category — e.g., "second time," "already contacted," or
    "expect me to believe you" indicate the standard workflow has already
    failed once, or that a templated reply risks worsening the interaction.
    Implemented as keyword matching in `decide.py` — acknowledged as a
    simplification; a stronger version would ask the LLM to judge tone
    directly rather than string-match.

11. **Used Ollama (`llama3.2`, local) rather than a paid API** for the full
    build — free, fast iteration, and the assignment explicitly permits any
    LLM or open model. Trade-off: noted that a frontier API model would likely
    score higher on classification accuracy and instruction-following, since
    smaller local models are less reliable at strict output-format
    compliance.

12. **Retrieval built on TF-IDF cosine similarity over ~61k historical
    (customer, reply) pairs**, not embeddings/a vector DB — sufficient for
    clearly finding near-duplicate complaint patterns at this scale, and
    avoids infrastructure overkill for a one-week project.

13. **Stripped URLs from retrieved examples before drafting**, after discovering
    the LLM would otherwise copy a different customer's real tracking link
    verbatim into a new draft — a genuine hallucination risk from grounding
    on real historical text.

14. **Instructed the drafter not to invent placeholders** (e.g., "@username,"
    "@123456") after an earlier version fabricated fake handles/order numbers
    — even placeholder hallucination isn't acceptable for a system meant to
    draft real customer-facing replies.

15. **Built and explicitly validated the LLM-judge against manual scoring**
    (30-example sample) rather than trusting judge scores at face value.
    Result: judge agreement was strong for tone (73% exact match) but weak for
    relevance (23%) and groundedness (33%) — meaning the judge's raw
    groundedness score should not be reported as a standalone headline
    number without this caveat.

16. **Fixed CSV encoding corruption via `latin-1` fallback read + re-save as
    UTF-8**, after the golden-set file was repeatedly corrupted by Excel
    re-saving it as Windows-1252 mid-labeling — moved final labeling work
    away from Excel to avoid recurrence.