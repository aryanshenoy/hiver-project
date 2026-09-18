import json
from taxonomy import VALID_LABELS
from classify import classifyMessage
from retrieve import buildRetriever
from draft import draftReply
from decide import decideEscalation

def loadHistoricalPairs(path='data/amazon_english_threads.json'):
    with open(path, encoding='utf-8') as f:
        threads = json.load(f)
    pairs = []
    for t in threads:
        tweets = t['tweets']
        if not tweets:
            continue
        customer_msg = tweets[0]['text']
        amazon_reply = next((tw['text'] for tw in tweets if tw['author_id'] == 'AmazonHelp'), None)
        if amazon_reply:
            pairs.append((customer_msg, amazon_reply))
    return pairs

def loadFewShotExamples(goldenSetPath='eval/golden_set.csv', numberPerIntent=2):
    import pandas as pd
    df = pd.read_csv(goldenSetPath, encoding='utf-8')
    few_shot = df.groupby('intent', group_keys=False).apply(
        lambda g: g.sample(n=min(numberPerIntent, len(g)), random_state=42)
    )
    return few_shot[['customer_message', 'intent']].to_dict('records')

def processMessage(customerMessage, retriever, fewShotExamples):
    """Runs the full pipeline on one customer message."""
    intent = classifyMessage(customerMessage, fewShotExamples)

    if intent == "off_topic":
        return {
            "customer_message": customerMessage,
            "intent": intent,
            "drafted_reply": None,
            "decision": None,
            "reason": "off-topic — not a genuine support request, no action taken",
        }

    similar_examples = retriever(customerMessage, k=3)
    drafted_reply = draftReply(customerMessage, similar_examples)
    decision, reason = decideEscalation(intent, customerMessage)

    return {
        "customer_message": customerMessage,
        "intent": intent,
        "drafted_reply": drafted_reply,
        "decision": decision,
        "reason": reason,
    }

def main():
    print("Loading historical data...")
    historical_pairs = loadHistoricalPairs()
    retriever = buildRetriever(historical_pairs)
    few_shot_examples = loadFewShotExamples()
    print(f"Ready. {len(historical_pairs)} historical pairs loaded.\n")

    demo_messages = [
        "My package was supposed to arrive today but tracking shows it's still not shipped",
        "Someone got into my account and changed my password",
        "The item I received is completely different from what I ordered",
        "Epstein Island was in Amazon Rainforest",
        "Hi!",
        "Wow Amazon is such a great place to hangout! Lots of snakes and animals and stuff, it gets scary at night tho.",
    ]

    for msg in demo_messages:
        result = processMessage(msg, retriever, few_shot_examples)
        print("=" * 70)
        print(f"MESSAGE: {result['customer_message']}")
        print(f"INTENT: {result['intent']}")
        if result['drafted_reply']:
            print(f"DRAFTED REPLY: {result['drafted_reply']}")
            print(f"DECISION: {result['decision']} — {result['reason']}")
        print()

if __name__ == "__main__":
    main()