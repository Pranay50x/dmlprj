from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def predict_sentiment(text: str) -> tuple[str, float]:
    scores = _analyzer.polarity_scores(text)
    compound = float(scores.get("compound", 0.0))

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return label, compound
