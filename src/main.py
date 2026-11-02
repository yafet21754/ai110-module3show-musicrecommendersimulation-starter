"""Run reproducible profile evaluations and an optional weight experiment."""

import argparse
from pathlib import Path

from .recommender import load_songs, recommend_songs

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    "Conflicting Sad Pop": {"genre": "pop", "mood": "sad", "energy": 0.9},
    "Unseen Genre": {"genre": "opera", "mood": "calm", "energy": 0.0},
}


def main() -> None:
    """Print top-five recommendations with scores and explanations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, help="Run just one profile")
    parser.add_argument("--experiment", action="store_true", help="Halve genre weight and double energy weight")
    args = parser.parse_args()
    songs = load_songs(Path(__file__).resolve().parents[1] / "data" / "songs.csv")
    weights = {"genre_weight": 1.0, "energy_weight": 2.0} if args.experiment else {}
    print(f"Loaded songs: {len(songs)}")
    print("Weights: genre=1.0, mood=1.0, energy=2.0" if args.experiment else "Weights: genre=2.0, mood=1.0, energy=1.0")
    selected = {args.profile: PROFILES[args.profile]} if args.profile else PROFILES
    for name, prefs in selected.items():
        print(f"\nProfile: {name} | {prefs}")
        for rank, (song, score, reason) in enumerate(recommend_songs(prefs, songs, k=5, **weights), 1):
            print(f"{rank}. {song['title']} - Score: {score:.2f}")
            print(f"   Because: {reason}")


if __name__ == "__main__":
    main()
