# worker.py
import os
import argparse
import asyncio

from stream2whisper import Stream2Whisper

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream-url", required=True)
    parser.add_argument("--language", default="en")
    parser.add_argument("--api-key", default="")
    return parser.parse_args()

async def main():
    args = parse_args()

    # Make sure it's set in environment
    api_key = os.environ["OPENAI_API_KEY"]

    app = Stream2Whisper(api_key)

    await app.run(
        stream_url=args.stream_url,
        language=args.language,
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt", flush=True)