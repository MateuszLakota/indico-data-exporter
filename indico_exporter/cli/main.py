import argparse

from indico_exporter.logging.logger import setup_logging
from indico_exporter.services.submission_service import export_submissions
from indico_exporter.services.workflow_service import export_workflow


def main():
    setup_logging()

    #export_workflow(2)
    export_submissions(list(range(300, 323)))

    # parser = argparse.ArgumentParser()
    #
    # subparsers = parser.add_subparsers(dest="command")
    #
    # workflow_parser = subparsers.add_parser("workflow")
    # workflow_parser.add_argument("--id", type=int, required=True)
    #
    # submission_parser = subparsers.add_parser("submission")
    # submission_parser.add_argument(
    #     "--ids",
    #     type=int,
    #     nargs="+",
    #     required=True,
    #     help="List of submission IDs"
    # )
    #
    # args = parser.parse_args()

    # if args.command == "workflow":
    #     export_workflow(args.id)
    #
    # if args.command == "submission":
    #     export_submissions(args.ids)


if __name__ == "__main__":
    main()
