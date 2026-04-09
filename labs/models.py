from django.db import models

from modelcluster.fields import ParentalKey

from django import forms

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.contrib.forms.forms import WagtailAdminFormPageForm
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from detoxify import Detoxify

# VADER's analysis model
vader = SentimentIntensityAnalyzer()

# Detoxify's analysis model, using unbiased-small so it's both light-weight and not incredibly oversensitive to a detrimental effect
detox = Detoxify('unbiased-small')

class QuoteWallTestPage(Page):
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

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)

        form.fields['your_quote'] = forms.CharField(
            label="Your Quote",
            widget=forms.Textarea,
            required=True
        )
        return form

    def analyze_with_vader(self, text):
        '''
        The old, less advanced content analysis method.
        VADER uses positive sentiment as the standard, so you want your scores to be higher to pass.

        :param text: Text to be analyzed.
        :return: An object with the sentiment score as a double `'score'` and a check whether it should go live as a boolean `'is_live'`.
        :rtype: object
        '''

        scores = vader.polarity_scores(text)
        return {
            'score': scores['compound'],
            'is_live': scores['compound'] > -0.5
        }

    def analyze_with_detoxify(self, text):
        '''
        The new and more advanced content analysis method.
        Detoxify uses negativity and toxicity as what it tests against. So a higher score is bad, in this case.
        
        :param text: Text to be analyzed.
        :return: An object with the toxicity score as a double `'score'` and a check whether it should go live through toxicity and identity attack as a boolean `'is_live'`.
        :rtype: object
        '''
        
        results = detox.predict(text)
        score = results['insult']
        return {
            'score': score,
            'is_live': score < 0.5 and results['identity_attack'] < 0.5 and results['threat'] < 0.5
        }

    def process_form_submission(self, form):
        # This process is automated with VADER

        quote_text = form.cleaned_data.get('your_quote', '')

        # data = self.analyze_with_vader(quote_text)
        data = self.analyze_with_detoxify(quote_text)

        SubmittedQuote.objects.create(
            quote_text=quote_text,
            sentiment_score=data['score'],
            is_live=data['is_live']
        )
        return super(AbstractForm, self).process_form_submission(form)

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