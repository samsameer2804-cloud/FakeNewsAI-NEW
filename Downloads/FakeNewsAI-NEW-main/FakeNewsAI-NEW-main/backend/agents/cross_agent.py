def verify_news(language, source, evidence):

    fake_matches = sum(
        1 for ev in evidence
        if "[fake]" in ev.lower()
    )

    real_matches = sum(
        1 for ev in evidence
        if "[real]" in ev.lower()
    )

    if fake_matches > real_matches:
        return "Fake News Detected"

    elif real_matches > fake_matches:
        return "Verified Real News"

    elif language.get("subjectivity", 0) > 0.6:
        return "Suspicious / Unverified Claim"

    else:
        return "Likely Real News"