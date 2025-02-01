from rest_framework.response import Response
from rest_framework import viewsets
from django.core.cache import cache
from .models import FAQ
from .serializers import FAQSerializer

class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        cache_key = f'faqs_{lang}'
        
        # Try cached version first
        if cached_data := cache.get(cache_key):
            return Response(cached_data)
        
        # Process and cache if not found
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Cache for 1 hour
        cache.set(cache_key, data, timeout=3600)
        
        return Response(data)