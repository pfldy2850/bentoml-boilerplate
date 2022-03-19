import argparse
import importlib
import traceback

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BentoML Boilerplate Project - Packer")

    parser.add_argument(
        "--project", type=str,
        help="project name to be packed"
    )

    args = parser.parse_args()

    try:
        packer = importlib.import_module(f"{args.project}.packer")
        saved_path = packer.pack()
        print(f"saved_path={saved_path}")
    except:
        traceback.print_exc()
