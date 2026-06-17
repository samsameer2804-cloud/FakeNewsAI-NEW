from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import joblib
import re
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load("fake_news_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# =========================================================
# FASTAPI APP
# =========================================================

GOOGLE_FACTCHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

factcheck_cache = {}
newsapi_cache = {}

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

    # === SPACE & SCIENCE ===
    "nasa": {"verified_fact": "NASA is the US space agency responsible for space exploration.", "credibility_score": "High"},
    "isro": {"verified_fact": "ISRO landed Chandrayaan-3 on the Moon's south pole in 2023.", "credibility_score": "High"},
    "spacex": {"verified_fact": "SpaceX is a private aerospace company founded by Elon Musk in 2002.", "credibility_score": "High"},
    "esa": {"verified_fact": "ESA is the European Space Agency coordinating Europe's space activities.", "credibility_score": "High"},
    "cern": {"verified_fact": "CERN operates the Large Hadron Collider and discovered the Higgs boson in 2012.", "credibility_score": "High"},
    "nih": {"verified_fact": "NIH is the US National Institutes of Health, the primary federal medical research agency.", "credibility_score": "High"},

    # === HEALTH & MEDICINE ===
    "cdc": {"verified_fact": "CDC provides verified public health guidance and vaccination recommendations.", "credibility_score": "High"},
    "who": {"verified_fact": "WHO is the global public health authority under the United Nations.", "credibility_score": "High"},
    "covid": {"verified_fact": "COVID-19 is caused by SARS-CoV-2, first identified in Wuhan, China in 2019.", "credibility_score": "High"},
    "vaccine": {"verified_fact": "Vaccines are medically approved tools to prevent infectious diseases.", "credibility_score": "High"},
    "fda": {"verified_fact": "FDA is the US Food and Drug Administration regulating food, drugs, and medical devices.", "credibility_score": "High"},
    "aiims": {"verified_fact": "AIIMS is India's premier medical institution and hospital network.", "credibility_score": "High"},
    "icmr": {"verified_fact": "ICMR is the Indian Council of Medical Research, India's top medical research body.", "credibility_score": "High"},

    # === TECH COMPANIES ===
    "microsoft": {"verified_fact": "Microsoft is a global technology company founded by Bill Gates in 1975.", "credibility_score": "High"},
    "google": {"verified_fact": "Google is a multinational technology company specializing in internet services and AI.", "credibility_score": "High"},
    "apple": {"verified_fact": "Apple Inc. is known for iPhone, Mac, and iOS products.", "credibility_score": "High"},
    "meta": {"verified_fact": "Meta Platforms owns Facebook, Instagram, and WhatsApp.", "credibility_score": "High"},
    "amazon": {"verified_fact": "Amazon is the world's largest e-commerce and cloud computing company.", "credibility_score": "High"},
    "openai": {"verified_fact": "OpenAI is an AI research company that created ChatGPT and GPT-4.", "credibility_score": "High"},
    "anthropic": {"verified_fact": "Anthropic is an AI safety company that created the Claude AI assistant.", "credibility_score": "High"},
    "nvidia": {"verified_fact": "NVIDIA is a semiconductor company dominant in GPU and AI chip markets.", "credibility_score": "High"},
    "samsung": {"verified_fact": "Samsung is a South Korean multinational electronics and technology company.", "credibility_score": "High"},
    "ibm": {"verified_fact": "IBM is a global technology company known for enterprise software and AI research.", "credibility_score": "High"},
    "intel": {"verified_fact": "Intel is a US semiconductor company and one of the world's largest chip makers.", "credibility_score": "High"},

    # === PEOPLE ===
    "elon musk": {"verified_fact": "Elon Musk is CEO of Tesla and SpaceX, and owner of X (formerly Twitter).", "credibility_score": "Medium"},
    "bill gates": {"verified_fact": "Bill Gates is co-founder of Microsoft and co-chair of the Bill & Melinda Gates Foundation.", "credibility_score": "High"},
    "narendra modi": {"verified_fact": "Narendra Modi is the Prime Minister of India since 2014.", "credibility_score": "High"},
    "joe biden": {"verified_fact": "Joe Biden served as the 46th President of the United States from 2021 to 2025.", "credibility_score": "High"},
    "donald trump": {"verified_fact": "Donald Trump is the 45th and 47th President of the United States.", "credibility_score": "High"},
    "sam altman": {"verified_fact": "Sam Altman is the CEO of OpenAI.", "credibility_score": "High"},
    "sundar pichai": {"verified_fact": "Sundar Pichai is the CEO of Google and Alphabet.", "credibility_score": "High"},
    "pope francis": {"verified_fact": "Pope Francis is the head of the Catholic Church since 2013.", "credibility_score": "High"},

    # === MEDIA & INFORMATION ===
    "bbc": {"verified_fact": "BBC is the British Broadcasting Corporation, a publicly funded UK media organization.", "credibility_score": "High"},
    "reuters": {"verified_fact": "Reuters is an international news organization known for factual reporting.", "credibility_score": "High"},
    "ap": {"verified_fact": "Associated Press (AP) is a nonprofit American news agency founded in 1846.", "credibility_score": "High"},
    "wikipedia": {"verified_fact": "Wikipedia is a free online encyclopedia collaboratively edited by volunteers.", "credibility_score": "Medium"},
    "snopes": {"verified_fact": "Snopes is a well-known fact-checking website.", "credibility_score": "High"},

    # === INTERNATIONAL ORGANIZATIONS ===
    "un": {"verified_fact": "The United Nations is an international organization founded in 1945.", "credibility_score": "High"},
    "unicef": {"verified_fact": "UNICEF is the United Nations agency providing aid to children worldwide.", "credibility_score": "High"},
    "imf": {"verified_fact": "IMF is the International Monetary Fund, a global financial institution.", "credibility_score": "High"},
    "world bank": {"verified_fact": "The World Bank provides financial and technical assistance to developing countries.", "credibility_score": "High"},
    "nato": {"verified_fact": "NATO is the North Atlantic Treaty Organization, a military alliance of 31 countries.", "credibility_score": "High"},
    "interpol": {"verified_fact": "Interpol is an international police cooperation organization.", "credibility_score": "High"},
    "wto": {"verified_fact": "WTO is the World Trade Organization regulating international trade.", "credibility_score": "High"},

    # === INDIA SPECIFIC ===
    "india": {"verified_fact": "India is the world's most populous country and largest democracy.", "credibility_score": "High"},
    "rbi": {"verified_fact": "The Reserve Bank of India is the central banking institution, established in 1935.", "credibility_score": "High"},
    "supreme court": {"verified_fact": "The Supreme Court of India is the highest judicial authority in the country.", "credibility_score": "High"},
    "sebi": {"verified_fact": "SEBI is the Securities and Exchange Board of India, regulating the securities market.", "credibility_score": "High"},
    "pib": {"verified_fact": "PIB is the Press Information Bureau, the official government communication body in India.", "credibility_score": "High"},
    "eci": {"verified_fact": "ECI is the Election Commission of India, responsible for conducting elections.", "credibility_score": "High"},
    "uidai": {"verified_fact": "UIDAI manages India's Aadhaar biometric identity system.", "credibility_score": "High"},
    "bcci": {"verified_fact": "BCCI is the Board of Control for Cricket in India, governing cricket in the country.", "credibility_score": "High"},
    "iit": {"verified_fact": "IITs are India's premier engineering institutions established by the Indian government.", "credibility_score": "High"},
    "niti aayog": {"verified_fact": "NITI Aayog is India's premier public policy think tank.", "credibility_score": "High"},

    # === UNIVERSITIES ===
    "oxford": {"verified_fact": "Oxford University is one of the oldest and most prestigious universities in the world.", "credibility_score": "High"},
    "harvard": {"verified_fact": "Harvard University is a private Ivy League research university in Massachusetts.", "credibility_score": "High"},
    "mit": {"verified_fact": "MIT is the Massachusetts Institute of Technology, a leading science and engineering university.", "credibility_score": "High"},
    "stanford": {"verified_fact": "Stanford University is a leading research university in California.", "credibility_score": "High"},
    "cambridge": {"verified_fact": "Cambridge University is one of the world's oldest and most prestigious universities.", "credibility_score": "High"},

    # === ENVIRONMENT & CLIMATE ===
    "climate": {"verified_fact": "UN reports confirm global temperatures have risen 1.1°C above pre-industrial levels.", "credibility_score": "High"},
    "ipcc": {"verified_fact": "IPCC is the Intergovernmental Panel on Climate Change, the UN body for climate science.", "credibility_score": "High"},
    "unep": {"verified_fact": "UNEP is the United Nations Environment Programme.", "credibility_score": "High"},

    # === FINANCE ===
    "tesla": {"verified_fact": "Tesla is an electric vehicle and clean energy company led by Elon Musk.", "credibility_score": "High"},
    "bitcoin": {"verified_fact": "Bitcoin is a decentralized digital cryptocurrency created in 2009.", "credibility_score": "Medium"},
    "sensex": {"verified_fact": "Sensex is the benchmark index of the Bombay Stock Exchange in India.", "credibility_score": "High"},
    "nse": {"verified_fact": "NSE is the National Stock Exchange of India.", "credibility_score": "High"},
    "fed": {"verified_fact": "The Federal Reserve is the central banking system of the United States.", "credibility_score": "High"},

    # === CRICKET ===
    "bcci": {"verified_fact": "BCCI is the Board of Control for Cricket in India.", "credibility_score": "High"},
    "ipl": {"verified_fact": "IPL is the Indian Premier League T20 cricket competition.", "credibility_score": "High"},
    "icc": {"verified_fact": "ICC is the International Cricket Council, global governing body of cricket.", "credibility_score": "High"},
    "cricket": {"verified_fact": "Cricket is governed internationally by the ICC.", "credibility_score": "High"},
    "vaibhav sooryavanshi": {"verified_fact": "Vaibhav Sooryavanshi is a teenage Indian cricket prodigy who scored 776 runs in IPL 2026.", "credibility_score": "High"},
    "rohit sharma": {"verified_fact": "Rohit Sharma is the captain of the Indian cricket team.", "credibility_score": "High"},
    "virat kohli": {"verified_fact": "Virat Kohli is a former Indian captain and batting legend.", "credibility_score": "High"},
    "ms dhoni": {"verified_fact": "MS Dhoni led India to the 2011 World Cup victory.", "credibility_score": "High"},
    "anura tennekoon": {"verified_fact": "Anura Tennekoon was Sri Lanka's first ODI captain in the 1975 World Cup.", "credibility_score": "High"},

    # === POLITICS ===
    "parliament": {"verified_fact": "Indian Parliament is the supreme legislative body of India.", "credibility_score": "High"},
    "lok sabha": {"verified_fact": "Lok Sabha is the lower house of India's Parliament.", "credibility_score": "High"},
    "white house": {"verified_fact": "The White House is the official residence of the US President.", "credibility_score": "High"},

    # === BUSINESS ===
    "tata": {"verified_fact": "Tata Group is India's largest multinational conglomerate.", "credibility_score": "High"},
    "reliance": {"verified_fact": "Reliance Industries is India's largest company by revenue.", "credibility_score": "High"},
    "infosys": {"verified_fact": "Infosys is a leading Indian multinational IT company.", "credibility_score": "High"},
    "wipro": {"verified_fact": "Wipro is a major Indian IT and consulting company.", "credibility_score": "High"},

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

    text_lower = text.lower()
    entities = []

    for entity in MOCK_KNOWLEDGE_GRAPH.keys():
        if entity in text_lower:        # ← ONE LINE FIX
            entities.append(entity)

    print("[Claim Agent] Found:", entities)
    return entities

# =========================================================
# LINGUISTIC AGENT
# =========================================================

async def linguistic_analysis_agent(text: str):

    print("[Linguistic Agent] Running...")

    clickbait_words = [
    # Sensationalism
    "shocking", "unbelievable", "mind-blowing", "jaw-dropping",
    "incredible", "insane", "outrageous", "bombshell", "explosive",
    "scandalous", "sensational", "astounding", "staggering",

    # Conspiracy / Distrust
    "secret", "conspiracy", "cover-up", "hidden truth", "they don't want you to know",
    "what they're hiding", "mainstream media won't tell you", "suppressed",
    "deep state", "new world order", "illuminati", "plandemic",

    # Urgency / Fear
    "breaking", "urgent", "alert", "warning", "danger", "crisis",
    "you won't believe", "must read", "share before deleted",
    "act now", "limited time", "before it's too late",

    # Fake credibility
    "100% true", "proven", "confirmed", "officially confirmed",
    "scientists baffled", "doctors hate this", "one weird trick",

    # Alien / Supernatural
    "aliens", "ufo", "reptilian", "supernatural", "miracle cure",
    "big pharma", "government admits"
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
# INTERNET VERIFICATION AGENT
# =========================================================

async def internet_verification_agent(text: str):

    print("[Internet Agent] Running...")

    cache_key = text[:100]

    if cache_key in factcheck_cache:
        print("[Internet Agent] Returning cached result")
        return factcheck_cache[cache_key]

    try:

        query = text[:100].replace(" ", "+")

        url = (
            f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
            f"?query={query}&key={GOOGLE_FACTCHECK_API_KEY}&languageCode=en"
        )

        async with httpx.AsyncClient() as client:

            response = await client.get(url, timeout=5.0)
            data = response.json()

        claims = data.get("claims", [])

        if not claims:

            result = {
                "found": False,
                "result": "No fact-check records found online."
            }

        else:

            top        = claims[0]
            claim_text = top.get("text", "")
            claimant   = top.get("claimant", "Unknown")
            review     = top.get("claimReview", [{}])[0]
            publisher  = review.get("publisher", {}).get("name", "Unknown")
            rating     = review.get("textualRating", "Unrated")
            review_url = review.get("url", "")

            result = {
                "found": True,
                "claim": claim_text,
                "claimant": claimant,
                "publisher": publisher,
                "rating": rating,
                "url": review_url
            }

        factcheck_cache[cache_key] = result

        return result

    except Exception as e:

        print("[Internet Agent] Error:", e)

        return {
            "found": False,
            "result": f"Could not reach API: {str(e)}"
        }


# =========================================================
# NEWS API VERIFICATION AGENT
# =========================================================

async def newsapi_verification_agent(text: str):

    print("[NewsAPI Agent] Running...")

    cache_key = text[:100]

    if cache_key in newsapi_cache:
        print("[NewsAPI Agent] Returning cached result")
        return newsapi_cache[cache_key]

    try:

        # Take first 50 chars as search query
        query = text[:50].replace(" ", "+")

        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={query}"
            f"&apiKey={NEWSAPI_KEY}"
            f"&pageSize=3"
            f"&language=en"
        )

        async with httpx.AsyncClient() as client:

            response = await client.get(url, timeout=5.0)
            data = response.json()

        articles = data.get("articles", [])
        total    = data.get("totalResults", 0)

        if not articles or total == 0:

            result = {
                "found": False,
                "total_sources": 0,
                "result": "No matching news found in verified sources."
            }

        else:

            # Get top 3 sources
            sources = []

            for article in articles[:3]:
                sources.append({
                    "title":  article.get("title", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url":    article.get("url", "")
                })

            result = {
                "found":         True,
                "total_sources": total,
                "top_sources":   sources,
                "result": f"Found in {total} verified news sources worldwide."
            }

        newsapi_cache[cache_key] = result

        return result

    except Exception as e:

        print("[NewsAPI Agent] Error:", e)

        return {
            "found":         False,
            "total_sources": 0,
            "result": f"Could not reach NewsAPI: {str(e)}"
        }



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
    evidence,
    newsapi
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
    
    if newsapi.get("found") and newsapi.get("total_sources", 0) >= 3:
        source_count = newsapi["total_sources"]
        confidence = min(0.70 + round(source_count / 200, 2), 0.95)
        return {
            "verdict": "REAL",
            "confidence_score": confidence,
            "explanation": f"Story found across {source_count} verified news sources via NewsAPI."
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

        internet = await internet_verification_agent(text)

        newsapi  = await newsapi_verification_agent(text)

        consensus = await cross_verification_agent(
            linguistic,
            source_data,
            evidence,
            newsapi
        )

                # ----------------------------------
        # FINAL DECISION
        # ----------------------------------

                # ----------------------------------
        # GOOGLE FACT CHECK RATING LOGIC (add this block first)
        # ----------------------------------

        FALSE_RATINGS = [
            "false", "fake", "misleading", "incorrect", "debunked",
            "pants on fire", "mostly false", "not true", "fabricated"
        ]

        TRUE_RATINGS = [
            "true", "correct", "accurate", "mostly true",
            "verified", "confirmed", "legitimate"
        ]

        factcheck_verdict = None

        if internet.get("found") and internet.get("rating"):
            rating_lower = internet["rating"].lower()
            if any(r in rating_lower for r in FALSE_RATINGS):
                factcheck_verdict = "FAKE"
            elif any(r in rating_lower for r in TRUE_RATINGS):
                factcheck_verdict = "REAL"

        # ----------------------------------
        # FINAL DECISION (your existing block, now extended)
        # ----------------------------------

        if consensus["verdict"] == "FAKE":
            final_verdict = "FAKE"
            confidence = max(consensus["confidence_score"], ml_result["confidence"])
            explanation = consensus["explanation"]

        elif factcheck_verdict == "FAKE":                          # ← NEW
            final_verdict = "FAKE"
            confidence = 0.95
            explanation = f"Google Fact Check rated this claim as: '{internet['rating']}' by {internet.get('publisher', 'a verified fact-checker')}."

        elif factcheck_verdict == "REAL":                          # ← NEW
            final_verdict = "REAL"
            confidence = 0.95
            explanation = f"Google Fact Check verified this claim as: '{internet['rating']}' by {internet.get('publisher', 'a verified fact-checker')}."

        elif consensus["verdict"] == "REAL":
            final_verdict = "REAL"
            confidence = max(consensus["confidence_score"], ml_result["confidence"])
            explanation = consensus["explanation"]

        else:
            final_verdict = ml_result["verdict"]
            confidence = ml_result["confidence"]
            explanation = "No verified evidence found. Using ML model prediction."

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

                "internet_verification":
                    internet,

                "newsapi_verification":
                    newsapi,

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