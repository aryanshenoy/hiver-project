import json
import csv
import pandas as pd

from retrieve import buildRetriever
from draft import draftReply
from judge import judgeReply

with open('data/amazon_english_threads.json', encoding='utf-8') as f:
    threads = json.load(f)

historical_pairs = []
for t in threads:
    tweets = t['tweets']
    if not tweets:
        continue
    customer_msg = tweets[0]['text']
    amazon_reply = next((tw['text'] for tw in tweets if tw['author_id'] == 'AmazonHelp'), None)
    if amazon_reply:
        historical_pairs.append((customer_msg, amazon_reply))

retriever = buildRetriever(historical_pairs)

df = pd.read_csv('eval/golden_set.csv', encoding='utf-8')
df = df[df['intent'] != 'off_topic'].sample(n=30, random_state=42) 

rows = []
for _, row in df.iterrows():
    msg = row['customer_message']
    similar = retriever(msg, k=3)
    drafted = draftReply(msg, similar)
    scores = judgeReply(msg, drafted, similar)

    rows.append({
        'thread_id': row['thread_id'],
        'customer_message': msg,
        'drafted_reply': drafted,
        'judge_relevance': scores.get('relevance'),
        'judge_groundedness': scores.get('groundedness'),
        'judge_tone': scores.get('tone'),
        'human_relevance': '',      
        'human_groundedness': '',
        'human_tone': '',
    })
    print(f"Done: {row['thread_id']}")

with open('eval/judge_sample.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nSaved eval/judge_sample.csv — now open it and fill in the human_* columns by hand")