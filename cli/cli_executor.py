"""
CLI executor implementation for running external LLM executables.
"""

import subprocess
from typing import Optional
from .interfaces import ExecutorInterface


class CLIExecutor(ExecutorInterface):
    """Handles execution of CLI-based LLM executable."""
    
    def __init__(self, exe_path: str = "./genie_bundle/genie-t2t-run.exe", 
                 config_file: str = "genie_bundle/genie_config.json", 
                 cwd: Optional[str] = None):
        self.exe_path = exe_path
        self.config_file = config_file
        self.cwd = cwd
    
    def execute(self, prompt: str) -> str:
        """Execute the CLI command with the given prompt."""
        print("Calling LLM with prompt:")
        print(prompt)

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
            return result.stdout

        except FileNotFoundError:
            raise FileNotFoundError(f"Executable not found at {self.exe_path}")

        except subprocess.CalledProcessError as e:
            # Return stdout even on failure for potential response extraction
            if e.stdout:
                return e.stdout
            raise RuntimeError(
                f"Command failed with exit code {e.returncode}\n"
                f"stdout:\n{e.stdout}\nstderr:\n{e.stderr}"
            )