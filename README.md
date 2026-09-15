# N1-Inspired Japanese Practice System

An unofficial personal learning application inspired by JLPT N1 study topics. This local Flask and SQLite application provides timed practice sessions and section-based exercises; it is not an official JLPT product or exam simulator and is not affiliated with the Japan Foundation or JEES.

## Features

- A 71-question, 110-minute practice-session workflow
- Section-based vocabulary, grammar, and reading exercises
- Automatic scoring and per-question review
- Local result and history persistence
- Browser-side session-state recovery
- Keyboard navigation: left/right arrows to move and `1`–`4` to select an answer
- Category-constrained question selection for practice sessions

## Question Bank

The question bank contains synthetic and AI-assisted practice content. Questions are hand-organized and template-generated to support vocabulary, grammar, and reading practice.

The content is not copied from official JLPT exam papers, is not an official JLPT question set, and is not intended to reproduce official question wording, difficulty calibration, or exam composition.

## Scoring Disclaimer

Scores are internal practice scores based on correct answers. They are not official JLPT scores, official pass/fail decisions, score predictions, or official difficulty calibration. The application does not include a listening section equivalent to the complete JLPT exam.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python / Flask |
| Database | SQLite |
| Front end | Jinja2 / Vanilla JavaScript / CSS |

## Installation and Usage

```bash
pip install flask
python seed_questions.py
python app.py
```

Then open `http://localhost:5000` in a browser.

## Practice Session Structure

| Exercise type | Questions |
| --- | ---: |
| Kanji reading (漢字読み) | 6 |
| Contextual meaning (文脈規定) | 7 |
| Paraphrase (言い換え) | 6 |
| Usage (用法) | 6 |
| Grammar form (文法形式) | 10 |
| Sentence ordering (文章組合) | 5 |
| Grammar in context (文章文法) | 5 |
| Reading: short texts to information retrieval (読解) | 26 |
