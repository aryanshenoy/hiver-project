# decide.py
from taxonomy import DEFAULT_ESCALATE_INTENTS

REPEAT_CONTACT_SIGNALS = [
    "again", "second time", "third time", "2nd time", "3rd time",
    "already contacted", "already told", "still waiting", "no resolution",
    "no response", "no reply", "for weeks", "for days"
]

DISTRUST_SIGNALS = [
    "expect me to believe", "insult my intelligence", "you're lying",
    "lied", "don't believe", "seriously?", "are you kidding"
]

SEVERE_SIGNALS = [
    "hacked", "stolen", "theft", "fraud", "scam", "trespass",
    "unauthorized", "threatening", "legal", "sue", "lawyer"
]

def decideEscalation(intent, message):
    """
    Returns (decision, reason) where decision is 'auto' or 'escalate'.
    Mirrors the manual rules used when labeling the golden set.
    """
    message_lower = message.lower()

    if intent in DEFAULT_ESCALATE_INTENTS:
        return "escalate", f"{intent} always escalates by policy (security-sensitive)"

    if any(sig in message_lower for sig in SEVERE_SIGNALS):
        return "escalate", "message contains a severity signal (fraud/theft/legal/safety) requiring human review"

    if any(sig in message_lower for sig in REPEAT_CONTACT_SIGNALS):
        return "escalate", "message indicates repeated/failed prior contact — standard workflow likely already failed"

    if any(sig in message_lower for sig in DISTRUST_SIGNALS):
        return "escalate", "distrustful/skeptical tone toward standard explanation — templated reply risks worsening it"

    return "auto", f"{intent} resolvable via standard first-response workflow, no escalation trigger detected"