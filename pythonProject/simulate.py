"""Simulate experimental participants using a language model.

This script uses the `litellm` package to generate responses that mimic
human participants under different experimental conditions. It can be run
as a command-line tool where the number of synthetic participants and other
parameters are configurable.
"""

from __future__ import annotations

import argparse
import base64
import json
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


def load_profile_config(path: Path | None) -> tuple[dict, dict[str, str]]:
    """Load demographic options and trait descriptions from JSON.

    The JSON file may contain two top-level objects:

    ``demographics``: a mapping of demographic fields to the choices the
        script will randomly sample from (e.g., ``{"sex": ["male", "female"]}``).
    ``characteristics``: a mapping of trait names to a short explanation of the
        1–7 scale (e.g., ``{"extraversion": "1=low,7=high"}``).
    """

    if path is None:
        path = BASE_DIR / "profile_config.json"
    if not path.exists():
        return {}, {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    demographics = data.get("demographics", {})
    traits = data.get("characteristics", {})
    return demographics, traits


def generate_participant_details(
    demographics_options: dict | None = None,
    traits: dict[str, str] | None = None,
) -> tuple[dict, dict[str, int]]:
    """Return random demographic and trait information."""

    demographics_options = demographics_options or {}
    age_range = tuple(demographics_options.get("age_range", (18, 65)))
    age = random.randint(*age_range)
    sex = random.choice(demographics_options.get("sex", ["male", "female"]))
    culture_background = random.choice(
        demographics_options.get(
            "culture_background",
            [
                "Caucasian",
                "African",
                "Asian",
                "Latino",
                "Middle Eastern",
                "Indigenous",
                "Mixed",
            ],
        )
    )

    demographics = {
        "Age": age,
        "Sex": sex,
        "Culture Background": culture_background,
    }

    trait_names = traits.keys() if traits else [
        "extraversion",
        "agreeableness",
        "conscientiousness",
        "neuroticism",
        "openness",
    ]
    characteristics = {trait: random.randint(1, 7) for trait in trait_names}
    return demographics, characteristics


def load_condition(file_path: Path) -> list[dict]:
    """Return message parts for a condition, supporting text and images."""

    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        text = file_path.read_text(encoding="utf-8").strip()
        return [{"type": "text", "text": text}]
    if suffix in {".png", ".jpg", ".jpeg", ".gif"}:
        with file_path.open("rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        mime = "jpeg" if suffix in {".jpg", ".jpeg"} else suffix.lstrip(".")
        url = f"data:image/{mime};base64,{b64}"
        return [{"type": "image_url", "image_url": {"url": url}}]
    raise ValueError(f"Unsupported condition file type: {file_path}")


def build_messages(
    condition_content: list[dict],
    demographics_options: dict | None = None,
    traits: dict[str, str] | None = None,
) -> tuple[list[dict], dict[str, int]]:
    """Create messages for the language model and participant metadata."""

    demographics, characteristics = generate_participant_details(
        demographics_options, traits
    )
    system_prompt = (
        "You are a human living in the US. You are {age} years old, {sex} gender, "
        "with {culture} cultural background.".format(
            age=demographics["Age"],
            sex=demographics["Sex"],
            culture=demographics["Culture Background"],
        )
    )
    for trait, value in characteristics.items():
        meaning = (
            traits.get(trait, "1=very low, 7=very high") if traits else "1=very low, 7=very high"
        )
        system_prompt += f" Your {trait} is {value} ({meaning})."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": condition_content},
        {"role": "user", "content": "Think carefully about what kind of person you are."},
        {
            "role": "user",
            "content": (
                "Now, based on your thoughts, what is your final answer? "
                "Output your rating only please."
            ),
        },
    ]
    metadata = {**demographics, **{trait.title(): val for trait, val in characteristics.items()}}
    return messages, metadata


# ---------------------------------------------------------------------------
# Simulation logic
# ---------------------------------------------------------------------------


def simulate_participants(
    count: int,
    model: str,
    output: Path | None = None,
    profile_config: Path | None = None,
) -> Path:
    """Run the simulation and save results to an Excel file.

    Parameters
    ----------
    count:
        Number of participants to generate.
    model:
        Model identifier understood by `litellm`.
    output:
        Optional path to the Excel file. If omitted, a timestamped file is
        created in the current directory.
    profile_config:
        Optional JSON file describing demographic choices and trait descriptions.

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
    demo_options, trait_defs = load_profile_config(profile_config)

    condition_a = load_condition(BASE_DIR / "conditionA.txt")
    condition_b = load_condition(BASE_DIR / "conditionB.txt")

    results: list[dict] = []
    for i in range(count):
        try:
            condition_key = random.choice(["condition A", "condition B"])
            condition_content = (
                condition_a if condition_key == "condition A" else condition_b
            )
            messages, metadata = build_messages(
                condition_content, demo_options, trait_defs
            )

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
    parser.add_argument(
        "--profile-config",
        type=Path,
        default=BASE_DIR / "profile_config.json",
        help="JSON file with demographic options and trait descriptions",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = simulate_participants(
        args.participants, args.model, args.output, args.profile_config
    )
    print(f"Results saved to {path}")


if __name__ == "__main__":  # pragma: no cover - direct execution
    main()

