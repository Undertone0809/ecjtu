import argparse

from ecjtu.server import start_api_server


def main():
    """start the api server from the command line

    Usage:
        python ecjtu.server.py --port 8000

    """
    parser = argparse.ArgumentParser(description="ECJTU Command Line Interface")
    parser.add_argument(
        "--port", type=int, default=8080, help="Port to run the server on"
    )

    args = parser.parse_args()

    start_api_server(args.port)


if __name__ == "__main__":
    main()
