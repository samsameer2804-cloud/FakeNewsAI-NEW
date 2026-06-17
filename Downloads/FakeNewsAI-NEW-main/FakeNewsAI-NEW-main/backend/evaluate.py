import pandas as pd
import asyncio
from main import analyze_news, NewsInput

fake = pd.read_csv("data/Fake.csv").head(50)
true = pd.read_csv("data/True.csv").head(50)

correct = 0
total = 0

async def test_article(text, expected):
    global correct, total

    result = await analyze_news(NewsInput(text=text))
    prediction = result["final_verdict"]["verdict"]

    if prediction == expected:
        correct += 1

    total += 1

async def run():
    for _, row in fake.iterrows():
        await test_article(row["text"], "FAKE")

    for _, row in true.iterrows():
        await test_article(row["text"], "REAL")

    print(f"Correct: {correct}")
    print(f"Total: {total}")
    print(f"Accuracy: {(correct/total)*100:.2f}%")

asyncio.run(run())