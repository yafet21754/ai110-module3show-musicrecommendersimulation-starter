from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""

import csv
from dataclasses import asdict
from pathlib import Path

import pytest

from src.recommender import load_songs, score_song, recommend_songs


def test_exact_score_and_reasons():
    song = asdict(make_small_recommender().songs[0])
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, song)
    assert score == pytest.approx(4.0)
    assert reasons == ["genre match (+2.00)", "mood match (+1.00)", "energy similarity 1.00 (+1.00)"]


def test_closer_energy_wins_even_when_lower():
    song = asdict(make_small_recommender().songs[0])
    prefs = {"genre": "unknown", "mood": "unknown", "energy": 0.2}
    assert score_song(prefs, dict(song, energy=0.2))[0] > score_song(prefs, dict(song, energy=0.9))[0]


def test_catalog_is_typed_and_expanded():
    songs = load_songs(Path(__file__).resolve().parents[1] / "data/songs.csv")
    assert len(songs) == 20
    assert len({song["id"] for song in songs}) == 20
    assert all(isinstance(song["id"], int) and isinstance(song["energy"], float) and isinstance(song["tempo_bpm"], float) for song in songs)


@pytest.mark.parametrize("energy", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_energy_rejected(energy):
    song = asdict(make_small_recommender().songs[0])
    with pytest.raises(ValueError, match="between 0 and 1"):
        score_song({"genre": "pop", "mood": "happy", "energy": energy}, song)


def test_csv_rejects_invalid_data_with_line_number(tmp_path):
    path = tmp_path / "invalid.csv"
    song = asdict(make_small_recommender().songs[0])
    song["energy"] = 2
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(song))
        writer.writeheader()
        writer.writerow(song)
    with pytest.raises(ValueError, match="line 2"):
        load_songs(path)


def test_k_ties_empty_and_no_mutation():
    song = asdict(make_small_recommender().songs[0])
    songs = [dict(song, id=2), dict(song, id=1)]
    prefs = {"genre": " POP ", "mood": "HAPPY", "energy": 0.8}
    assert [row[0]["id"] for row in recommend_songs(prefs, songs, 99)] == [2, 1]
    assert [item["id"] for item in songs] == [2, 1]
    assert recommend_songs(prefs, songs, 0) == []
    assert recommend_songs(prefs, []) == []
    with pytest.raises(ValueError):
        recommend_songs(prefs, songs, -1)


def test_object_and_dictionary_interfaces_agree():
    rec = make_small_recommender()
    user = UserProfile("lofi", "chill", 0.4, True)
    functional = recommend_songs(asdict(user), [asdict(song) for song in rec.songs])
    assert [song.id for song in rec.recommend(user)] == [row[0]["id"] for row in functional]
    assert rec.explain_recommendation(user, rec.songs[0]) == "; ".join(score_song(asdict(user), asdict(rec.songs[0]))[1])


def test_acoustic_preference_rewards_matching_direction():
    song = asdict(make_small_recommender().songs[0])
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": True}
    assert score_song(prefs, dict(song, acousticness=1.0))[0] == pytest.approx(4.5)
    assert score_song(dict(prefs, likes_acoustic=False), dict(song, acousticness=0.0))[0] == pytest.approx(4.5)


def test_weight_shift_changes_conflicting_profile_winner():
    songs = load_songs(Path(__file__).resolve().parents[1] / "data/songs.csv")
    prefs = {"genre": "pop", "mood": "sad", "energy": 0.9}
    assert recommend_songs(prefs, songs)[0][0]["title"] == "Gym Hero"
    assert recommend_songs(prefs, songs, genre_weight=1.0, energy_weight=2.0)[0][0]["title"] == "Electric Tears"
