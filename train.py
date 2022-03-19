import argparse
import importlib
import traceback

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BentoML Boilerplate Project - Train")

    parser.add_argument(
        "--project", type=str,
        help="project name to be packed"
    )

    args = parser.parse_args()

    try:
        train = importlib.import_module(f"{args.project}.train")
        train.train()
    except:
        traceback.print_exc()
