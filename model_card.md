# Model Card: VibeFinder 1.0

## 1. Model Name

VibeFinder 1.0.

## 2. Intended Use and Goal / Task

Suggest and explain the top five songs for an explicit taste profile. This is a classroom simulation for learning about features, scoring, ranking, and bias. It assumes the supplied preferences describe the listener's current interests. It is not intended for production personalization, psychological judgments, or claims about listener satisfaction.

## 3. How the Model Works / Algorithm Summary

Every song earns two points for matching genre and one for matching mood. It also earns up to one point for energy closeness. Optional acoustic preference contributes up to half a point. The system sorts the songs by total score and returns the highest results with explanations. Both the class interface and dictionary interface call the same scoring function. The weights are chosen by design, not learned from data.

## 4. Data Used

The CSV contains 20 illustrative tracks: the 10 starter records are preserved and 10 AI-generated fictional tracks were added. The added genres are afrobeat, classical, folk, techno, reggae, hip hop, rnb, country, house, and hyperpop. Titles, artists, and numerical attributes are synthetic teaching data, not verified real recordings or measured audio features. No personal listening data is collected.

Features include identifiers, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. All normalized numerical attributes are validated in the range zero to one; tempo must be positive. Only genre, mood, energy, and optionally acousticness influence the score.

Genre counts: afrobeat: 1, ambient: 1, classical: 1, country: 1, folk: 1, hip hop: 1, house: 1, hyperpop: 1, indie pop: 1, jazz: 1, lofi: 3, pop: 2, reggae: 1, rnb: 1, rock: 1, synthwave: 1, techno: 1.

## 5. Strengths

The leading results align with the stated feature preferences: Sunrise City leads happy pop, Library Rain leads chill lofi, and Storm Runner leads intense rock. Library Rain receives the full core score of 4.00 because all three scored features match. Sunrise City's 3.98 consists of 2.00 genre points, 1.00 mood point, and 0.98 energy points. This is a feature-based plausibility check, not a claim that the synthetic songs sound right to a listener.

## 6. Limitations and Bias

Genre weighting can keep listeners inside a filter bubble: Gym Hero outranks a sad track for the sad-pop profile even though its mood is intense. The catalog is uneven, with three lofi songs but only one rock song and no opera, giving some tastes more matching choices. Exact labels miss relationships such as pop versus indie pop and chill versus relaxed. Synthetic energy and mood values omit lyrics, language, culture, and changing listening context. Catalog-order tie breaking gives earlier entries a small exposure advantage, and there is no ground truth from real listeners to establish accuracy.

## 7. Evaluation Process and Observed Behavior

The baseline was run with five profiles, always returning the top five with reasons. The README contains the exact baseline terminal output. Three core profiles test distinct styles, while sad pop with high energy tests conflicting preferences and opera at energy zero tests an unseen genre and a boundary energy value. Recommendations are deterministic and make no network calls.

### All pairwise profile comparisons

| Profile pair | Output difference and explanation |
| --- | --- |
| High-Energy Pop / Chill Lofi | Sunrise City versus Library Rain leads; genre and mood switch, and energy drops from 0.8 to 0.35. Their top-five lists share no tracks. |
| High-Energy Pop / Deep Intense Rock | Sunrise City versus Storm Runner leads; rock and intense preferences replace pop and happy. Gym Hero appears in both lists because it matches pop in one and intense mood in the other. |
| Chill Lofi / Deep Intense Rock | Library Rain versus Storm Runner leads; low-energy chill tracks give way to high-energy intense tracks. Their top-five lists share no tracks. |
| High-Energy Pop / Conflicting Sad Pop | The leader changes from Sunrise City to Gym Hero because target energy rises; neither pop track is sad, yet their genre bonuses beat Electric Tears. |
| High-Energy Pop / Unseen Genre | Sunrise City gives way to Quiet Strings; opera has no matches, so calm mood and low energy control the result. |
| Chill Lofi / Conflicting Sad Pop | Library Rain gives way to Gym Hero as genre, mood, and target energy all change. Their top-five lists share no tracks. |
| Chill Lofi / Unseen Genre | Library Rain falls from first to fourth while Quiet Strings becomes first; there is no opera bonus and the target moves toward zero energy and calm mood. |
| Deep Intense Rock / Conflicting Sad Pop | Storm Runner gives way to Gym Hero; both target 0.9 energy, but genre and mood bonuses change. Electric Tears appears in both because its energy is exactly 0.9. |
| Deep Intense Rock / Unseen Genre | High-energy intense tracks give way to calm, low-energy tracks; their top-five lists share no tracks. |
| Conflicting Sad Pop / Unseen Genre | Gym Hero gives way to Quiet Strings. Blue Porch remains in both lists because it matches sad mood in one and low energy in the other. |

### Weight-shift experiment

Genre was halved to 1.0 and energy doubled to 2.0; mood stayed at 1.0. The experiment is isolated behind a CLI flag so it is repeatable without editing source code.

| Profile | Baseline leader | Experiment leader | Observation |
| --- | --- | --- | --- |
| High-Energy Pop | Sunrise City | Sunrise City | 2 of five rank positions changed |
| Chill Lofi | Library Rain | Library Rain | 0 of five rank positions changed |
| Deep Intense Rock | Storm Runner | Storm Runner | 0 of five rank positions changed |
| Conflicting Sad Pop | Gym Hero | Electric Tears | 4 of five rank positions changed |
| Unseen Genre | Quiet Strings | Quiet Strings | 0 of five rank positions changed |

