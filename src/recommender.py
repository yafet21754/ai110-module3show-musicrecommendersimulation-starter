"""Explainable, content-based music recommendations using fixed weights."""

import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Song:
    """Store song metadata and normalized audio attributes."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Store a listener's genre, mood, energy, and acoustic preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _unit_value(value, name: str) -> float:
    """Validate a finite numerical feature on the zero-to-one scale."""
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return number


def load_songs(csv_path: str) -> List[Dict]:
    """Read and validate CSV songs, converting numerical fields to numbers."""
    songs = []
    ids = set()
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        required = set(Song.__dataclass_fields__)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV is missing required song columns")
        for line, row in enumerate(reader, start=2):
            try:
                song = {key: row[key].strip() for key in required}
                song["id"] = int(song["id"])
                if song["id"] in ids:
                    raise ValueError("duplicate song id")
                for field in ("title", "artist", "genre", "mood"):
                    if not song[field]:
                        raise ValueError(f"{field} cannot be blank")
                for field in ("energy", "valence", "danceability", "acousticness"):
                    song[field] = _unit_value(song[field], field)
                song["tempo_bpm"] = float(song["tempo_bpm"])
                if not math.isfinite(song["tempo_bpm"]) or song["tempo_bpm"] <= 0:
                    raise ValueError("tempo_bpm must be finite and positive")
                ids.add(song["id"])
                songs.append(song)
            except (ValueError, TypeError, AttributeError) as error:
                raise ValueError(f"Invalid song on CSV line {line}: {error}") from error
    return songs


def score_song(user_prefs: Dict, song: Dict, *, genre_weight: float = 2.0,
               mood_weight: float = 1.0, energy_weight: float = 1.0) -> Tuple[float, List[str]]:
    """Return a weighted match score and the contributions that explain it."""
    for weight in (genre_weight, mood_weight, energy_weight):
        if not math.isfinite(weight) or weight < 0:
            raise ValueError("Weights must be finite and non-negative")
    genre = user_prefs.get("genre", user_prefs.get("favorite_genre", ""))
    mood = user_prefs.get("mood", user_prefs.get("favorite_mood", ""))
    target = _unit_value(user_prefs.get("energy", user_prefs.get("target_energy")), "target energy")
    energy = _unit_value(song["energy"], "song energy")
    score = 0.0
    reasons = []
    for name, preference, weight in (("genre", genre, genre_weight), ("mood", mood, mood_weight)):
        if not isinstance(preference, str) or not preference.strip():
            raise ValueError(f"User {name} must be a non-empty string")
        if preference.strip().casefold() == song[name].strip().casefold():
            score += weight
            reasons.append(f"{name} match (+{weight:.2f})")
    similarity = 1.0 - abs(energy - target)
    contribution = energy_weight * similarity
    score += contribution
    reasons.append(f"energy similarity {similarity:.2f} (+{contribution:.2f})")
    # Optional acoustic preference adds at most 0.5 points; omitted profiles get no bonus.
    if "likes_acoustic" in user_prefs:
        likes_acoustic = user_prefs["likes_acoustic"]
        if not isinstance(likes_acoustic, bool):
            raise ValueError("likes_acoustic must be a boolean")
        acousticness = _unit_value(song["acousticness"], "acousticness")
        similarity = acousticness if likes_acoustic else 1.0 - acousticness
        contribution = 0.5 * similarity
        score += contribution
        reasons.append(f"acoustic preference (+{contribution:.2f})")
    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, **weights) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the highest k, preserving catalog order on ties."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError("k must be a non-negative integer")
    ranked = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, **weights)
        ranked.append((song, score, "; ".join(reasons)))
    return sorted(ranked, key=lambda item: item[1], reverse=True)[:k]


class Recommender:
    """Adapt the shared functional scoring logic to Song and UserProfile objects."""

    def __init__(self, songs: List[Song]):
        """Keep a separate catalog list without modifying the caller's list."""
        self.songs = list(songs)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return Song objects in descending score order."""
        results = recommend_songs(asdict(user), [asdict(song) for song in self.songs], k)
        return [Song(**song) for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain a recommendation using exactly the same scoring function."""
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)
