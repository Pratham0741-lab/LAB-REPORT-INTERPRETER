# frontend.py
import sys
import requests
import json


BACKEND_URL = "http://127.0.0.1:8000/analyze_report"


def main():
    if len(sys.argv) < 2:
        print("Usage: python frontend.py path/to/report.pdf")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        files = {"file": (path, f, "application/octet-stream")}
        print(f"Sending {path} to backend at {BACKEND_URL} ...")
        resp = requests.post(BACKEND_URL, files=files, timeout=120)

    if not resp.ok:
        print("Error:", resp.status_code, resp.text)
        sys.exit(1)

    data = resp.json()
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
