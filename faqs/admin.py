from django.contrib import admin
from django.utils.html import format_html
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question_en', 'translations_preview', 'translated_languages')
    readonly_fields = ('translations_preview',)
    search_fields = ('question_en',)

    def translated_languages(self, obj):
        """Show available translations as styled labels."""
        if not obj.translations:
            return format_html("<span style='color:red;'>❌ No Translations</span>")

        return format_html(" ".join(
            f"<span style='padding:5px 8px; background:#28a745; color:white; border-radius:5px; margin-right:5px;'>{code.upper()}</span>"
            for code in obj.translations.keys()
        ))

    translated_languages.short_description = "Available Translations"

    def translations_preview(self, obj):
        """Enhanced preview with better styling and fallback indicators."""
        if not obj.pk or not obj.translations:
            return format_html("<span style='color:red;'>Save to generate translations</span>")

        preview = []
        for code, name in FAQ.LANGUAGES:
            if code == 'en':
                continue

            trans = obj.translations.get(code, {})
            status = "✅" if trans.get('question') else "❌"
            question = trans.get('question', "<i>Not translated</i>")
            answer = trans.get('answer', "<i>Not translated</i>")

            preview.append(
                f"""
                <div style='margin-bottom:8px; padding:8px; border:1px solid #ddd; border-radius:5px; background:#f9f9f9;'>
                    <strong>{status} {name} ({code}):</strong><br>
                    <span style='color:#333;'><b>Q:</b> {question}</span><br>
                    <span style='color:#333;'><b>A:</b> {answer}</span>
                </div>
                """
            )
        return format_html("".join(preview))

    translations_preview.short_description = "Translations Overview"
