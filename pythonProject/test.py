"""Script for generating participant responses using a language model.

This project originally relied on the ``openai`` Python package.  The
environment used for assessment does not have that dependency installed,
which caused an import error and prevented the script from running.  To
make the project executable without the OpenAI SDK, the script now uses
`litellm` – a lightweight, drop‑in replacement that provides a similar
`completion` interface while supporting multiple backends.

In addition, a small bug in ``generate_participant_details`` returned the
entire list of social‑sensitivity options rather than a single randomly
selected string.  That has been corrected so that each participant has a
single social‑sensitivity value.
"""

from litellm import completion
import os
import pandas as pd
import openpyxl
import random
import time
from datetime import datetime
from pathlib import Path


def load_env():
    """Load environment variables from a .env file if present."""
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        with env_path.open() as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key, value)


# Load .env variables and read the API key
load_env()
api_key = os.getenv("LITELLM_API_KEY")
if not api_key:
    raise RuntimeError("LITELLM_API_KEY not set. Create a .env file or export the variable before running.")

# To switch providers, set their API key in the environment and supply the
# provider-prefixed model name (e.g., "anthropic/claude-3-haiku") when calling
# ``completion`` below.

# Function to generate random participant details
def generate_participant_details():
    age = random.randint(18, 65)
    sex = random.choice(["male", "female"])
    culture_background = random.choice(["Caucasian", "African", "Asian", "Latino", "Middle Eastern", "Indigenous", "Mixed"])
    socialSensitivity = random.choice(["very low", "low", "moderate", "high", "very high"])
    mood = random.choice(["happy", "sad", "angry", "anxious", "excited", "calm", "bored", "confused", "frustrated",
                          "hopeful", "relaxed", "nervous", "grateful", "jealous", "content"])
    return age, sex, culture_background, socialSensitivity, mood

# Function to load conditions from external text files
def load_condition(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Path helper to allow running this script from any directory
BASE_DIR = Path(__file__).resolve().parent

# Load conditions A and B from text files located alongside the script
conditionA = load_condition(BASE_DIR / 'conditionA.txt')
conditionB = load_condition(BASE_DIR / 'conditionB.txt')

# Define a dictionary that includes condition A and condition B
messages_options = {
    "condition A": lambda: [
        generate_participant_details(),
        # Few-shot examples to guide the response pattern
        {"role": "system", "content": "You are a human living in the US. You are {} years old, {} gender,"
                                      " with {} cultural background. You social sensitivity is {}."
                                      "Today you are feeling {}.".format(*generate_participant_details())},
        {"role": "user", "content": conditionA},
        # Prompting to generate thoughts before the final response (thought-process breakdown)
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {"role": "user", "content": "Now, based on your thoughts, what is your final answer? Output your rating only please."}
    ],
    "condition B": lambda: [
        generate_participant_details(),
        # Few-shot examples to guide the response pattern
        {"role": "system", "content": "You are a human living in the US. You are {} years old, {} gender,"
                                      " with {} cultural background. You social sensitivity is {}. "
                                      "Today you are feeling {}.".format(*generate_participant_details())},
        {"role": "user", "content": conditionB},
        # Prompting to generate thoughts before the final response (thought-process breakdown)
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {"role": "user", "content": "Now, based on your thoughts, what is your final answer? Output your rating only please."}
    ]
}

# Create an empty list to store the results
results = []

for i in range(200):
    try:
        # Randomly select a condition (either A or B)
        selected_condition_key = random.choice(["condition A", "condition B"])

        # Get the corresponding message by calling the lambda function
        participant_details, *selected_message = messages_options[selected_condition_key]()
        age, sex, culture_background, name, mood = participant_details

        # Call the model API via liteLLM to generate a response
        completion_response = completion(
            model="gpt-4o-mini",
            messages=selected_message,
            api_key=api_key,
            temperature=random.uniform(1.0, 1.5),
            top_p=random.uniform(0.85, 1.0),
        )

        # Obtain the answer from the API response
        DV = completion_response["choices"][0]["message"]["content"].strip()
        print(DV)

        # Store the result in a list, including participant details and the dependent variable (DV)
        results.append({'Condition': selected_condition_key, 'DV': DV, 'Age': age, 'Sex': sex, 'Culture Background': culture_background, 'Mood': mood, 'Name': name})

        # Optional: Add a delay to avoid hitting rate limits
        time.sleep(random.uniform(0.5, 1.5))

    except Exception as e:
        # Print an error message if something goes wrong during the iteration
        print(f"Error on iteration {i}: {e}")

# Save the results to an Excel file with a timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
df_results = pd.DataFrame(results, columns=['Condition', 'DV', 'Age', 'Sex', 'Culture Background', 'Mood', 'Name'])
df_results.to_excel(f'DV_{timestamp}.xlsx', index=False)
