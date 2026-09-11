import unittest

from blindtyping.engine import TypingSession


class TypingSessionTests(unittest.TestCase):
    def test_progress_and_completion(self):
        session = TypingSession("abc")
        self.assertFalse(session.running)
        self.assertTrue(session.add_char("a"))
        self.assertTrue(session.running)
        self.assertFalse(session.add_char("x"))
        self.assertTrue(session.add_char("c"))
        self.assertTrue(session.finished)
        result = session.result()
        self.assertEqual(result.typed, "axc")
        self.assertEqual(result.correct_chars, 2)
        self.assertEqual(result.errors, 1)

    def test_backspace_rewinds_position(self):
        session = TypingSession("ab")
        session.add_char("a")
        self.assertTrue(session.backspace())
        self.assertEqual(session.position, 0)
        self.assertEqual(session.expected, "a")

    def test_empty_target_rejected(self):
        with self.assertRaises(ValueError):
            TypingSession("")


if __name__ == "__main__":
    unittest.main()
