import argparse
import os
import sys
import requests


def main():
    parser = argparse.ArgumentParser(description="OpenVoice /clone client")
    parser.add_argument("--url", default="http://localhost:8811/clone", help="Clone endpoint URL")
    parser.add_argument("--ref", required=True, help="Path to reference audio (wav/mp3)")
    parser.add_argument("--out", default="output.wav", help="Output wav path")
    parser.add_argument("--text", default="Hello from OpenVoice", help="Synthesis text")
    parser.add_argument("--language", default="EN_NEWEST", help="Language key (e.g. EN_NEWEST, EN, ES, FR, ZH, JP, KR)")
    parser.add_argument("--speed", default="1.0", help="Speech speed (string or float)")
    parser.add_argument("--speaker", default=None, help="Optional base speaker key")
    args = parser.parse_args()

    if not os.path.exists(args.ref):
        print(f"Reference file not found: {args.ref}", file=sys.stderr)
        sys.exit(2)

    data = {
        "text": args.text,
        "language": args.language,
        "speed": str(args.speed),
    }
    if args.speaker:
        data["speaker"] = args.speaker

    with open(args.ref, "rb") as f:
        files = {"reference_audio": (os.path.basename(args.ref), f, "application/octet-stream")}
        r = requests.post(args.url, data=data, files=files, timeout=600)

    if r.status_code != 200:
        print(f"Request failed: {r.status_code}\n{r.text}", file=sys.stderr)
        sys.exit(1)

    with open(args.out, "wb") as out:
        out.write(r.content)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
