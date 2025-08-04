"""Simulate experimental participants using a language model.

This script uses the `litellm` package to generate responses that mimic
human participants under different experimental conditions.  It can be run
as a command‑line tool where the number of synthetic participants and other
parameters are configurable.
"""

from __future__ import annotations

import argparse
import os
import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from litellm import completion

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


def generate_participant_details() -> tuple[int, str, str, str, str]:
    """Return random demographic information for a synthetic participant."""
    age = random.randint(18, 65)
    sex = random.choice(["male", "female"])
    culture_background = random.choice(
        [
            "Caucasian",
            "African",
            "Asian",
            "Latino",
            "Middle Eastern",
            "Indigenous",
            "Mixed",
        ]
    )
    social_sensitivity = random.choice(
        ["very low", "low", "moderate", "high", "very high"]
    )
    mood = random.choice(
        [
            "happy",
            "sad",
            "angry",
            "anxious",
            "excited",
            "calm",
            "bored",
            "confused",
            "frustrated",
            "hopeful",
            "relaxed",
            "nervous",
            "grateful",
            "jealous",
            "content",
        ]
    )
    return age, sex, culture_background, social_sensitivity, mood


def load_condition(file_path: Path) -> str:
    """Return the contents of a text file used as an experimental condition."""
    with file_path.open("r", encoding="utf-8") as fh:
        return fh.read().strip()


def build_messages(condition_text: str) -> tuple[list[dict], dict]:
    """Create messages for the language model and participant metadata."""
    age, sex, culture_background, social_sensitivity, mood = (
        generate_participant_details()
    )
    system_prompt = (
        "You are a human living in the US. You are {} years old, {} gender, "
        "with {} cultural background. You social sensitivity is {}. Today you are "
        "feeling {}."
    ).format(age, sex, culture_background, social_sensitivity, mood)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": condition_text},
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {
            "role": "user",
            "content": (
                "Now, based on your thoughts, what is your final answer? "
                "Output your rating only please."
            ),
        },
    ]
    metadata = {
        "Age": age,
        "Sex": sex,
        "Culture Background": culture_background,
        "Social Sensitivity": social_sensitivity,
        "Mood": mood,
    }
    return messages, metadata


# ---------------------------------------------------------------------------
# Simulation logic
# ---------------------------------------------------------------------------


def simulate_participants(
    count: int,
    model: str,
    output: Path | None = None,
) -> Path:
    """Run the simulation and save results to an Excel file.

    Parameters
    ----------
    count:
        Number of participants to generate.
    model:
        Model identifier understood by `litellm`.
    output:
        Optional path to the Excel file.  If omitted, a timestamped file is
        created in the current directory.
    Returns
    -------
    Path
        The path to the saved results file.
    """

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("LITELLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LITELLM_API_KEY not set. Create a .env file or export the variable before running."
        )

    condition_a = load_condition(BASE_DIR / "conditionA.txt")
    condition_b = load_condition(BASE_DIR / "conditionB.txt")

    results: list[dict] = []
    for i in range(count):
        try:
            condition_key = random.choice(["condition A", "condition B"])
            condition_text = condition_a if condition_key == "condition A" else condition_b
            messages, metadata = build_messages(condition_text)

            response = completion(
                model=model,
                messages=messages,
                api_key=api_key,
                temperature=random.uniform(1.0, 1.5),
                top_p=random.uniform(0.85, 1.0),
            )
            dv = response["choices"][0]["message"]["content"].strip()
            metadata.update({"Condition": condition_key, "DV": dv})
            results.append(metadata)
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as exc:  # pragma: no cover - used for resilience
            print(f"Error on iteration {i}: {exc}")

    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = Path.cwd() / f"DV_{timestamp}.xlsx"

    df = pd.DataFrame(results)
    df.to_excel(output, index=False)
    return output


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n",
        "--participants",
        type=int,
        default=200,
        help="number of synthetic participants to generate (default: 200)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="gpt-4o-mini",
        help="model to use via litellm (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="optional path to save the Excel results",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = simulate_participants(args.participants, args.model, args.output)
    print(f"Results saved to {path}")


if __name__ == "__main__":  # pragma: no cover - direct execution
    main()
