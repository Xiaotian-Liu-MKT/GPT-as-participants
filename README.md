# GPT-as-participants

This repository contains a small utility for generating synthetic
"participants" for psychology or social‑science experiments using a
language model.  The script wraps the [`litellm`](https://github.com/BerriAI/litellm)
package so you can plug in different model providers while keeping a
consistent API.

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Provide an API key**

   Copy `pythonProject/.env.example` to `pythonProject/.env` and fill in
your `LITELLM_API_KEY` (for example an OpenAI key).  The script reads this
file automatically.

3. **Edit experimental conditions**

   The prompts presented to the simulated participants live in
   `pythonProject/conditionA.txt` and `pythonProject/conditionB.txt`.
   Adjust them to match your experiment.

## Usage

Run the simulator from the repository root:

```bash
python pythonProject/simulate.py --participants 50 --model gpt-4o-mini
```

Command‑line options:

- `--participants` / `-n` – number of synthetic participants (default 200).
- `--model` / `-m` – model name understood by `litellm`.
- `--output` / `-o` – optional path to save the Excel file (default uses a
timestamped name).

The script saves an Excel spreadsheet containing the condition, model
output, and generated participant metadata.
