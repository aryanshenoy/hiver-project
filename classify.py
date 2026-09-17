import requests
from taxonomy import INTENTS, VALID_LABELS

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

def buildSystemPrompt():
    intent_list = "\n".join(f"- {name}: {desc}" for name, desc in INTENTS.items())
    return f"""You are an intent classifier for AmazonHelp customer support messages on Twitter.   Classify the customer's message into EXACTLY ONE of these categories:
    {intent_list}
    - off_topic: Not a genuine support request (spam, unrelated content, insufficient context).
    Respond with ONLY the category name, nothing else. No explanation, no punctuation. Just the category name. If the message is off-topic, respond with "off_topic". Do not respond with any other text or formatting. Do not include any additional commentary or explanation. Only return the category name as a single word, in lowercase."""

def buildFewShotMessages(fewShotExamples):
    """
    fewShotExamples: list of dicts with 'customer_message' and 'intent' keys
    """
    messages = []
    for ex in fewShotExamples:
        messages.append({"role": "user", "content": ex["customer_message"]})
        messages.append({"role": "assistant", "content": ex["intent"]})
    return messages

def classifyMessage(customerMessage, fewShotExamples, model=MODEL_NAME):
    system_prompt = buildSystemPrompt()
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(buildFewShotMessages(fewShotExamples))
    messages.append({"role": "user", "content": customerMessage})

    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0}
    })
    response.raise_for_status()
    raw_output = response.json()["message"]["content"].strip().lower()

    if raw_output in VALID_LABELS:
        return raw_output
    for label in VALID_LABELS:
        if label in raw_output:
            return label
    return "off_topic"