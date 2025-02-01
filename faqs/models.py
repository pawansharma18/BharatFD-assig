import time
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from googletrans import Translator

logger = logging.getLogger(__name__)

class FAQ(models.Model):
    LANGUAGES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('bn', 'Bengali'),
        ('es', 'Spanish'),
        ('fr', 'French')
    ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # CKEditor fields for rich text support
    question_en = CKEditor5Field(_("Question (English)"), config_name="default")
    answer_en = CKEditor5Field(_("Answer (English)"), config_name="default")

    # JSONField should allow blank values (to avoid mandatory input issue)
    translations = models.JSONField(default=dict, blank=True, null=True)

    def generate_translations(self):
        """Generate multilingual translations safely with fallbacks."""
        translator = Translator(service_urls=['translate.google.com', 'translate.google.co.in'])
        self.translations = {}

        for code, name in self.LANGUAGES:
            if code == 'en':  # Skip English as it's the source
                continue
            
            try:
                trans_q, trans_a = None, None

                for attempt in range(3):  # Retry up to 3 times
                    try:
                        trans_q = translator.translate(self.question_en, dest=code, src='en').text
                        trans_a = translator.translate(self.answer_en, dest=code, src='en').text
                        break  # Exit loop on success
                    except Exception:
                        if attempt == 2:
                            logger.error(f"Translation failed for {name} ({code}). Using fallback.")
                        time.sleep(1)

                self.translations[code] = {
                    'question': trans_q or self.question_en,  # Fallback to English
                    'answer': trans_a or self.answer_en,      # Fallback to English
                }
                logger.info(f"Translated to {name} ({code}): {trans_q[:50]}...")

            except Exception as e:
                logger.error(f"Translation error for {name} ({code}): {str(e)}")
                self.translations[code] = {
                    'question': self.question_en,
                    'answer': self.answer_en
                }

    def save(self, *args, **kwargs):
        """Automatically generate translations when saving if not present."""
        if not self.translations:  # Generate only if empty
            self.generate_translations()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_en[:50]
