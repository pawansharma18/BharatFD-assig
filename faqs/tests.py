from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from .models import FAQ
from unittest.mock import patch

class FAQModelTest(TestCase):
    
    
    @patch('faqs.models.Translator')
    def test_translation_creation(self, mock_translator):
        """Test translations are auto-generated in JSON format"""
        # Configure mock
        mock_instance = mock_translator.return_value
        mock_instance.translate.side_effect = lambda text, dest: type('obj', (object,), {'text': f'Translated {text}'})
    
        faq = FAQ.objects.create(
            question_en="Test Question",
            answer_en="<p>Test Answer</p>"
        )
    
        # Verify mock translations
        self.assertEqual(
            faq.translations['hi']['question'],
            'Translated Test Question'
        )
        self.assertEqual(
            faq.translations['hi']['answer'],
            'Translated <p>Test Answer</p>'
        )
class FAQAPITest(TestCase):
    def setUp(self):
        # Create FAQ with automatic translations
        self.faq = FAQ.objects.create(
            question_en="Test Question",
            answer_en="<p>Test Answer</p>"
        )
        self.url = reverse('faq-list')
    
    def test_hindi_translation(self):
        """Test API returns Hindi translations"""
        # Force translation update
        self.faq.generate_translations()
        self.faq.save()
    
        response = self.client.get(f"{self.url}?lang=hi")
        self.assertEqual(response.status_code, 200)
    
        # Verify translation exists and differs from English
        translated_question = response.json()[0]['question']
        self.assertNotEqual(translated_question, "Test Question")
        self.assertGreater(len(translated_question), 3)

    
    
        # Verify translation exists and differs from English
        translated_question = response.json()[0]['question']
        self.assertNotEqual(translated_question, "Test Question")
        self.assertGreater(len(translated_question), 3)
    
        # Verify answer contains HTML
        self.assertIn('<p>', response.json()[0]['answer'])
    
    def test_cache_behavior(self):
        """Verify Redis caching works"""
        # Clear existing cache
        cache.delete('faqs_en')
    
        # First request (cache miss - should SET cache)
        response1 = self.client.get(self.url)
    
        # Verify cache was created after first request
        cached_data = cache.get('faqs_en')
        self.assertIsNotNone(cached_data, "Cache should be set after first request")
        self.assertEqual(response1.json(), cached_data)
    
        # Second request (cache hit - should USE cache)
        response2 = self.client.get(self.url)
        self.assertEqual(response1.content, response2.content)