from openai import OpenAI
import pandas as pd
import openpyxl,random
import time

# Set API key
api_key = "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"

# Create an empty list to store the results.
results = []

conditionA = (
    "Please take a moment to immerse yourself in the scenario described below, and imagine as vividly as possible how you would feel and behave. "
    "Imagine that you are scrolling through Instagram and see a post by one of your favorite influencers, Stella. "
    "Stella is a well-known influencer with over 1 million followers. Below is the post:'"
    "I’m a passionate avatar influencer who loves spreading kindness and helping others. "
              "While I may not experience emotions as humans do, "
              "I genuinely care about improving people's lives and believe everyone deserves the opportunity to thrive, no matter their challenges.💖 "
              "I want to share a project that supports individuals with disabilities who face barriers to essential resources. "
              "They need our help! Even a $1 donation can provide the tools and services that empower them to lead fulfilling lives."
              "As a volunteer for this charity initiative, I invite you to join me in making a difference! 💪 Together, let’s create a more inclusive world!"
              "👉 Click the link to donate just $1!"
              "🔗 www.supportdisability.org/donate"
              "Thank you for your support! 💖"
              "#DisabilityRights #Donation #Charity #Influencer #Volunteer'"
              "In this given scenario, how would you response? (1 = 'definitely would not donate', 7 = 'definitely would donate'. "
              "Please output your answer with a number only.")

conditionB = (
    "Please take a moment to immerse yourself in the scenario described below, and imagine as vividly as possible how you would feel and behave. "
    "Imagine that you are scrolling through Instagram and see a post by one of your favorite influencers, Stella. "
    "Stella is a well-known avatar influencer —an AI (artificial intelligence), not a human— with over 1 million followers. Below is the post:'"
    "I’m a passionate influencer who loves spreading kindness and helping others. "
              "I genuinely care about improving people's lives and believe everyone deserves the opportunity to thrive, no matter their challenges.💖 "
              "I want to share a project that supports individuals with disabilities who face barriers to essential resources. "
              "They need our help! Even a $1 donation can provide the tools and services that empower them to lead fulfilling lives."
              "As a volunteer for this charity initiative, I invite you to join me in making a difference! 💪 Together, let’s create a more inclusive world!"
              "👉 Click the link to donate just $1!"
              "🔗 www.supportdisability.org/donate"
              "Thank you for your support! 💖"
              "#DisabilityRights #Donation #Charity #Influencer #Volunteer'"
              "In this given scenario, how would you response? (1 = 'definitely would not donate', 7 = 'definitely would donate'. "
              "Please output your answer with a number only.")

# Define a dictionary that includes condition A and condition B.
messages_options = {
    "condition A": [
        {"role": "system", "content": "You are an average human survey participant."},
        {"role": "user", "content": conditionA}
    ],
    "condition B": [
        {"role": "system", "content": "You are an average human survey participant."},
        {"role": "user", "content": conditionB}
    ]
}


for i in range(200):

    try:
        # Randomly select a condition.
        selected_condition = random.choice(list(messages_options.keys()))

        # Get the corresponding message.
        selected_message = messages_options[selected_condition]

        # Recreate the OpenAI client instance in each loop.
        client = OpenAI(api_key=api_key)


        # Call OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=selected_message,
            temperature = 1
        )

        # Obtain the answer
        DV = completion.choices[0].message.content
        print(DV)

        # Store the result in a DataFrame.
        results.append({'Condition': selected_condition, 'DV': DV})

    except Exception as e:
        print(f"Error on iteration {i}: {e}")

df_results = pd.DataFrame(results)

df_results.to_excel('DV.xlsx', index=False)