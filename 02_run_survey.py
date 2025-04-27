#!/usr/bin/env python3
"""
Surveys personas with high-variety, blunt answers.
"""
import os, json, asyncio, uuid, statistics, click
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from openai import AsyncOpenAI

load_dotenv();  aclient = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@click.command()
@click.argument('persona_file', type=click.Path(exists=True))
@click.option('-q','--question', prompt='Stimulus / question')
@click.option('-m','--model', default='gpt-4o-mini', show_default=True)
@click.option('-t','--temperature', default=1.1, show_default=True)
@click.option('--sc', default=2, show_default=True,
              help='Drafts per persona (soft self-consistency)')
@click.option('--reflect/--no-reflect', default=True, show_default=True,
              help='Reflection pass at T=0.3 for authenticity check')
@click.option('-o','--output', default=None)
def main(persona_file, question, model, temperature, sc, reflect, output):
    personas = json.load(open(persona_file))["personas"]

    SYS = ("You are {name}, {age}, {city}. Mood: {mood}. Values: {values}. "
           "Candor={candor}. Language style: {style}. Big-Five: {big5}. "
           "Speak as if venting to a close friend in private. Mild profanity is fine. "
           "Do not mention being an AI.  Be brutally honest; no hedging.")

    async def draft_once(p):
        sys = SYS.format(
            name=p['name'], age=p['age'], city=p['city'], mood=p.get('mood',''),
            values=', '.join(p.get('values_rank',[])), style=p.get('language_style',''),
            candor=p.get('candor',1.0), big5=p['big5'])
        r = await aclient.chat.completions.create(
                model=model, temperature=temperature,
                messages=[{"role":"system","content":sys},
                          {"role":"user","content":question}])
        return r.choices[0].message.content.strip()

    async def ask(p):
        drafts = [await draft_once(p) for _ in range(sc)]
        if sc > 1:
            chosen = max(drafts, key=lambda x: statistics.stdev([ord(c) for c in x]))
        else:
            chosen = drafts[0]

        if reflect:
            refl = ("Does your answer truly match your mood, values, and candor level? "
                    "If not, rewrite it.  Keep it raw.  Return only the final text.")
            r = await aclient.chat.completions.create(
                    model=model, temperature=0.3,
                    messages=[{"role":"system","content":SYS.format(
                                name=p['name'], age=p['age'], city=p['city'],
                                mood=p.get('mood',''), values=', '.join(p.get('values_rank',[])),
                                style=p.get('language_style',''), candor=p.get('candor',1.0),
                                big5=p['big5'])},
                              {"role":"user","content":f"Prev reply:\n{chosen}\n\n{refl}"}])
            chosen = r.choices[0].message.content.strip()

        return {"id":p['id'], "name":p['name'], "reply":chosen}

    async def run_all():
        bar = tqdm(total=len(personas), desc="Survey")
        results = []
        tasks = [asyncio.create_task(ask(p)) for p in personas]
        for coro in asyncio.as_completed(tasks):
            results.append(await coro); bar.update(1)
        bar.close()
        fn = output or f"opinions_{uuid.uuid4().hex[:6]}.json"
        json.dump({"persona_file": persona_file, "question": question,
                   "answers": results}, open(fn,"w"), indent=2)
        click.echo(f"Saved ➜ {fn}")

    asyncio.run(run_all())

if __name__ == "__main__":
    main()