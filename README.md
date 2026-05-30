Disclaimer: This software is provided for educational and research purposes only. Users are solely responsible for ensuring their use complies with all relevant rules and regulations.

### install & use
```bash
pip install -r requirements.txt
```

```python
import asyncio
from stream2whisper import Stream2Whisper

OPENAI_API_KEY = "your-api-key-here"
app = Stream2Whisper(OPENAI_API_KEY)
asyncio.run(app.run(stream_url="https://www.youtube.com/@Markets/live", language="en"))
```

For flexibility and transcribing multiple streams, use the [worker.py](worker.py) multiprocess approach.

```bash
export OPENAI_API_KEY="your-key-here";
python3 worker.py --stream-url https://www.youtube.com/@TheBurntPeanut/live
python3 worker.py --stream-url https://www.youtube.com/@YahooFinance/live --language en
python3 worker.py --stream-url https://www.youtube.com/@Halktvkanali/live --language tr
```

Save the transcription outputs to files
```bash
python3 worker.py --stream-url https://www.youtube.com/@Markets/live >> markets.txt # appends
python3 worker.py --stream-url https://www.youtube.com/@Markets/live >> log.txt 2>&1 # combine stdout and stderr
```

You can monitor the stdout, the file you wrote to or `event.delta` in the code (edit [stream2whisper.py](stream2whisper.py))

### what is stream2whisper?
it is a lightweight, high level yet low latency Python implementation that uses yt-dlp, ffmpeg and OpenAI `gpt-realtime-whisper` model for getting transcriptions of livestreams on [supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) such as YouTube, Twitch, Kick and more.

### requirements
- internet connection
- `OPENAI_API_KEY`
- `python3.11+`


### why?

this is for lightweight, high level use cases without bothering with CUDA, ML libraries, all the different whisper engines, audio libraries and whatnot.

To self host whisper yourself, see [openai/whisper](https://github.com/openai/whisper) and [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp). If you do not have CUDA GPUs, there are CPU and Mac alternatives of course. For example, on Apple Silicon M1+ Macs, [mlx-whisper](https://pypi.org/project/mlx-whisper/) is quite efficient and works great.

Many household GPUs can handle certain whisper models and workloads but for certain use cases, highest accuracy with the lowest latency at scale is needed. This is an idea in that direction but at the cost of credits.
