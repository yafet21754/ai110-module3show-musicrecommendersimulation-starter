# AI Assistance Record

## Agentic Workflow

The student supplied the assignment instructions and repository, then asked: “yes build it” with the GitHub repository link. ChatGPT inspected the starter, implemented the project, generated ten synthetic songs, ran the CLI for five profiles and a weight experiment, and prepared documentation and automated checks.

Files changed: `src/recommender.py`, `src/main.py`, `src/__init__.py`, `data/songs.csv`, `tests/test_recommender.py`, `README.md`, `model_card.md`, `requirements.txt`, and this log.

The implementation keeps both starter interfaces and shares one scoring rule. It fixes the package import for `python -m src.main`. The experiment halves genre weight and doubles energy weight without changing the baseline.

## Verification and Human Review

The agent checked actual terminal output, score calculations, interface consistency, and the automated test suite. These are agent-run checks, not claims that the student manually tested or listened to the fictional tracks. The student should run the project, inspect explanations, and revise the personal reflection to match their actual experience. No separate student chat sessions or manual review are claimed.

## Design Choice

The existing Recommender class adapts Song and UserProfile objects to the functional scoring API. This avoids duplicated formulas. No additional design-pattern stretch credit is claimed.
