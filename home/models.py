from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

class HomePage(Page):
    body = MarkdownField(blank=True)
    quotes_title = models.CharField(
        max_length=255,
        default='Community Quotes',
        help_text='Heading for the quotes section'
    )
    no_quotes = models.CharField(
        max_length=255,
        default='No quotes yet, be the first!',
        help_text='Text in case there are no quotes to display'
    )
    add_quote_text = models.CharField(
        max_length=50,
        default="Add a Quote"
    )
    add_quote_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('quotes_title'),
        FieldPanel('no_quotes'),
        FieldPanel('add_quote_text'),
        PageChooserPanel('add_quote_page'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['quotes'] = SubmittedQuote.objects.filter(is_live=True)
        return context

class FormField(AbstractFormField):
    page = ParentalKey('QuoteRequestPage', on_delete=models.CASCADE, related_name='form_fields')

class QuoteRequestPage(AbstractForm):
    intro = RichTextField(blank=True)
    outtro = RichTextField(blank=True)
    submit_button = models.CharField(
        max_length=50,
        default='Submit Quote',
        help_text='Text on submit button'
    )

    content_panels = AbstractForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label='Form fields'),
        FieldPanel('outtro'),
        FieldPanel('submit_button'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        return context

    def process_form_submission(self, form):
        # This process is automated with VADER

        quote_text = form.cleaned_data.get('your_quote', '')

        # VADER analysis
        scores = analyzer.polarity_scores(quote_text)
        compound_score = scores['compound']

        SubmittedQuote.objects.create(
            quote_text=quote_text,
            sentiment_score=compound_score,
            is_live=compound_score > -0.5
        )
        return super().process_form_submission(form)

################################################################
## SNIPPETS ####################################################
################################################################

class SubmittedQuote(models.Model):
    quote_text = models.TextField()
    is_live = models.BooleanField(default=False)
    sentiment_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quote_text[:50]
    
    panels = [
        FieldPanel('quote_text'),
        FieldPanel('is_live'),
    ]

class SubmittedQuoteViewSet(SnippetViewSet):
    model = SubmittedQuote

    list_display = ('quote_text', 'is_live', 'sentiment_score', 'created_at')

    list_filter = ('is_live', 'created_at')

    search_fields = ('quote_text',)

    ordering = ('created_at',)

register_snippet(SubmittedQuote, viewset=SubmittedQuoteViewSet)