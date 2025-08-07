#!/usr/bin/env python3
"""Quick setup script for GPT Participants Simulator.

This script helps users configure their environment and test API connections.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional
import subprocess

try:
    from dotenv import load_dotenv, set_key
    import requests
    from litellm import completion
except ImportError:
    print("Installing required dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed. Please run the script again.")
    sys.exit(0)


class SetupWizard:
    """Interactive setup wizard for the simulator."""

    def __init__(self):
        self.base_dir = Path(__file__).parent / "pythonProject"
        self.env_file = self.base_dir / ".env"
        self.config_file = self.base_dir / "profile_config.json"

    def run(self):
        """Run the setup wizard."""
        print("=" * 60)
        print("🚀 GPT Participants Simulator - Setup Wizard")
        print("=" * 60)

        # Step 1: Check existing configuration
        if self.env_file.exists():
            print("\n⚠️  Existing .env file found.")
            overwrite = input("Do you want to reconfigure? (y/n): ").lower()
            if overwrite != 'y':
                print("Keeping existing configuration.")
                self.test_configuration()
                return

        # Step 2: Configure API keys
        print("\n📝 Step 1: Configure API Keys")
        print("-" * 40)
        self.configure_api_keys()

        # Step 3: Configure profile
        print("\n📝 Step 2: Configure Participant Profile")
        print("-" * 40)
        self.configure_profile()

        # Step 4: Test configuration
        print("\n🧪 Step 3: Test Configuration")
        print("-" * 40)
        self.test_configuration()

        print("\n✅ Setup complete! You can now run:")
        print("   python pythonProject/gui.py        # For GUI")
        print("   python pythonProject/simulate.py   # For CLI")

    def configure_api_keys(self):
        """Configure API keys interactively."""
        providers = {
            "1": ("OpenAI", "LITELLM_API_KEY", "sk-"),
            "2": ("GitHub Models", "GITHUB_TOKEN", "ghp_"),
            "3": ("Anthropic", "ANTHROPIC_API_KEY", "sk-ant-"),
            "4": ("Google", "GOOGLE_API_KEY", ""),
            "5": ("Both OpenAI and GitHub", None, None)
        }

        print("\nWhich provider(s) do you want to use?")
        for key, (name, _, _) in providers.items():
            if key != "5":
                print(f"  {key}. {name}")
            else:
                print(f"  {key}. {name}")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "5":
            # Configure both OpenAI and GitHub
            self._save_api_key("LITELLM_API_KEY", "sk-", "OpenAI")
            self._save_api_key("GITHUB_TOKEN", "ghp_", "GitHub")
        elif choice in providers:
            name, key_name, prefix = providers[choice]
            if key_name:
                self._save_api_key(key_name, prefix, name)
        else:
            print("Invalid choice. Using default (OpenAI).")
            self._save_api_key("LITELLM_API_KEY", "sk-", "OpenAI")

    def _save_api_key(self, key_name: str, prefix: str, provider_name: str):
        """Save an API key to the .env file."""
        print(f"\nConfiguring {provider_name}:")

        if provider_name == "GitHub":
            print("  Get your token from: https://github.com/settings/tokens")
            print("  Required scopes: repo, read:packages")
        elif provider_name == "OpenAI":
            print("  Get your API key from: https://platform.openai.com/api-keys")

        api_key = input(f"Enter your {provider_name} API key: ").strip()

        if not api_key:
            print(f"  ⚠️  No key provided for {provider_name}")
            return

        if prefix and not api_key.startswith(prefix):
            print(f"  ⚠️  Warning: {provider_name} keys usually start with '{prefix}'")

        # Create .env file if it doesn't exist
        if not self.env_file.exists():
            self.env_file.touch()

        set_key(str(self.env_file), key_name, api_key)
        print(f"  ✅ {provider_name} API key saved")

    def configure_profile(self):
        """Configure participant profile settings."""
        print("\nDo you want to use default participant profile settings?")
        print("  (Age: 18-65, Sex: male/female, Big Five personality traits)")

        use_default = input("Use defaults? (y/n): ").lower()

        if use_default == 'y':
            self._create_default_profile()
        else:
            self._create_custom_profile()

    def _create_default_profile(self):
        """Create default profile configuration."""
        default_config = {
            "demographics": {
                "age_range": [18, 65],
                "sex": ["male", "female"],
                "culture_background": [
                    "Caucasian", "African", "Asian", "Latino",
                    "Middle Eastern", "Indigenous", "Mixed"
                ]
            },
            "characteristics": {
                "extraversion": "1=very introverted, 7=very extraverted",
                "agreeableness": "1=very disagreeable, 7=very agreeable",
                "conscientiousness": "1=very disorganized, 7=very organized",
                "neuroticism": "1=very calm, 7=very anxious",
                "openness": "1=very traditional, 7=very open-minded"
            }
        }

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)

        print("  ✅ Default profile configuration created")

    def _create_custom_profile(self):
        """Create custom profile configuration interactively."""
        config = {"demographics": {}, "characteristics": {}}

        # Age range
        print("\nAge range configuration:")
        min_age = input("  Minimum age (default 18): ").strip() or "18"
        max_age = input("  Maximum age (default 65): ").strip() or "65"
        config["demographics"]["age_range"] = [int(min_age), int(max_age)]

        # Sex options
        print("\nSex options (comma-separated):")
        sex_input = input("  Options (default: male,female): ").strip()
        sex_options = sex_input.split(",") if sex_input else ["male", "female"]
        config["demographics"]["sex"] = [s.strip() for s in sex_options]

        # Culture background
        print("\nCulture background options (comma-separated):")
        print("  Default: Caucasian,African,Asian,Latino,Middle Eastern,Indigenous,Mixed")
        culture_input = input("  Options (press Enter for default): ").strip()
        if culture_input:
            config["demographics"]["culture_background"] = [
                c.strip() for c in culture_input.split(",")
            ]
        else:
            config["demographics"]["culture_background"] = [
                "Caucasian", "African", "Asian", "Latino",
                "Middle Eastern", "Indigenous", "Mixed"
            ]

        # Personality traits
        print("\nPersonality traits to measure:")
        print("  Default: Big Five (extraversion, agreeableness, etc.)")
        use_big_five = input("  Use Big Five? (y/n): ").lower()

        if use_big_five == 'y':
            config["characteristics"] = {
                "extraversion": "1=very introverted, 7=very extraverted",
                "agreeableness": "1=very disagreeable, 7=very agreeable",
                "conscientiousness": "1=very disorganized, 7=very organized",
                "neuroticism": "1=very calm, 7=very anxious",
                "openness": "1=very traditional, 7=very open-minded"
            }
        else:
            print("\nEnter custom traits (one per line, empty line to finish):")
            print("Format: trait_name:description")
            while True:
                trait_input = input("  > ").strip()
                if not trait_input:
                    break
                if ':' in trait_input:
                    name, desc = trait_input.split(':', 1)
                    config["characteristics"][name.strip()] = desc.strip()
                else:
                    config["characteristics"][trait_input] = "1=very low, 7=very high"

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print("  ✅ Custom profile configuration created")

    def test_configuration(self):
        """Test the configuration by making a simple API call."""
        print("\nTesting configuration...")

        # Load environment variables
        load_dotenv(self.env_file)

        # Test available APIs
        tested_any = False

        # Test OpenAI/LiteLLM
        if os.getenv("LITELLM_API_KEY"):
            print("\n  Testing OpenAI connection...")
            if self._test_litellm("gpt-4o-mini"):
                print("    ✅ OpenAI connection successful")
                tested_any = True
            else:
                print("    ❌ OpenAI connection failed")

        # Test GitHub Models
        if os.getenv("GITHUB_TOKEN"):
            print("\n  Testing GitHub Models connection...")
            if self._test_github_models():
                print("    ✅ GitHub Models connection successful")
                tested_any = True
            else:
                print("    ❌ GitHub Models connection failed")

        if not tested_any:
            print("\n  ⚠️  No API keys configured or tests failed")
            print("  Please check your configuration and try again")
        else:
            print("\n  🎉 Configuration test complete!")

    def _test_litellm(self, model: str) -> bool:
        """Test LiteLLM connection."""
        try:
            response = completion(
                model=model,
                messages=[{"role": "user", "content": "Say 'test successful' only"}],
                max_tokens=10,
                api_key=os.getenv("LITELLM_API_KEY")
            )
            return "success" in response["choices"][0]["message"]["content"].lower()
        except Exception as e:
            print(f"      Error: {e}")
            return False

    def _test_github_models(self) -> bool:
        """Test GitHub Models connection."""
        try:
            # Test with a simple API call
            token = os.getenv("GITHUB_TOKEN")
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            # Test GitHub API access
            response = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"}
            )

            if response.status_code == 200:
                username = response.json().get("login", "Unknown")
                print(f"      Connected as: {username}")
                return True
            else:
                print(f"      HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"      Error: {e}")
            return False


def main():
    """Run the setup wizard."""
    wizard = SetupWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()