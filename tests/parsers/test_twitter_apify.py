import json

import pytest

from src.models.shared import Post, Source
from src.parsers.twitter_apify import TwitterApifyParser

with open("tests/fixtures/twitter_apify_tweet.json") as f:
    tweet_document = json.load(f)

with open("tests/fixtures/twitter_apify_retweet.json") as f:
    retweet_document = json.load(f)

with open("tests/fixtures/twitter_apify_bad_retweet.json") as f:
    bad_retweet_document = json.load(f)

with open("tests/fixtures/twitter_apify_very_bad_retweet.json") as f:
    very_bad_retweet_document = json.load(f)

with open("tests/fixtures/twitter_apify_no_retweet_author_username.json") as f:
    no_retweet_author_username = json.load(f)

with open("tests/fixtures/twitter_apify_no_author_username.json") as f:
    no_author_username = json.load(f)

with open("tests/fixtures/twitter_apify_no_retweet_author_and_mentions.json") as f:
    no_retweet_author_and_mentions = json.load(f)

ok_test_cases = {
    "tweet_document": tweet_document,
    "retweet_document": retweet_document,
    "bad_retweet_document": bad_retweet_document,
    "very_bad_retweet_document": very_bad_retweet_document,
    "no_retweet_author_username": no_retweet_author_username,
    "no_retweet_author_and_mentions": no_retweet_author_and_mentions,
}

ko_test_cases = {
    "no_author_username": no_author_username,
}

input_file = "twitter_apify/topic_5d624512-4133-4647-8093-41cb7ef1c5a8/2026"


@pytest.mark.parametrize("document", ok_test_cases.values(), ids=ok_test_cases.keys())
def test_parses_post_correctly(document: dict):
    parser = TwitterApifyParser(input_file)
    post = parser.normalize_raw_document(document)
    assert isinstance(post, Post)
    assert post.source == Source.TWITTER


@pytest.mark.parametrize("document", ok_test_cases.values(), ids=ok_test_cases.keys())
def test_parses_interaction_correctly(document: dict):
    parser = TwitterApifyParser(input_file)
    interactions = parser.get_document_interactions(document)
    assert isinstance(interactions, list)
    assert all(interaction.n_likes is None for interaction in interactions)


@pytest.mark.parametrize("document", ko_test_cases.values(), ids=ko_test_cases.keys())
def test_not_parses_post(document: dict):
    parser = TwitterApifyParser(input_file)
    post = parser.normalize_raw_document(document)
    assert isinstance(post, type(None))


@pytest.mark.parametrize("document", ko_test_cases.values(), ids=ko_test_cases.keys())
def test_not_parses_interaction(document: dict):
    parser = TwitterApifyParser(input_file)
    interactions = parser.get_document_interactions(document)
    assert isinstance(interactions, list)
    assert len(interactions) == 0
