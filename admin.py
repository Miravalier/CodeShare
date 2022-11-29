#!/usr/bin/env python3
import argparse
import os
import requests
from dotenv import load_dotenv


load_dotenv()


BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create", "list"])
    args = parser.parse_args()

    if args.command == "create":
        create_command()
    elif args.command == "list":
        list_command()


def create_command():
    response = requests.post(BASE_URL + "/create/c", json={
        "admin_token": ADMIN_TOKEN
    })
    print(response.content)


def list_command():
    response = requests.post(BASE_URL + "/list/c", json={
        "admin_token": ADMIN_TOKEN
    })
    print(response.content)


if __name__ == '__main__':
    main()
