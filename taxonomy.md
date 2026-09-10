# Intent Taxonomy — AmazonHelp Support Agent

Built by manually reading ~150 randomly sampled English-language customer
threads directed at @AmazonHelp (seed=42, from twcs.csv). Categories emerged
from repeated patterns rather than being predefined.

## Intents

1. **delivery_delay** — Order has not yet arrived, past the expected/promised date.
2. **delivery_not_received** — Tracking/app shows "delivered" but customer says it
   never arrived, or was delivered to the wrong address.
3. **item_quality_issue** — Wrong item, damaged item, counterfeit/fake product, or
   defective item received.
4. **refund_billing** — Refund requests, duplicate/unexpected charges, subscription
   billing disputes, cashback/promo issues.
5. **account_security** — Login/access issues, locked accounts, unauthorized
   access or orders, phishing reports. Default: escalate (never auto-handle).
6. **app_device_technical** — Bugs or issues with Kindle, Echo, Fire TV, the
   Amazon app, or streaming/content playback.
7. **general_complaint** — Frustration/venting with no specific, resolvable
   request attached.
8. **informational** — Pre-purchase questions, feature requests, praise,
   general product questions — no problem to resolve.

## Excluded (not an intent)
- **off_topic** — Not a genuine support message (spam, unrelated mentions,
  content promo, etc.) — flagged and dropped from core pipeline eval, but
  counted and reported as dataset noise.