import random


def get_score(store, online_score_request):
    score = 0
    if online_score_request.phone:
        score += 1.5
    if online_score_request.email:
        score += 1.5
    if online_score_request.birthday and online_score_request.gender:
        score += 1.5
    if online_score_request.first_name and online_score_request.last_name:
        score += 0.5
    return score


def get_interests(store, cid):
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return random.sample(interests, 2)

