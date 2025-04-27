#!/usr/bin/env python3
import json
import click
import os

@click.command()
@click.argument('opinions_file', type=click.Path(exists=True))
def visualize(opinions_file):
    """Visualizes the survey opinions linked to their personas."""
    with open(opinions_file, 'r') as f:
        data = json.load(f)

    question = data.get("question", "N/A")
    answers = data.get("answers", [])
    persona_file_path = data.get("persona_file")

    if not persona_file_path or not os.path.exists(persona_file_path):
        click.echo(f"Error: Persona file path '{persona_file_path}' not found or not specified in {opinions_file}")
        # Fallback or alternative display if personas can't be loaded?
        # For now, just show replies without full persona details.
        click.echo(f"\n--- Question ---\n{question}")
        click.echo("\n--- Raw Replies ---")
        for answer in answers:
            click.echo(f"- {answer.get('name', 'Unknown')}: {answer.get('reply', 'No reply')}")
        return

    # Load personas
    with open(persona_file_path, 'r') as f:
        personas_data = json.load(f)
        
        personas_list = None # Initialize
        if isinstance(personas_data, list):
            # Case 1: The file root is directly the list of personas
            personas_list = personas_data
        elif isinstance(personas_data, dict):
            if 'personas' in personas_data and isinstance(personas_data['personas'], list):
                # Case 2: The file root is a dict containing a 'personas' key with the list
                personas_list = personas_data['personas']
            else:
                if 'personas' in personas_data:
                    pass
        else:
            pass

        # Check if personas_list was successfully assigned
        if personas_list is None:
            click.echo(f"Error: Could not find a list of personas in {persona_file_path}. Expected a list or a dict with a 'personas' key.")
            return # Or handle differently

        personas_map = {p['id']: p for p in personas_list if isinstance(p, dict) and 'id' in p}


    click.echo(f"""
--- Survey Results from {opinions_file} ---
Based on personas from: {persona_file_path}

--- Question ---
{question}
""")
    click.echo("\n--- Responses ---")

    for i, answer in enumerate(answers):
        persona_id = answer.get('id')
        persona = personas_map.get(persona_id)

        click.echo(f"\n--- Persona {i+1}/{len(answers)} ---")
        if persona:
            click.echo(f"  Name: {persona.get('name', 'N/A')}")
            click.echo(f"  Age: {persona.get('age', 'N/A')}")
            click.echo(f"  City: {persona.get('city', 'N/A')}")
            click.echo(f"  Bio: {persona.get('short_bio', 'N/A')}")
            big5 = persona.get('big5', {})
            if big5:
                click.echo(f"  Big5 Traits:")
                for trait, score in big5.items():
                    click.echo(f"    - {trait.capitalize()}: {score}")
            else:
                click.echo("  Big5 Traits: N/A")
            click.echo(f"\n  Reply: {answer.get('reply', 'No reply')}")
        else:
            click.echo(f"  Persona Details (ID: {persona_id}): Not found in {persona_file_path}")
            click.echo(f"  Reply: {answer.get('reply', 'No reply')}")
        click.echo("--------------------")

if __name__ == '__main__':
    visualize()
