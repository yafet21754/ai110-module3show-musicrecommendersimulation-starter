# VibeFinder 1.0 — Music Recommender Simulation

## Project Summary

VibeFinder is a CLI-first Python simulation that ranks a catalog of 20 songs against a listener's taste profile. Each result includes its score and the reasons for that score. It is a fixed-rule content-based recommender, with no trained machine-learning model or real listening history.

## How The System Works

Real recommendation systems can use collaborative filtering to find patterns across users' behavior, while content-based filtering compares item attributes to a user's interests. Likes, skips, playlists, and listening histories describe behavior; genre, mood, energy, and tempo describe music. YouTube's published 2016 architecture illustrates two stages: candidate generation followed by ranking. This project uses explicit genre, mood, and energy preferences and scores the entire tiny catalog, so it needs no candidate-generation stage.

Sources: [Google's collaborative-filtering guide](https://developers.google.com/machine-learning/recommendation/collaborative/basics), [Google Research: content-based recommendations](https://research.google/pubs/content-based-related-video-recommendations/), and [YouTube recommendation architecture, 2016](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/). These sources explain concepts; this project does not reproduce a production platform.

### Data and taste profiles

- `Song`: `id`, `title`, `artist`, `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`.
- `UserProfile`: `favorite_genre`, `favorite_mood`, `target_energy`, and `likes_acoustic`.
- The CLI uses dictionaries with `genre`, `mood`, and `energy`. The scorer also accepts the longer UserProfile names. `likes_acoustic` is optional in dictionaries.
- Tempo, valence, and danceability are loaded for future work but do not affect the current score. Acousticness affects it only when `likes_acoustic` is supplied.

The default profile is happy pop with target energy 0.8. Genre plus mood separates intense rock from chill lofi, and target energy distinguishes tracks within those categories. One favorite genre is still a narrow view of taste. Unknown genres receive no genre points; the remaining features still produce a ranking.

### Algorithm Recipe

For each song:

1. Add **2.0** points for an exact genre match (ignoring case and surrounding whitespace).
2. Add **1.0** point for a mood match.
3. Add **1 − abs(song energy − target energy)** points. Closer energy earns more, regardless of whether it is higher or lower.
4. If acoustic preference is supplied, add **0.5 × acousticness** when true or **0.5 × (1 − acousticness)** when false.

The core score ranges from 0 to 4; the optional acoustic contribution raises the maximum to 4.5. It is a relevance score, not a probability. Explanations list the actual contributions.

The scoring rule judges one song. The ranking rule sorts all scored songs from highest to lowest and returns the first k. Ties preserve CSV order. `sorted()` creates a new list; `.sort()` changes a list in place and returns None. The original catalog is not reordered.

Data flow: CSV → typed song dictionaries; user preferences + each song → score and reasons; all scores → descending ranking → top five.

Genre receives the largest weight to prioritize a listener's named style. This choice can hide songs with a better mood match, so the evaluation also tests a less genre-heavy recipe.

## Getting Started

Run commands from the repository root. Python 3.9+ is recommended. The CLI uses only Python's standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

On Windows PowerShell, activate with `.\.venv\Scripts\Activate.ps1`.

Run a single profile or repeat the experiment:

```bash
python -m src.main --profile "High-Energy Pop"
python -m src.main --experiment
python -m pytest -q
```

## Project Structure

| File | Purpose |
| --- | --- |
| `data/songs.csv` | Original 10 songs plus 10 synthetic additions |
| `src/recommender.py` | CSV validation, shared scoring, ranking, and class adapters |
| `src/main.py` | Five profiles and repeatable weight experiment |
| `tests/test_recommender.py` | Starter tests and scoring, validation, and ranking checks |
| `model_card.md` | Data, evaluation, bias, future work, and reflection draft |
| `ai_interactions.md` | Honest record of AI assistance and review still needed |

## Sample Recommendation Output

Actual baseline output from `python -m src.main`:

```text
Loaded songs: 20
Weights: genre=2.0, mood=1.0, energy=1.0

Profile: High-Energy Pop | {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
1. Sunrise City - Score: 3.98
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.98 (+0.98)
2. Gym Hero - Score: 2.87
   Because: genre match (+2.00); energy similarity 0.87 (+0.87)
3. Rooftop Lights - Score: 1.96
   Because: mood match (+1.00); energy similarity 0.96 (+0.96)
4. City Verse - Score: 1.00
   Because: energy similarity 1.00 (+1.00)
5. Desert Steps - Score: 0.95
   Because: energy similarity 0.95 (+0.95)

Profile: Chill Lofi | {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}
1. Library Rain - Score: 4.00
   Because: genre match (+2.00); mood match (+1.00); energy similarity 1.00 (+1.00)
2. Midnight Coding - Score: 3.93
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.93 (+0.93)
3. Focus Flow - Score: 2.95
   Because: genre match (+2.00); energy similarity 0.95 (+0.95)
4. Spacewalk Thoughts - Score: 1.93
   Because: mood match (+1.00); energy similarity 0.93 (+0.93)
5. Coffee Shop Stories - Score: 0.98
   Because: energy similarity 0.98 (+0.98)

Profile: Deep Intense Rock | {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}
1. Storm Runner - Score: 3.99
   Because: genre match (+2.00); mood match (+1.00); energy similarity 0.99 (+0.99)
2. Gym Hero - Score: 1.97
   Because: mood match (+1.00); energy similarity 0.97 (+0.97)
3. Warehouse Dawn - Score: 1.94
   Because: mood match (+1.00); energy similarity 0.94 (+0.94)
4. Electric Tears - Score: 1.00
   Because: energy similarity 1.00 (+1.00)
5. Afterglow Floor - Score: 0.98
   Because: energy similarity 0.98 (+0.98)

Profile: Conflicting Sad Pop | {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
1. Gym Hero - Score: 2.97
   Because: genre match (+2.00); energy similarity 0.97 (+0.97)
2. Sunrise City - Score: 2.92
   Because: genre match (+2.00); energy similarity 0.92 (+0.92)
3. Electric Tears - Score: 2.00
   Because: mood match (+1.00); energy similarity 1.00 (+1.00)
4. Last Train Home - Score: 1.56
   Because: mood match (+1.00); energy similarity 0.56 (+0.56)
5. Blue Porch - Score: 1.40
   Because: mood match (+1.00); energy similarity 0.40 (+0.40)

Profile: Unseen Genre | {'genre': 'opera', 'mood': 'calm', 'energy': 0.0}
1. Quiet Strings - Score: 1.82
   Because: mood match (+1.00); energy similarity 0.82 (+0.82)
2. Spacewalk Thoughts - Score: 0.72
   Because: energy similarity 0.72 (+0.72)
3. Blue Porch - Score: 0.70
   Because: energy similarity 0.70 (+0.70)
4. Library Rain - Score: 0.65
   Because: energy similarity 0.65 (+0.65)
5. Coffee Shop Stories - Score: 0.63
   Because: energy similarity 0.63 (+0.63)
```

## Experiments You Tried

`python -m src.main --experiment` halves genre weight from 2.0 to 1.0 and doubles energy weight from 1.0 to 2.0. Mood stays at 1.0. Optional acoustic weighting is unchanged. Both recipes have the same core maximum of 4.0, and the similarity formula still stays between zero and one.

For happy pop, Rooftop Lights moves above Gym Hero because matching mood and closer energy now beat a genre-only match. For sad pop at energy 0.9, Electric Tears moves from third to first. This better satisfies the stated mood and energy, but no listening ratings establish that it is more accurate. The default recipe remains unchanged; the experiment is an explicit command-line option.

Full experiment output and profile comparisons appear in the [model card](model_card.md).

## Limitations and Risks

The catalog is small and uneven. Genre labels match exactly: pop and indie pop are treated differently. Hand-assigned mood and audio attributes simplify musical taste. Strong genre weighting can create a filter bubble. No lyrics, language, listening context, or behavioral feedback are used, and a sparse genre may have only one matching track.

## Reflection

The implemented comparison shows that the chosen weights change what counts as a good match. Scores and explanations make that decision visible, but they do not prove that a listener will like a song. See the model card for a personal reflection draft that the student should review and adapt before submission.
