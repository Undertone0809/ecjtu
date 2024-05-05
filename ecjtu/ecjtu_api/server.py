#TODO

import argparse
from ecjtu.client import ECJTU

def main():
    parser = argparse.ArgumentParser(description="ECJTU Command Line Interface")
    parser.add_argument('--stud_id', required=True, help='Student ID')
    parser.add_argument('--pwd', required=True, help='Password')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')

    args = parser.parse_args()

    client = ECJTU(stud_id=args.stud_id, password=args.pwd)
    client.start_api_server(port=args.port)

if __name__ == "__main__":
    main()