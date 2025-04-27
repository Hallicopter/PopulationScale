#!/usr/bin/env python3
import json
import os
import glob
from flask import Flask, render_template, abort

app = Flask(__name__)

DATA_DIR = "."

@app.route('/')
def index():
    """Lists available opinion files."""
    opinion_files = []
    try:
        # Find opinion files in the current directory
        for filepath in glob.glob(os.path.join(DATA_DIR, 'opinions_*.json')):
            filename = os.path.basename(filepath)
            opinion_files.append(filename)
        opinion_files.sort(reverse=True) # Show newest first
    except Exception as e:
        print(f"Error finding opinion files: {e}") 
        # Handle error appropriately, maybe show an error message on the page
        pass 
        
    return render_template('index.html', opinion_files=opinion_files)

@app.route('/view/<filename>')
def view_opinions(filename):
    """Displays the details of a specific opinion file."""
    opinions_filepath = os.path.join(DATA_DIR, filename)

    if not filename.startswith('opinions_') or not filename.endswith('.json') or not os.path.exists(opinions_filepath):
        abort(404, description="Opinion file not found or invalid.")

    try:
        with open(opinions_filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        abort(500, description=f"Error reading opinion file: {e}")

    question = data.get("question", "N/A")
    answers = data.get("answers", [])
    persona_file_path_relative = data.get("persona_file")

    personas_map = {}
    persona_file_error = None
    full_persona_file_path = None

    if persona_file_path_relative:
        full_persona_file_path = os.path.join(DATA_DIR, persona_file_path_relative)
        if os.path.exists(full_persona_file_path):
            try:
                with open(full_persona_file_path, 'r') as f:
                    personas_data = json.load(f)
                    personas_list = None
                    if isinstance(personas_data, list):
                        personas_list = personas_data
                    elif isinstance(personas_data, dict) and 'personas' in personas_data and isinstance(personas_data['personas'], list):
                        personas_list = personas_data['personas']
                    
                    if personas_list is not None:
                        personas_map = {p['id']: p for p in personas_list if isinstance(p, dict) and 'id' in p}
                    else:
                         persona_file_error = f"Could not find a list of personas within {persona_file_path_relative}."
            except Exception as e:
                persona_file_error = f"Error reading persona file {persona_file_path_relative}: {e}"
        else:
            persona_file_error = f"Persona file '{persona_file_path_relative}' not found."
    else:
        persona_file_error = "Persona file path not specified in the opinions file."

    # Combine answers with persona details
    results = []
    for answer in answers:
        persona_id = answer.get('id')
        persona_details = personas_map.get(persona_id)
        results.append({
            'persona': persona_details, # This will be None if not found
            'reply': answer.get('reply', 'No reply provided.')
        })

    return render_template('view_opinions.html', 
                           question=question, 
                           results=results,
                           opinions_filename=filename,
                           persona_filename=persona_file_path_relative,
                           persona_file_error=persona_file_error)

if __name__ == '__main__':
    # Make sure debug=False in production
    app.run(debug=True, port=5001)
