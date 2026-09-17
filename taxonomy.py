INTENTS = {
    "delivery_delay": "Order has not yet arrived, past the expected/promised delivery date.",

    "delivery_not_received": "Tracking/notification shows delivered (or attempted) but customer says it never arrived, was misdelivered, or was left in an unsafe/wrong location.",

    "item_quality_issue": "Wrong, damaged, counterfeit, defective, or tampered item received.",

    "refund_billing": "Refund requests, duplicate or unexpected charges, subscription billing disputes, cashback/promo issues, pricing discrepancies.",

    "account_security": "Login/access issues, locked or suspended accounts, unauthorized access or orders, phishing reports, account compromise.",

    "app_device_technical": "Bugs or issues with Kindle, Echo, Fire TV, the Amazon app, or streaming/content playback.",

    "general_complaint": "Frustration, venting, or dissatisfaction with no single specific resolvable request — includes staff/rep conduct complaints.",

    "informational": "Pre-purchase questions, policy questions, feature requests, praise, or general product/service questions — no problem to resolve.",
}

OFF_TOPIC_LABEL = "off_topic"

VALID_LABELS = list(INTENTS.keys()) + [OFF_TOPIC_LABEL]

# intents that should always escalate
DEFAULT_ESCALATE_INTENTS = {"account_security"}