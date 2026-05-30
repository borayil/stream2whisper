import asyncio
import base64

import ffmpeg
from yt_dlp import YoutubeDL
from openai import AsyncOpenAI
from openai.resources.realtime.realtime import AsyncRealtimeConnection

CHANNELS = 1
SAMPLE_RATE = 24000

class Stream2Whisper:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.connection: AsyncRealtimeConnection | None = None
        self.session = None
        self.connected = asyncio.Event()
        self.stop_event = asyncio.Event()

    async def stop(self):
        self.stop_event.set()

    async def handle_rt(self, language:str):
        async with self.client.realtime.connect(extra_query={"intent": "transcription"}) as conn:
            self.connection = conn

            async for event in conn:
                if event.type == "session.created":
                    self.session = event.session
                    self.connected.set()
                    print("[OK] Session created with ID:", event.session.id)
                    break

            await conn.session.update(
                session={
                    "type": "transcription",
                    "audio": {
                        "input": {
                            "format": {
                                "type": "audio/pcm",
                                "rate": SAMPLE_RATE
                            },
                            "transcription": {
                                "model": "gpt-realtime-whisper",
                                "language": language
                            }
                        }
                    }
                }
            )

            async for event in conn:
                if self.stop_event.is_set():
                    break
                
                if event.type == "session.updated":
                    self.session = event.session
                    print("[OK] Session created with ID:", event.session.id)

                elif event.type == "conversation.item.input_audio_transcription.delta":
                    print(event.delta, end="", flush=True)            

    async def _get_connection(self):
        await self.connected.wait()
        assert self.connection is not None
        return self.connection

    async def stream_audio(self, stream_url: str):

        def get_audio_stream(url):
            with YoutubeDL({
                "format": "bestaudio/best",
                "quiet": True,
            }) as ydl:
                info = ydl.extract_info(url, download=False)

            return info["url"]

        audio_url = get_audio_stream(stream_url)

        process = (
            ffmpeg
            .input(audio_url)
            .output(
                "pipe:",
                format="s16le",
                acodec="pcm_s16le",
                ac=1,
                ar=16000,
            )
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        read_size = 3200
        chunks = 0

        try:
            while not self.stop_event.is_set():
                pcm = await asyncio.to_thread(
                    process.stdout.read,
                    read_size,
                )

                if not pcm:
                    print("FFmpeg ended")
                    break

                conn = await self._get_connection()

                await conn.input_audio_buffer.append(
                    audio=base64.b64encode(pcm).decode("utf-8")
                )

                chunks += 1

                await asyncio.sleep(0.05) # <1 OK

                if chunks >= 100:
                    await conn.input_audio_buffer.commit()
                    await conn.response.create()
                    chunks = 0

        finally:
            process.kill()
            process.wait()
            try:
                process.stdout.close()
            except Exception:
                pass

    async def run(self, stream_url: str, language : str):
        await asyncio.gather(
            self.handle_rt(language),
            self.stream_audio(stream_url=stream_url),
        )
