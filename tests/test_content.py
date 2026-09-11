import unittest

from blindtyping.content import lessons, random_lesson


class ContentTests(unittest.TestCase):
    def test_language_filter(self):
        self.assertTrue(lessons("Русский", "Начальный"))
        self.assertTrue(lessons("English", "Начальный"))
        self.assertTrue(all(x.language == "Русский" for x in lessons("Русский")))

    def test_random_lesson_matches_request(self):
        lesson = random_lesson("Русский", "Средний")
        self.assertEqual(lesson.language, "Русский")
        self.assertEqual(lesson.level, "Средний")
        self.assertTrue(lesson.text)


if __name__ == "__main__":
    unittest.main()
