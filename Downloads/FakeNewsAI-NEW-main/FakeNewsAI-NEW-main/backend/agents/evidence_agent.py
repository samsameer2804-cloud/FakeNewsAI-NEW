import os
import pandas as pd

DATASET_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "news_dataset.csv"
    )
)

if os.path.exists(DATASET_PATH):
    df_news = pd.read_csv(DATASET_PATH)
else:
    df_news = pd.DataFrame(
        columns=["title", "text", "label"]
    )

def retrieve_evidence(claims: list):

    evidence = []

    if df_news.empty:
        return [
            "No historical evidence database found."
        ]

    for claim in claims:

        if not claim.strip():
            continue

        words = claim.lower().split()

        for word in words:

            if len(word) < 4:
                continue

            matches = df_news[
                df_news["title"]
                .str.lower()
                .str.contains(word, na=False)
            ]

            for _, row in matches.head(1).iterrows():

                evidence.append(
                    f"Dataset Match [{row['label']}]: {row['title']}"
                )

    if not evidence:

        evidence.append(
            "No matching historical evidence found."
        )

    return evidence