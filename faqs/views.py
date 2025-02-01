from rest_framework.response import Response
from rest_framework import viewsets
from django.core.cache import cache
from .models import FAQ
from .serializers import FAQSerializer

class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en').lower()  # Ensure case insensitivity
        cache_key = f'faqs_{lang}'
        
        #fetching cached data
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        # Fetch fresh data
        queryset = self.get_queryset()
        data = []

        for faq in queryset:
            translation = faq.translations.get(lang, {}) if faq.translations else {}
            question = translation.get('question', faq.question_en)  # Fallback to English
            answer = translation.get('answer', faq.answer_en)        # Fallback to English

            data.append({
                "id": faq.id,
                "question": question,
                "answer": answer,
                "created_at": faq.created_at,
                "updated_at": faq.updated_at,
                "language": lang
            })

        # Cache data for 1 hour
        cache.set(cache_key, data, timeout=3600)

        return Response(data)
