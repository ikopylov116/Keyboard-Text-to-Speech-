import tempfile
import unittest
from pathlib import Path

from blindtyping.engine import TypingSession
from blindtyping.storage import HistoryStore


class HistoryStoreTests(unittest.TestCase):
    def test_result_persists_language_and_level(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            store = HistoryStore(path)
            session = TypingSession("abc")
            for char in "abc":
                session.add_char(char)
            store.add_result(session.result(), "Начальный", "English")

            loaded = HistoryStore(path)
            rows = loaded.sessions()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["language"], "English")
            self.assertEqual(rows[0]["level"], "Начальный")
            self.assertEqual(rows[0]["typed"], "abc")

    def test_corrupt_file_is_recovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            path.write_text("not-json", encoding="utf-8")
            store = HistoryStore(path)
            self.assertEqual(store.sessions(), [])
            self.assertEqual(store.best()["sessions"], 0)


if __name__ == "__main__":
    unittest.main()
