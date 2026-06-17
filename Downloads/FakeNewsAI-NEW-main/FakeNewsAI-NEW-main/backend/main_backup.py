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
        "verified_fact": "NASA successfully launched the Artemis II lunar mission with four astronauts.",
        "credibility_score": "High"
    },
    "cdc": {
        "verified_fact": "CDC provides verified public health guidance and vaccination recommendations.",
        "credibility_score": "High"
    },
    "who": {
        "verified_fact": "WHO is the global public health authority operating under the United Nations.",
        "credibility_score": "High"
    },
    "isro": {
        "verified_fact": "ISRO successfully landed Chandrayaan-3 on the Moon's south pole in 2023.",
        "credibility_score": "High"
    },
    "microsoft": {
        "verified_fact": "Microsoft is a global technology company founded by Bill Gates in 1975.",
        "credibility_score": "High"
    },
    "google": {
        "verified_fact": "Google is a multinational technology company specializing in internet services and AI.",
        "credibility_score": "High"
    },
    "apple": {
        "verified_fact": "Apple Inc. is a technology company known for iPhone, Mac, and iOS products.",
        "credibility_score": "High"
    },
    "un": {
        "verified_fact": "The United Nations is an international organization founded in 1945 to promote peace.",
        "credibility_score": "High"
    },
    "unicef": {
        "verified_fact": "UNICEF is the United Nations agency responsible for providing aid to children worldwide.",
        "credibility_score": "High"
    },
    "wikipedia": {
        "verified_fact": "Wikipedia is a free online encyclopedia collaboratively edited by volunteers worldwide.",
        "credibility_score": "Medium"
    },
    "elon musk": {
        "verified_fact": "Elon Musk is the CEO of Tesla and SpaceX and owner of X (formerly Twitter).",
        "credibility_score": "Medium"
    },
    "spacex": {
        "verified_fact": "SpaceX is a private aerospace company founded by Elon Musk in 2002.",
        "credibility_score": "High"
    },
    "tesla": {
        "verified_fact": "Tesla is an electric vehicle and clean energy company led by Elon Musk.",
        "credibility_score": "High"
    },
    "oxford": {
        "verified_fact": "Oxford University is one of the oldest and most prestigious universities in the world.",
        "credibility_score": "High"
    },
    "harvard": {
        "verified_fact": "Harvard University is a private Ivy League research university in Cambridge, Massachusetts.",
        "credibility_score": "High"
    },
    "bbc": {
        "verified_fact": "BBC is the British Broadcasting Corporation, a publicly funded UK media organization.",
        "credibility_score": "High"
    },
    "reuters": {
        "verified_fact": "Reuters is an international news organization known for factual and unbiased reporting.",
        "credibility_score": "High"
    },
    "climate": {
        "verified_fact": "UN climate reports confirm global temperatures have risen 1.1°C above pre-industrial levels.",
        "credibility_score": "High"
    },
    "covid": {
        "verified_fact": "COVID-19 is a respiratory disease caused by the SARS-CoV-2 virus, first identified in 2019.",
        "credibility_score": "High"
    },
    "india": {
        "verified_fact": "India is the world's most populous country and the largest democracy.",
        "credibility_score": "High"
    },
    "rbi": {
        "verified_fact": "The Reserve Bank of India is the central banking institution of India, established in 1935.",
        "credibility_score": "High"
    },
    "supreme court": {
        "verified_fact": "The Supreme Court of India is the highest judicial authority in the country.",
        "credibility_score": "High"
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