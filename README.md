# Population Scale Persona & Survey Toolkit

This project provides a toolkit for generating synthetic personas based on demographic descriptions, surveying these personas on a given topic using the OpenAI API, and visualizing the results through a web interface.

## Features

*   **Persona Generation (`01_generate_personas.py`)**: Creates detailed personas with attributes like name, age, city, bio, Big Five personality traits, mood, values, language style, and candor level.
*   **Survey Execution (`02_run_survey.py`)**: Surveys the generated personas with a specific question, leveraging the OpenAI API to generate realistic, context-aware responses based on each persona's profile. Supports self-consistency checks and reflection steps for higher quality answers.
*   **Web Visualization (`app.py`)**: A Flask web application that allows you to browse and view the survey results. It lists available opinion files and displays each persona's response alongside their details.

## Project Structure

```
population_scale/
├── .gitignore             # Specifies intentionally untracked files that Git should ignore
├── 01_generate_personas.py # Script to generate personas
├── 02_run_survey.py        # Script to run surveys on personas
├── 03_visualize.py       # (Legacy) Original terminal visualization script
├── app.py                  # Flask web application for visualization
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates for the Flask app
│   ├── index.html
│   └── view_opinions.html
├── .env                    # (Needs to be created by user) Stores API keys
├── personas_*.json         # Generated persona files (ignored by git)
└── opinions_*.json         # Generated opinion files (ignored by git)
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Hallicopter/PopulationScale.git
    cd PopulationScale
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Create a file named `.env` in the project root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY='your_openai_api_key_here'
    ```

## Usage

**1. Generate Personas:**

*   Run the script and follow the prompts:
    ```bash
    python 01_generate_personas.py
    ```
*   Or specify options directly:
    ```bash
    python 01_generate_personas.py -d "30-40 male tech workers SF" -n 15 -g "TechSF30s"
    ```
    This will create a `personas_*.json` file.

**2. Run Survey:**

*   Run the script, providing the path to a persona file, and follow the prompts:
    ```bash
    python 02_run_survey.py personas_abcdef.json
    ```
*   Or specify options directly:
    ```bash
    python 02_run_survey.py personas_abcdef.json -q "What are your thoughts on remote work?" -sc 3 --reflect
    ```
    This will create an `opinions_*.json` file.

**3. Visualize Results:**

*   Start the Flask web server:
    ```bash
    python app.py
    ```
*   Open your web browser and navigate to `http://127.0.0.1:5001`.
*   The homepage will list all `opinions_*.json` files in the directory. Click on a file to view the detailed responses for that survey.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source (consider adding a specific license file like MIT or Apache 2.0).
