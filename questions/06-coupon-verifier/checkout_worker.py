"""Call the candidate's checkout entry point from a separate process."""

import importlib.util
import json
from pathlib import Path
import sys


def main():
    checkout_path = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(checkout_path.parent))
    spec = importlib.util.spec_from_file_location("checkout", checkout_path)
    checkout = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = checkout
    spec.loader.exec_module(checkout)

    request = json.load(sys.stdin)
    json.dump(checkout.checkout_summary(**request), sys.stdout)


if __name__ == "__main__":
    main()