The surprise is that high-energy sad music exists in the catalog, but the default genre bonus still pushes the sad hyperpop track below two non-sad pop tracks. The experiment brings Electric Tears to first and swaps Rooftop Lights ahead of Gym Hero for happy pop. This supports the design claim that less genre weight allows stronger mood-and-energy alternatives. It does not establish improved prediction accuracy without listener feedback or ground truth labels.

Actual terminal output from `python -m src.main --experiment`:

```text
Loaded songs: 20
Weights: genre=1.0, mood=1.0, energy=2.0

Profile: High-Energy Pop | {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
1. Sunrise City - Score: 3.96
   Because: genre match (+1.00); mood match (+1.00); energy similarity 0.98 (+1.96)
2. Rooftop Lights - Score: 2.92
   Because: mood match (+1.00); energy similarity 0.96 (+1.92)
3. Gym Hero - Score: 2.74
   Because: genre match (+1.00); energy similarity 0.87 (+1.74)
4. City Verse - Score: 2.00
   Because: energy similarity 1.00 (+2.00)
5. Desert Steps - Score: 1.90
   Because: energy similarity 0.95 (+1.90)

Profile: Chill Lofi | {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}
1. Library Rain - Score: 4.00
   Because: genre match (+1.00); mood match (+1.00); energy similarity 1.00 (+2.00)
2. Midnight Coding - Score: 3.86
   Because: genre match (+1.00); mood match (+1.00); energy similarity 0.93 (+1.86)
3. Focus Flow - Score: 2.90
   Because: genre match (+1.00); energy similarity 0.95 (+1.90)
4. Spacewalk Thoughts - Score: 2.86
   Because: mood match (+1.00); energy similarity 0.93 (+1.86)
5. Coffee Shop Stories - Score: 1.96
   Because: energy similarity 0.98 (+1.96)

Profile: Deep Intense Rock | {'genre': 'rock', 'mood': 'intense', 'energy': 0.9}
1. Storm Runner - Score: 3.98
   Because: genre match (+1.00); mood match (+1.00); energy similarity 0.99 (+1.98)
2. Gym Hero - Score: 2.94
   Because: mood match (+1.00); energy similarity 0.97 (+1.94)
3. Warehouse Dawn - Score: 2.88
   Because: mood match (+1.00); energy similarity 0.94 (+1.88)
4. Electric Tears - Score: 2.00
   Because: energy similarity 1.00 (+2.00)
5. Afterglow Floor - Score: 1.96
   Because: energy similarity 0.98 (+1.96)

Profile: Conflicting Sad Pop | {'genre': 'pop', 'mood': 'sad', 'energy': 0.9}
1. Electric Tears - Score: 3.00
   Because: mood match (+1.00); energy similarity 1.00 (+2.00)
2. Gym Hero - Score: 2.94
   Because: genre match (+1.00); energy similarity 0.97 (+1.94)
3. Sunrise City - Score: 2.84
   Because: genre match (+1.00); energy similarity 0.92 (+1.84)
4. Last Train Home - Score: 2.12
   Because: mood match (+1.00); energy similarity 0.56 (+1.12)
5. Storm Runner - Score: 1.98
   Because: energy similarity 0.99 (+1.98)

Profile: Unseen Genre | {'genre': 'opera', 'mood': 'calm', 'energy': 0.0}
1. Quiet Strings - Score: 2.64
   Because: mood match (+1.00); energy similarity 0.82 (+1.64)
2. Spacewalk Thoughts - Score: 1.44
   Because: energy similarity 0.72 (+1.44)
3. Blue Porch - Score: 1.40
   Because: energy similarity 0.70 (+1.40)
4. Library Rain - Score: 1.30
   Because: energy similarity 0.65 (+1.30)
5. Coffee Shop Stories - Score: 1.26
   Because: energy similarity 0.63 (+1.26)
```

### Automated checks

Validation result: **14 tests passed** with `python -m pytest -q`.

The tests cover the original object interface, exact score arithmetic and explanations, energy closeness, CSV numeric conversion and validation, invalid target energy, top-k boundaries, empty catalogs, stable ties, unchanged input ordering, agreement between both interfaces, acoustic weighting, and the experiment's changed winner. Run them with `python -m pytest -q`.

## 8. Ideas for Improvement

1. Collect a larger, balanced catalog and listener ratings to evaluate satisfaction against real ground truth.
2. Support multiple preferred genres and graded mood similarity, plus tempo and danceability targets.
3. Add an explicit diversity or exploration step so the same genres and artists do not dominate every list.

## 9. Personal Reflection — Draft for Student Review

The following is an AI-assisted draft based on the implemented results. Review and adapt it to your actual understanding and experience before submission.

The biggest lesson from this project is that a recommendation depends on what the scoring rule rewards. The sad-pop experiment demonstrates that a large genre bonus can outweigh a better mood match. Even a small algorithm can produce recommendations that seem personalized because different profiles change which song features earn points.

AI helped implement the shared scoring function, expand the fictional dataset, and document repeatable experiments. The results still needed checks: the explanations had to agree with the score, numerical values needed validation, and the class and dictionary interfaces had to rank consistently. A possible next step is to collect real listener feedback and add a diversity rule. That would help test whether the recommendations are useful rather than just mathematically consistent.
