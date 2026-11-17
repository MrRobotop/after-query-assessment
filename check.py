"""Run the assessment's executable checks from any working directory."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
CHECKS = (
    ("Median candidates", "-m", "unittest", "discover", "-s", "questions/01-median", "-v"),
    ("Inventory verifier", "questions/04-reward-hacking/inventory_demo.py"),
    ("Order total caching", "questions/05-cache-consistency/cache_demo.py"),
    ("Coupon verifier", "questions/06-coupon-verifier/verify.py", "--demo"),
)


def main():
    for label, *arguments in CHECKS:
        print(f"\n{label}", flush=True)
        result = subprocess.run([sys.executable, "-B", *arguments], cwd=ROOT)
        if result.returncode:
            return result.returncode
    print("\nAll assessment checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
