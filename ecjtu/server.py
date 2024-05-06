import argparse
from ecjtu_api.api import start_api_server

def main():
    parser = argparse.ArgumentParser(description="ECJTU Command Line Interface")
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')

    args = parser.parse_args()

    start_api_server(args.port)

if __name__ == "__main__":
    main()