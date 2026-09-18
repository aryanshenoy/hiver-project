import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

JUDGE_RUBRIC = """You are evaluating a drafted customer support reply for AmazonHelp.
Score the reply from 1-5 on each of these dimensions:

1. Relevance: does it actually address the customer's specific problem?
2. Groundedness: does it match how Amazon has historically responded to similar issues (based on the examples given)?
3. Tone: does it sound like a real, professional AmazonHelp reply?

Respond in EXACTLY this format, nothing else:
relevance: <1-5>
groundedness: <1-5>
tone: <1-5>
"""

def judgeReply(customer_message, drafted_reply, similar_examples, model="llama3.2"):
    examples_text = "\n\n".join(
        f"Customer: {c}\nAmazon's reply: {r}" for c, r in similar_examples
    )
    user_content = f"""Customer message: {customer_message}

Historical examples for reference:
{examples_text}

Drafted reply to evaluate: {drafted_reply}"""

    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "messages": [
            {"role": "system", "content": JUDGE_RUBRIC},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "options": {"temperature": 0}
    })
    response.raise_for_status()
    raw = response.json()["message"]["content"].strip().lower()

    scores = {}
    for line in raw.split("\n"):
        for dim in ["relevance", "groundedness", "tone"]:
            if line.startswith(dim):
                try:
                    scores[dim] = int(''.join(filter(str.isdigit, line)))
                except ValueError:
                    scores[dim] = None
    return scores