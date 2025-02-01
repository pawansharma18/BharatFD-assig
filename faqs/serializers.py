from rest_framework import serializers
from .models import FAQ

class FAQSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    translations = serializers.JSONField(read_only=True)  # For debugging

    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'translations', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'translations']

    def get_translation_context(self):
        """Retrieve the requested language from the request context, fallback to 'en'."""
        request = self.context.get('request')
        if request:
            lang = request.query_params.get('lang', 'en').lower()
            if lang in dict(FAQ.LANGUAGES):  # Ensure lang is valid
                return lang
        return 'en'  # Default to English

    def get_question(self, obj):
        """Fetch translated question, fallback to default English question."""
        lang = self.get_translation_context()
        if obj.translations:
            return obj.translations.get(lang, {}).get('question', obj.question_en)
        return obj.question_en  # Fallback to default English

    def get_answer(self, obj):
        """Fetch translated answer, fallback to default English answer."""
        lang = self.get_translation_context()
        if obj.translations:
            return obj.translations.get(lang, {}).get('answer', obj.answer_en)
        return obj.answer_en  # Fallback to default English
