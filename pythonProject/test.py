from openai import OpenAI
import pandas as pd
import openpyxl
import random
import time
from datetime import datetime

# Set API key
api_key = "sk-your_api_key"

# Function to generate random participant details
def generate_participant_details():
    age = random.randint(18, 65)
    sex = random.choice(["male", "female", "non-binary"])
    culture_background = random.choice(["urban", "rural", "suburban", "immigrant"])
    name = random.choice(["Alex", "Jordan", "Taylor", "Morgan", "Riley", "Casey", "Cameron", "Avery"])
    mood = random.choice(["happy", "frustrated", "optimistic", "nervous", "thoughtful"])
    return age, sex, culture_background, name, mood

# Function to load conditions from external text files
def load_condition(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()

# Load conditions A and B from text files
conditionA = load_condition('conditionA.txt')
conditionB = load_condition('conditionB.txt')

# Define a dictionary that includes condition A and condition B
messages_options = {
    "condition A": lambda: [
        generate_participant_details(),
        # Few-shot examples to guide the response pattern
        {"role": "system", "content": "You are a human living in the US. You are {} years old, {} gender, with {} cultural background, named {}. Today you are feeling {}.".format(*generate_participant_details())},
        {"role": "user", "content": conditionA},
        # Prompting to generate thoughts before the final response (thought-process breakdown)
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {"role": "user", "content": "Now, based on your thoughts, what is your final answer?"}
    ],
    "condition B": lambda: [
        generate_participant_details(),
        # Few-shot examples to guide the response pattern
        {"role": "system", "content": "You are a human living in the US. You are {} years old, {} gender, with {} cultural background, named {}. Today you are feeling {}.".format(*generate_participant_details())},
        {"role": "user", "content": conditionB},
        # Prompting to generate thoughts before the final response (thought-process breakdown)
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {"role": "user", "content": "Now, based on your thoughts, what is your final answer?"}
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

        # Recreate OpenAI client instance in each loop (required for independent API calls)
        client = OpenAI(api_key=api_key)

        # Call OpenAI API to generate a response based on the selected message
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=selected_message,
            temperature=random.uniform(1.0, 1.5),  # Temperature setting controls randomness of the response
            top_p=random.uniform(0.85, 1.0)  # Top-p sampling to increase diversity
        )

        # Obtain the answer from the API response
        DV = completion.choices[0].message.content.strip()
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
