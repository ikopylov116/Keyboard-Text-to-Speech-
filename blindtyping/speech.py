from __future__ import annotations

import queue
import threading


class SpeechService:
    """Optional offline TTS adapter. The trainer still works if pyttsx3 is unavailable."""

    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.enabled = True
        self._queue: queue.Queue[str | None] = queue.Queue(maxsize=30)
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self) -> None:
        try:
            import pyttsx3
        except ImportError:
            self.enabled = False
            return
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            while True:
                text = self._queue.get()
                if text is None:
                    return
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass
        except Exception:
            self.enabled = False
        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass

    def say(self, text: str) -> None:
        if not self.enabled or not text:
            return
        try:
            self._queue.put_nowait(text)
        except queue.Full:
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(text)
            except queue.Empty:
                pass

    def stop(self) -> None:
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
