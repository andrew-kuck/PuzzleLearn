import json
import requests
import re
import random


def generate_question_with_ollama(columns, sample_rows):
    prompt = f"""
You are generating one SQL practice question for students.

The browser uses AlaSQL, similar to SQLite, against one table named nba.

Table name:
nba

Columns:
{json.dumps(columns, indent=2)}

Sample rows:
{json.dumps(sample_rows[:5], indent=2)}

Rules:
1. Return JSON only.
2. The JSON must have exactly these keys: "question" and "sql".
3. The question should ask for a subset or summary of the data.
4. The SQL must correctly answer the question.
5. Use the table name nba.
6. Put every column name in square brackets, for example [Player], [Points], [3_Pointers_Made].
7. Numeric-looking columns are available as numbers in the browser.
8. Do not use SQL features that AlaSQL is unlikely to support.
9. Avoid rounding unless the question explicitly asks for rounded values.
10. Include ORDER BY when returning multiple rows, so results are deterministic.
11. Do not include markdown.
12. Do not include explanations.

Good examples:
{{
  "question": "Return the distinct opponents against which LeBron James scored more than 20 points.",
  "sql": "SELECT DISTINCT [Opponent] FROM nba WHERE [Player] = 'LeBron James' AND [Points] > 20 ORDER BY [Opponent]"
}}

{{
  "question": "Return the average number of offensive rebounds for players on LAL.",
  "sql": "SELECT AVG([Offensive_Rebounds]) AS avg_offensive_rebounds FROM nba WHERE [Team] = 'LAL'"
}}

Now generate one new question.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8
            }
        },
        timeout=30
    )

    response.raise_for_status()

    text = response.json()["response"].strip()

    # Robustly extract the JSON object if the model accidentally adds text.
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in LLM response.")

    data = json.loads(match.group(0))

    question = data.get("question")
    sql = data.get("sql")

    if not question or not sql:
        raise ValueError("LLM response missing question or sql.")

    return {
        "question": question,
        "sql": sql
    }


def generate_fallback_question(sample_rows):
    if not sample_rows:
        return {
            "question": "Return all players who scored more than 20 points, ordered by points from highest to lowest.",
            "sql": "SELECT [Player], [Points] FROM nba WHERE [Points] > 20 ORDER BY [Points] DESC"
        }

    row = random.choice(sample_rows)

    player = sql_escape(row.get("Player", "LeBron James"))
    team = sql_escape(row.get("Team", "LAL"))

    templates = [
        {
            "question": f"Return the distinct opponents against which {player} scored more than 20 points.",
            "sql": f"SELECT DISTINCT [Opponent] FROM nba WHERE [Player] = '{player}' AND [Points] > 20 ORDER BY [Opponent]"
        },
        {
            "question": f"Return the average number of offensive rebounds for players on {team}.",
            "sql": f"SELECT AVG([Offensive_Rebounds]) AS avg_offensive_rebounds FROM nba WHERE [Team] = '{team}'"
        },
        {
            "question": f"Return all games for {player} where they had at least 5 assists, ordered by game date.",
            "sql": f"SELECT [GameDate], [Opponent], [Assists] FROM nba WHERE [Player] = '{player}' AND [Assists] >= 5 ORDER BY [GameDate]"
        },
        {
            "question": f"Return the total points scored by players on {team}.",
            "sql": f"SELECT SUM([Points]) AS total_points FROM nba WHERE [Team] = '{team}'"
        }
    ]

    return random.choice(templates)


def sql_escape(value):
    return str(value).replace("'", "''")

