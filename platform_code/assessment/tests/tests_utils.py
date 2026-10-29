from types import SimpleNamespace
from unittest.mock import Mock, patch

from assessment.utils import markdownify_bold, markdownify_italic, select_label_choice
from assessment.views.utils.utils import manage_missing_language
from django.test import TestCase
from django.utils.translation import LANGUAGE_SESSION_KEY


class TestManageMissingLanguage(TestCase):
    @patch("assessment.views.utils.utils.activate")
    @patch("assessment.views.utils.utils.get_language_from_request", return_value="en")
    def test_available_languages_are_cached_per_assessment(
        self, get_language_from_request, activate
    ):
        assessment = SimpleNamespace(
            pk=1, get_the_available_languages=Mock(return_value=["fr"])
        )
        request = SimpleNamespace(session={})
        cache = {}

        manage_missing_language(
            request,
            SimpleNamespace(assessment=assessment),
            available_languages_cache=cache,
        )
        manage_missing_language(
            request,
            SimpleNamespace(assessment=assessment),
            available_languages_cache=cache,
        )

        assessment.get_the_available_languages.assert_called_once_with()
        self.assertEqual(request.session, {LANGUAGE_SESSION_KEY: "fr"})
        self.assertEqual(activate.call_count, 2)


class TestMarkdownify(TestCase):
    def setUp(self):
        self.text1 = "Bonjour *madame*"
        self.text2 = "Bonjour **madame**"
        self.text3 = "I **gonna** take _a break_"
        self.text4 = "This sentence is pointless :("
        self.text5 = "Thi*s definit**ly a ran'(dom _ sen***tence"
        self.text6 = "There **are** __bold__ *text* **EVERYWHERE** !!"

    def testBold(self):
        self.assertEqual(self.text1, markdownify_bold(self.text1))
        self.assertEqual("Bonjour <strong>madame</strong>", markdownify_bold(self.text2))
        self.assertEqual(
            "I <strong>gonna</strong> take _a break_", markdownify_bold(self.text3)
        )
        self.assertEqual(self.text4, markdownify_bold(self.text4))
        self.assertEqual(self.text5, markdownify_bold(self.text5))
        self.assertEqual(
            "There <strong>are</strong> <strong>bold</strong> *text* <strong>EVERYWHERE</strong> !!",
            markdownify_bold(self.text6),
        )

    def testItalic(self):
        self.assertEqual("Bonjour <i>madame</i>", markdownify_italic(self.text1))
        self.assertEqual(self.text2, markdownify_italic(self.text2))
        self.assertEqual("I **gonna** take <i>a break</i>", markdownify_italic(self.text3))
        self.assertEqual(self.text4, markdownify_italic(self.text4))
        self.assertEqual(self.text5, markdownify_italic(self.text5))

    def testCombined(self):
        self.assertEqual(
            "Bonjour <i>madame</i>", markdownify_italic(markdownify_bold(self.text1))
        )
        self.assertEqual(
            "Bonjour <strong>madame</strong>",
            markdownify_italic(markdownify_bold(self.text2)),
        )
        self.assertEqual(
            "I <strong>gonna</strong> take <i>a break</i>",
            markdownify_italic(markdownify_bold(self.text3)),
        )
        self.assertEqual(self.text4, markdownify_italic(markdownify_bold(self.text4)))
        self.assertEqual(self.text5, markdownify_italic(markdownify_bold(self.text5)))
        self.assertEqual(
            "There <strong>are</strong> <strong>bold</strong> <i>text</i> <strong>EVERYWHERE</strong> !!",
            markdownify_italic(markdownify_bold(self.text6)),
        )


class TestSelectLabelChoice(TestCase):
    def setUp(self):
        self.text1 = (
            ' <input type="checkbox" name="29" value="6.4.a Notre organisation'
            ' n&#x27;utilise pas de modèles prédictifs élaborés par apprentissage automatique" id="id_29_0">'
            "Notre organisation n&#x27;utilise pas de modèles prédictifs élaborés par apprentissage"
            " automatique</label>"
        )
        self.text2 = (
            '<li><label for="id_30_1"><input type="radio" name="30" value="6.5.b Nous communiquons sur nos'
            ' résultats" id="id_30_1">'
        )

    def test_select_label_choice(self):
        # Catch the pattern
        self.assertIn(
            "Notre organisation n&#x27;utilise pas de modèles prédictifs élaborés par apprentissage"
            " automatique</label",
            select_label_choice(self.text1),
        )
        # Case the pattern is not found in the regex of select_label_choice, so the function returns empty list
        self.assertEqual([], select_label_choice(self.text2))
