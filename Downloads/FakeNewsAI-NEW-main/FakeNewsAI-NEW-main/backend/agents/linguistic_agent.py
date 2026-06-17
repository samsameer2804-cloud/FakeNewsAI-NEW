from textblob import TextBlob

def analyze_language(text: str):

    blob = TextBlob(text)

    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if subjectivity > 0.6:
        tone = "Highly Sensational"

    elif polarity < -0.2:
        tone = "Negative/Biased"

    elif polarity > 0.2:
        tone = "Positive/Promotional"

    else:
        tone = "Neutral"

    return {
        "tone": tone,
        "score": round(polarity, 2),
        "subjectivity": round(subjectivity, 2)
    }