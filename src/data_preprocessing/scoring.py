def calculate_score(view_count=0, comment_count=0, sentiment_score=0):
    """
    Calculate the overall score for a piece of content.

    Formula:
        Score = (0.5 * view_count) + (0.3 * comment_count) + (0.2 * sentiment_score)

    Weights can be adjusted based on project needs.
    """
    normalized_sentiment = max(min(sentiment_score, 1), -1)  # Ensure sentiment_score is within [-1, 1]
    score = (0.5 * view_count) + (0.3 * comment_count) + (0.2 * normalized_sentiment * 100)
    return round(score, 2)


def assign_scores(data):
    """
    Assign a score to a list of data items.

    :param data: List of dictionaries containing 'view_count', 'comment_count', and 'sentiment_score'.
    :return: List of dictionaries with 'score' field added.
    """
    for item in data:
        view_count = item.get('view_count', 0)
        comment_count = item.get('comment_count', 0)
        sentiment_score = item.get('sentiment_score', 0)
        item['score'] = calculate_score(view_count, comment_count, sentiment_score)
    return data
