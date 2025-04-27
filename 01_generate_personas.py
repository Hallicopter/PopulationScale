#!/usr/bin/env python3
"""
Generates richer, blunt-speaker personas.
Run: python generate_personas.py -d "20-28 female NYC" -n 20 -g "GenZ_NY"
"""
import json, uuid, os, random, click, dotenv, openai, re
dotenv.load_dotenv();  openai.api_key = os.getenv("OPENAI_API_KEY")

def jitter(v):                       # ±10 % jitter, clipped
    return max(0, min(1, round(v + random.uniform(-.1, .1), 2)))

@click.command()
@click.option('-d', '--demographic', prompt='Demographic (e.g. 20-28 female NYC)')
@click.option('-n', '--count', type=int, prompt='Number of personas')
@click.option('-g', '--group-name', prompt='Group name')
@click.option('-m', '--model', default='gpt-4o-mini', show_default=True)
@click.option('-o', '--output', help='Output file (JSON)')
def main(demographic, count, group_name, model, output):
    sys_msg = ("You are a data generator.  Output **only** a JSON LIST (no markdown). "
               "Fields for each item: id, name, age, city, short_bio, big5, mood, "
               "values_rank, language_style, recent_event, day_in_life, candor "
               "(0=very guarded, 1=brutally honest).")
    example = """
[
  {
    "id":"a1e5b9",
    "name":"Maya Ortiz",
    "age":23,
    "city":"New York City",
    "short_bio":"UX-designer; salsa dancer; bodega-coffee snob.",
    "big5":{"openness":0.78,"conscientiousness":0.56,"extraversion":0.83,"agreeableness":0.64,"neuroticism":0.32},
    "mood":"hyped after boxing class",
    "values_rank":["friendship","creativity","adventure"],
    "language_style":"Bronx slang with 🎉 emojis and the occasional f-bomb",
    "recent_event":"Bought tickets to Sofar Sounds gig",
    "day_in_life":"6 am boxing → F-train → SoHo coworking → rooftop drinks",
    "candor":0.92
  }
]
"""
    user_msg = (f"{example}\nCreate {count} distinct personas that fit: {demographic}. "
                "Keep ages within range; vary candor widely (0.3-1.0).")

    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role":"system","content":sys_msg},
                  {"role":"user","content":user_msg}],
        response_format={"type":"json_object"}
    )
    raw = re.sub(r"^```(?:json)?|```$", "", resp.choices[0].message.content.strip(), flags=re.MULTILINE)
    personas = json.loads(raw)

    # Normalise whatever shape the model returns
    if isinstance(personas, str):
        # Sometimes the whole list comes back as a JSON string
        personas = json.loads(personas)

    if isinstance(personas, dict):
        # Wrapped in an object like {"personas":[...] } or {"data":[...]}
        personas = personas.get("personas") or personas.get("data") or list(personas.values())[0]

    if isinstance(personas, list):
        cleaned = []
        for item in personas:
            if isinstance(item, str):
                try:
                    cleaned.append(json.loads(item))
                except json.JSONDecodeError:
                    # If it isn't valid JSON, skip it
                    continue
            else:
                cleaned.append(item)
        personas = cleaned

    # final touches
    for p in personas:
        p["id"] = p.get("id") or uuid.uuid4().hex[:6]
        p["big5"] = {k: jitter(v) for k, v in p["big5"].items()}

    out = {"group_name": group_name, "demographic": demographic, "personas": personas}
    fn  = output or f"personas_{uuid.uuid4().hex[:6]}.json"
    json.dump(out, open(fn,"w"), indent=2);  click.echo(f"Saved ➜ {fn}")

if __name__ == "__main__":
    main()