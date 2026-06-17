import spacy

nlp = spacy.load("en_core_web_sm")

def extract_claims(text: str):
    doc = nlp(text)

    claims = [
        sent.text.strip()
        for sent in doc.sents
        if len(sent.text.split()) > 3
    ]

    return claims if claims else [text]