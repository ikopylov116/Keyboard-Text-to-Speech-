from __future__ import annotations

import queue
import threading


class SpeechService:
    """Offline TTS adapter. The rest of the application does not depend on pyttsx3."""

    def __init__(self, rate: int = 175, volume: float = 1.0, enabled: bool = True):
        self.rate = rate
        self.volume = volume
        self.enabled = enabled
        self._queue: queue.Queue[str | None] = queue.Queue(maxsize=30)
        self._thread: threading.Thread | None = None
        self._start_worker()

    def _start_worker(self) -> None:
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self) -> None:
        try:
            import pyttsx3
        except ImportError:
            self.enabled = False
            return
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            while True:
                text = self._queue.get()
                if text is None:
                    return
                if not self.enabled:
                    continue
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    continue
        except Exception:
            self.enabled = False
        finally:
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

    def restart(self) -> None:
        self.stop()
        self._queue = queue.Queue(maxsize=30)
        self._start_worker()

    def stop(self) -> None:
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
