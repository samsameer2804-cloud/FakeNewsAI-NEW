FakeNews AI — Multi-Agent Verification Network
FakeNews AI is a collaborative, multi-agent AI system designed to detect disinformation by orchestrating multiple specialized verification modules. Moving beyond standard single-model classifiers, this project uses a multi-agent pipeline to cross-verify claims against linguistic patterns, entity credibility, and external knowledge sources.
🛠 System Architecture
The project utilizes a modular FastAPI backend to coordinate six specialized agents, providing a comprehensive "Verdict Breakdown" rather than just a binary result.
The Agent Pipeline
Claim Extraction: Isolates key entities (e.g., NASA, CDC) and core factual claims.
Linguistic Analysis: Evaluates text for sensationalism, hyperbole, and clickbait patterns.
Source Credibility: Audits the trust-index of the identified source entities.
Evidence Retrieval: Searches a local Knowledge Graph to verify factual consistency.
Internet Verification: Queries the Google Fact Check API for external validation.
ML Classification: Executes a TF-IDF + Logistic Regression model to calculate probability scores.
Consensus Resolver: An orchestrator agent aggregates these contributions to issue a final REAL, FAKE, or UNVERIFIED verdict.
🚀 Setup Guide
Prerequisites
Python 3.10+
Git
Installation
Clone the repository:
git clone [https://github.com/samsameer2804-cloud/FakeNewsAI-NEW.git](https://github.com/samsameer2804-cloud/FakeNewsAI-NEW.git)
cd FakeNewsAI-NEW


Backend Setup:
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r ../requirements.txt
pip install httpx python-dotenv


Configure API Key:
Create a file named .env inside the backend/ folder and add:
GOOGLE_FACTCHECK_API_KEY=your_api_key_here

(Note: Obtain your API key privately; do not commit this file to GitHub.)
Start the Engine:
uvicorn main:app --reload


🖥 Frontend Interface
The frontend is a premium, dashboard-style interface.
To run: Simply open the /frontend/index.html file directly in any modern web browser.
Features:
Live Pipeline Tracking: Watch as each agent completes its sub-routine in real-time.
Verdict Dashboard: Get high-confidence final reports with color-coded alerts.
Session Audit: Automatic logging of previous checks.
🧪 Testing
Scenario
Input Example
Expected Verdict
Fake News
"SHOCKING: Conspiracy exposed! Aliens living among us..."
FAKE
Real News
"NASA successfully launched the Artemis II lunar mission..."
REAL
Unverified
"The parliament passed a new budget bill..."
UNVERIFIED

⚠️ Troubleshooting
Backend Unreachable: Ensure the FastAPI server is running (uvicorn main:app --reload) on port 8000.
Environment Errors: Ensure you have activated the virtual environment and installed all dependencies from requirements.txt.
API Key Issues: Verify the .env file exists and the key is correctly formatted.
👤 Contact
For setup assistance or access to API keys, contact:
Sameer — samsameer2804-cloud
