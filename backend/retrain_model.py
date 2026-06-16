# backend/retrain_model.py
# Run this separately: python retrain_model.py

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# --------------------------------------------------
# STEP A: Load datasets
# Download these CSVs from Kaggle:
# 1. https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset
#    → Fake.csv and True.csv
# 2. Place both in backend/data/ folder
# --------------------------------------------------

fake_df = pd.read_csv("data/Fake.csv")
real_df = pd.read_csv("data/True.csv")

fake_df["label"] = 0   # 0 = FAKE
real_df["label"] = 1   # 1 = REAL

df = pd.concat([fake_df, real_df], ignore_index=True)
df = df[["text", "label"]].dropna()
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

print(f"Total samples: {len(df)}")
print(df["label"].value_counts())

# --------------------------------------------------
# STEP B: Train
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["label"], test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(max_features=10000, stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

preds = model.predict(X_test_vec)
print(f"Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")

# --------------------------------------------------
# STEP C: Save — replaces your existing .pkl files
# --------------------------------------------------

joblib.dump(model,      "fake_news_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model saved: fake_news_model.pkl")
print("Vectorizer saved: vectorizer.pkl")