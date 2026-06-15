async function analyzeNews() {

    const text = document.getElementById("newsText").value;
    const resultDiv = document.getElementById("result");
    const btn = document.getElementById("analyzeBtn");

    if (!text.trim()) {
        alert("Please enter some news text.");
        return;
    }

    btn.disabled = true;
    btn.innerText = "Orchestrating Core System Agents...";
    resultDiv.classList.add("hidden");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text
                })
            }
        );

        const data = await response.json();

        const verdict =
            data.final_verdict.verdict;

        let verdictClass = "unverified";

        if (verdict === "REAL")
            verdictClass = "real";

        if (verdict === "FAKE")
            verdictClass = "fake";

        resultDiv.innerHTML = `

        <div class="verdict-card"
             style="border-left-color:
             ${
                verdict === "REAL"
                ? "#4ade80"
                : verdict === "FAKE"
                ? "#f87171"
                : "#fbbf24"
             }">

            <div class="verdict-title ${verdictClass}">
                Verdict: ${verdict}
            </div>

            <div class="confidence-text">
                <strong>Confidence Level:</strong>
                ${Math.round(
                    data.final_verdict.confidence_score * 100
                )}%
            </div>

            <p class="explanation-text">
                <strong>System Analysis:</strong>
                ${data.final_verdict.explanation}
            </p>

        </div>

        <div class="section-title">
            Collaborative Agent System Metrics
        </div>

        <div class="agent-grid">

            <div class="agent-card">
                <h4>🔍 Claim Extraction Agent</h4>

                <div class="agent-content">

                    ${
                        data.agent_contributions
                            .claim_extraction_agent
                            .identified_entities.length > 0

                        ? data.agent_contributions
                            .claim_extraction_agent
                            .identified_entities
                            .map(
                                entity =>
                                `• ${entity.toUpperCase()}`
                            )
                            .join("<br>")

                        : "No entities detected"
                    }

                </div>
            </div>

            <div class="agent-card">
                <h4>📊 Linguistic Agent</h4>

                <div class="agent-content">

                    Score:
                    <strong>
                    ${Math.round(
                        data.agent_contributions
                        .linguistic_agent
                        .linguistic_integrity_score * 100
                    )}%
                    </strong>

                    <br>

                    <span
                        style="
                        color:#f87171;
                        font-size:12px;
                        ">

                        ${
                            data.agent_contributions
                            .linguistic_agent
                            .flags.length > 0

                            ? data.agent_contributions
                                .linguistic_agent
                                .flags.join(", ")

                            : "No stylistic alerts."
                        }

                    </span>

                </div>
            </div>

            <div class="agent-card">
                <h4>🛡️ Source Credibility Agent</h4>

                <div class="agent-content">

                    <pre>
${JSON.stringify(
    data.agent_contributions
        .source_credibility_agent,
    null,
    2
)}
                    </pre>

                </div>
            </div>

            <div class="agent-card">
                <h4>🕸️ Knowledge Graph Memory</h4>

                <div class="agent-content">

                    ${
                        data.agent_contributions
                        .knowledge_graph_evidence
                        .length > 0

                        ? data.agent_contributions
                            .knowledge_graph_evidence
                            .join("<br>")

                        : "Zero linked historical records found."
                    }

                </div>
            </div>

            <div class="agent-card">
                <h4>🤖 ML Classification Agent</h4>

                <div class="agent-content">

                    <strong>Model:</strong>

                    <br>

                    ${
                        data.agent_contributions
                        .ml_classifier.model
                    }

                    <br><br>

                    <strong>Prediction:</strong>

                    ${
                        data.agent_contributions
                        .ml_classifier.prediction
                    }

                    <br><br>

                    <strong>Confidence:</strong>

                    ${
                        Math.round(
                            data.agent_contributions
                            .ml_classifier
                            .confidence * 100
                        )
                    }%

                </div>
            </div>

        </div>
        `;

        resultDiv.classList.remove("hidden");

    } catch (error) {

        console.error(error);

        resultDiv.innerHTML = `

        <div class="verdict-card"
             style="border-left-color:#f87171">

            <div class="verdict-title fake">
                Connection Failure
            </div>

            <p class="explanation-text">

                Could not connect to the
                FastAPI backend.

                Make sure Uvicorn is running:

                <br><br>

                <strong>
                uvicorn main:app --reload
                </strong>

            </p>

        </div>
        `;

        resultDiv.classList.remove("hidden");

    } finally {

        btn.disabled = false;
        btn.innerText = "Analyze News";
    }
}