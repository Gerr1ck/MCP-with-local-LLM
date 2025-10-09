import re
import subprocess
from typing import Optional


class LLMClient:
    """Simple wrapper to call a local LLM executable.

    Usage contract (minimal):
    - Inputs: user_message (either full tagged message or plain user content)
    - Output: stdout returned by the executable (string)
    - Errors: raises FileNotFoundError if executable missing; RuntimeError on non-zero exit
    """

    def __init__(self, exe_path: str = "./genie_bundle/genie-t2t-run.exe", config_file: str = "genie_bundle/genie_config.json", cwd: Optional[str] = None):
        self.exe_path = exe_path
        self.config_file = config_file
        # If you need to run with a specific working directory, pass cwd (e.g. "genie_bundle")
        self.cwd = cwd

    def _build_prompt(self, user_message: str) -> str:
        """Return a full prompt string. If the incoming user_message already contains
        the tag '<|user|>' we assume it's already formatted and return it unchanged.
        Otherwise we wrap it with the system and user tags used by the backend.
        """
        if "<|user|>" in user_message:
            return user_message

        return (
            "<|system|>\nYou are a helpful assistant. Be helpful but brief.<|end|>\n"
            f"<|user|>{user_message}\n<|end|>\n"
            "<|assistant|>\n"
        )

    def ask(self, user_message: str) -> str:
        """Send the prompt to the executable and return stdout.

        Example: client.ask("Whats the capital of France?")
                 or client.ask("<|user|>Whats the capital of France?\n<|end|>\n")
        """
        prompt = self._build_prompt(user_message)

        command = [
            self.exe_path,
            "-c",
            self.config_file,
            "-p",
            prompt,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.cwd,
            )

            stdout_text = result.stdout

            # Look for the content between '[BEGIN]:' and '[END]'
            m = re.search(r"\[BEGIN\]:\s*(.*?)\[END\]", stdout_text, re.DOTALL)
            if m:
                # Return trimmed inner text
                return m.group(1).strip()

            # If markers not found, return empty string to avoid returning the whole stdout.
            return ""

        except FileNotFoundError:
            raise FileNotFoundError(f"Executable not found at {self.exe_path}")

        except subprocess.CalledProcessError as e:
            # Even in failure, try to extract the marked response from stdout if present
            stdout_text = e.stdout or ""
            m = re.search(r"\[BEGIN\]:\s*(.*?)\[END\]", stdout_text, re.DOTALL)
            if m:
                return m.group(1).strip()

            raise RuntimeError(f"Command failed with exit code {e.returncode}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}")


if __name__ == "__main__":
    client = LLMClient()

    # Example: pass either the full tagged prompt or just the plain user content.
    example_prompt = "<|user|>Whats the capital of France?\n<|end|>\n"

    print("Running example prompt...")
    try:
        response = client.ask(example_prompt)
        print("\n--- Response ---")
        print(response)
    except Exception as exc:
        print("Error:", exc)
