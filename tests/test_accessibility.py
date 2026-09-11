import tempfile
import unittest
from pathlib import Path

from blindtyping.accessibility import AccessibilityController
from blindtyping.storage import HistoryStore


class FakeSpeech:
    def __init__(self):
        self.enabled = True
        self.messages = []

    def set_enabled(self, value):
        self.enabled = value

    def say(self, text):
        self.messages.append(text)


class AccessibilityTests(unittest.TestCase):
    def make_controller(self):
        store = HistoryStore(Path(tempfile.mkdtemp()) / "history.json")
        speech = FakeSpeech()
        return AccessibilityController(speech, store), speech

    def test_toggle_persists(self):
        controller, speech = self.make_controller()
        self.assertTrue(controller.enabled)
        controller.toggle()
        self.assertFalse(controller.enabled)
        self.assertFalse(speech.enabled)

    def test_error_feedback_describes_expected_character(self):
        controller, speech = self.make_controller()
        controller.character_feedback("x", False, " ")
        self.assertTrue(any("пробел" in item for item in speech.messages))

    def test_character_feedback_can_be_enabled(self):
        controller, speech = self.make_controller()
        controller.speak_characters = True
        controller.character_feedback("а", True, "б")
        self.assertIn("а", speech.messages)


if __name__ == "__main__":
    unittest.main()
