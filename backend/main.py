from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import joblib
import re

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load("fake_news_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="FakeNews AI",
    version="2.0.0",
    description="Multi-Agent Fake News Detection System"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# REQUEST MODEL
# =========================================================

class NewsInput(BaseModel):
    text: str

# =========================================================
# KNOWLEDGE GRAPH
# =========================================================

MOCK_KNOWLEDGE_GRAPH: Dict[str, Dict[str, str]] = {

    "nasa": {
        "verified_fact":
            "NASA successfully launched the Artemis II lunar mission.",
        "credibility_score":
            "High"
    },

   

    "cdc": {
        "verified_fact":
            "CDC provides verified public health guidance.",
        "credibility_score":
            "High"
    }
}

# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "FakeNews AI",
        "version": "2.0.0"
    }

# =========================================================
# CLAIM EXTRACTION AGENT
# =========================================================

async def claim_extraction_agent(text: str):

    print("\n[Claim Agent] Running...")

    tokens = re.findall(r"\b[a-z]+\b", text.lower())

    entities = []

    for entity in MOCK_KNOWLEDGE_GRAPH.keys():
        if entity in tokens:
            entities.append(entity)

    print("[Claim Agent] Found:", entities)

    return entities

# =========================================================
# LINGUISTIC AGENT
# =========================================================

async def linguistic_analysis_agent(text: str):

    print("[Linguistic Agent] Running...")

    clickbait_words = [

        "shocking",
        "unbelievable",
        "secret",
        "conspiracy",
        "aliens",
        "100% true",
        "breaking"

    ]

    found_flags = []

    lower = text.lower()

    for word in clickbait_words:
        if word in lower:
            found_flags.append(word)

    score = 0.90

    if found_flags:
        score = 0.45

    return {
        "linguistic_integrity_score": score,
        "flags": found_flags
    }

# =========================================================
# SOURCE CREDIBILITY AGENT
# =========================================================

async def source_credibility_agent(entities):

    print("[Source Agent] Running...")

    result = {}

    for entity in entities:

        if entity in MOCK_KNOWLEDGE_GRAPH:

            result[entity] = MOCK_KNOWLEDGE_GRAPH[
                entity
            ]["credibility_score"]

    return result

# =========================================================
# EVIDENCE AGENT
# =========================================================

async def evidence_retrieval_agent(entities):

    print("[Evidence Agent] Running...")

    evidence = []

    for entity in entities:

        if entity in MOCK_KNOWLEDGE_GRAPH:

            evidence.append(
                MOCK_KNOWLEDGE_GRAPH[entity]["verified_fact"]
            )

    return evidence

# =========================================================
# ML AGENT
# =========================================================

async def ml_classification_agent(text):

    print("[ML Agent] Running...")

    vector = vectorizer.transform([text])

    prediction = model.predict(vector)[0]

    probability = model.predict_proba(vector)[0]

    confidence = float(max(probability))

    verdict = "REAL" if prediction == 1 else "FAKE"

    return {
        "verdict": verdict,
        "confidence": round(confidence, 4)
    }

# =========================================================
# CROSS VERIFICATION AGENT
# =========================================================

async def cross_verification_agent(
    linguistic,
    source_data,
    evidence
):

    print("[Cross Verification Agent] Running...")

    if linguistic["linguistic_integrity_score"] < 0.5:

        return {
            "verdict": "FAKE",
            "confidence_score": 0.88,
            "explanation":
                "Clickbait or sensationalized language detected."
        }

    if evidence:

        return {
            "verdict": "REAL",
            "confidence_score": 0.94,
            "explanation":
                "Evidence found in Knowledge Graph."
        }

    return {
        "verdict": "UNVERIFIED",
        "confidence_score": 0.55,
        "explanation":
            "No matching evidence found."
    }

# =========================================================
# MAIN ANALYSIS ENDPOINT
# =========================================================

@app.post("/analyze")
async def analyze_news(input_data: NewsInput):

    try:

        text = input_data.text.strip()

        if not text:

            return {
                "status": "error",
                "message": "Empty text submitted."
            }

        # Prevent huge payloads

        text = text[:5000]

        print("\n====================================")
        print("NEW ANALYSIS REQUEST")
        print("====================================")

        # ----------------------------------

        entities = await claim_extraction_agent(text)

        linguistic = await linguistic_analysis_agent(text)

        source_data = await source_credibility_agent(
            entities
        )

        evidence = await evidence_retrieval_agent(
            entities
        )

        ml_result = await ml_classification_agent(
            text
        )

        consensus = await cross_verification_agent(
            linguistic,
            source_data,
            evidence
        )

                # ----------------------------------
        # FINAL DECISION
        # ----------------------------------

        if consensus["verdict"] == "FAKE":

            final_verdict = "FAKE"

            confidence = max(
                consensus["confidence_score"],
                ml_result["confidence"]
            )

            explanation = consensus["explanation"]

        elif consensus["verdict"] == "REAL":

            final_verdict = "REAL"

            confidence = max(
                consensus["confidence_score"],
                ml_result["confidence"]
            )

            explanation = consensus["explanation"]

        else:

            final_verdict = ml_result["verdict"]

            confidence = ml_result["confidence"]

            explanation = (
                "No verified evidence found. "
                "Using ML model prediction."
            )
        

        # ----------------------------------

        return {

            "status": "success",

            "final_verdict": {

                "verdict": final_verdict,

                "confidence_score":
                    round(confidence, 4),

                "explanation":
                    explanation
            },

            "agent_contributions": {

                "claim_extraction_agent": {
                    "identified_entities":
                        entities
                },

                "linguistic_agent":
                    linguistic,

                "source_credibility_agent":
                    source_data,

                "knowledge_graph_evidence":
                    evidence,

                "ml_classifier": {

                    "model":
                        "TF-IDF + Logistic Regression",

                    "prediction":
                        ml_result["verdict"],

                    "confidence":
                        ml_result["confidence"]
                }
            }
        }

    except Exception as e:

        print("ERROR:", e)

        return {

            "status": "error",

            "message": str(e)
        }