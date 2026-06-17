def check_source(text: str):

    text = text.lower()

    trusted = [
        "bbc",
        "reuters",
        "nasa"
    ]

    flagged = [
        "dailybuzz",
        "clicknews",
        "whatsapp forward"
    ]

    for src in trusted:

        if src in text:
            return {
                "source": src,
                "status": "Verified"
            }

    for src in flagged:

        if src in text:
            return {
                "source": src,
                "status": "Flagged / Unreliable"
            }

    return {
        "source": "Unknown",
        "status": "Unverified"
    }