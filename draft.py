import re
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

def stripUrls(text):
    """Replace URLs with a placeholder so the model doesn't copy real links from other customers."""
    return re.sub(r'https?://\S+', '[link]', text)

def draftReply(customer_message, similar_examples, model="llama3.2"):
    """
    customer_message: the new incoming customer message (str)
    similar_examples: list of (customer_message, amazon_reply) tuples from retrieve.py
    """
    examples_text = "\n\n".join(
        f"Customer: {stripUrls(ex[0])}\nAmazon's reply: {stripUrls(ex[1])}"
        for ex in similar_examples
    )

    system_prompt = f"""You are drafting a reply as AmazonHelp support, in the style of how
Amazon has historically resolved similar issues. Here are real past examples (for TONE AND STYLE ONLY —
do not reuse any specific links, order numbers, names, or tracking numbers from these examples,
since they belong to different customers):

{examples_text}

Write a reply to the NEW customer message below, matching Amazon's tone and typical resolution
approach. Keep it concise, like a real tweet reply. Do not include any URLs or made-up links.
Do not invent an order number, tracking number, or customer name that wasn't given to you.
Do not invent placeholder text like "@username" or "@123456" — if you don't have the 
customer's handle or an order number, phrase the reply generically without needing one 
(e.g. "Can you DM us your order details?" rather than inventing a placeholder)."""

    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": stripUrls(customer_message)}
        ],
        "stream": False
    })
    response.raise_for_status()
    raw_reply = response.json()["message"]["content"].strip()

    # extra safety net: strip any URL the model might still hallucinate despite instructions
    return stripUrls(raw_reply).replace("[link]", "").strip()