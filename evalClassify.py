import pandas as pd
from sklearn.metrics import classification_report, accuracy_score
from classify import classifyMessage
from baseline import most_frequent_baseline, train_tfidf_baseline
from taxonomy import VALID_LABELS

GOLDEN_SET_PATH = "eval/golden_set.csv"
FEW_SHOT_PER_INTENT = 2

def pickFewShotExamples(goldenSet, numberPerIntent = 2):
    fewShotRows = (
        goldenSet.groupby("intent", group_keys=False)
        .apply(lambda g: g.sample(n=min(numberPerIntent, len(g)), random_state=42))
    )
    return fewShotRows

def runLLMClassifier(goldenSet, fewShotExamples):
    predictions = []
    for i, msg in enumerate(goldenSet["customer_message"]):
        prediction = classifyMessage(msg, fewShotExamples)
        predictions.append(prediction)
        if (i + 1) % 20 == 0:
            print(f"  classified {i + 1}/{len(goldenSet)}")
    return predictions

def main():
    goldenSet = pd.read_csv(GOLDEN_SET_PATH, encoding="utf-8")

    # few-shot split (drawn from the full labeled set, including off_topic)
    fewShotDf = pickFewShotExamples(goldenSet, FEW_SHOT_PER_INTENT)
    evalDf = goldenSet.drop(fewShotDf.index).reset_index(drop=True)

    print(f"Few-shot examples: {len(fewShotDf)}")
    print(f"Held-out eval examples: {len(evalDf)}\n")

    fewShotExamples = fewShotDf[["customer_message", "intent"]].to_dict("records")

    # --- LLM classifier ---
    print("Running LLM classifier (Ollama)...")
    llm_preds = runLLMClassifier(evalDf, fewShotExamples)

    # --- Baselines ---
    print("\nRunning baselines...")
    trivial = most_frequent_baseline(fewShotDf["intent"])
    trivial_preds = [trivial(msg) for msg in evalDf["customer_message"]]

    tfidf_predict = train_tfidf_baseline(fewShotDf["customer_message"], fewShotDf["intent"])
    tfidf_preds = [tfidf_predict(msg) for msg in evalDf["customer_message"]]

    y_true = evalDf ["intent"].tolist()

    # --- Results ---
    print("\n" + "=" * 60)
    print("LLM CLASSIFIER (Ollama)")
    print("=" * 60)
    print(f"Accuracy: {accuracy_score(y_true, llm_preds):.3f}")
    print(classification_report(y_true, llm_preds, labels=VALID_LABELS, zero_division=0))

    print("\n" + "=" * 60)
    print("TRIVIAL BASELINE (most frequent class)")
    print("=" * 60)
    print(f"Accuracy: {accuracy_score(y_true, trivial_preds):.3f}")
    print(classification_report(y_true, trivial_preds, labels=VALID_LABELS, zero_division=0))

    print("\n" + "=" * 60)
    print("SIMPLE BASELINE (TF-IDF + Logistic Regression)")
    print("=" * 60)
    print(f"Accuracy: {accuracy_score(y_true, tfidf_preds):.3f}")
    print(classification_report(y_true, tfidf_preds, labels=VALID_LABELS, zero_division=0))

    # save predictions for later failure analysis
    results_df = evalDf.copy()
    results_df["llm_pred"] = llm_preds
    results_df["trivial_pred"] = trivial_preds
    results_df["tfidf_pred"] = tfidf_preds
    results_df.to_csv("eval/classification_results.csv", index=False, encoding="utf-8")
    print("\nSaved per-row predictions to eval/classification_results.csv")


if __name__ == "__main__":
    main()


