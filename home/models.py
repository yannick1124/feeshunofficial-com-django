from django.db import models
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django import forms

from modelcluster.fields import ParentalKey

from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel, FieldRowPanel
from wagtailmarkdown.fields import MarkdownField
from wagtailmarkdown.blocks import MarkdownBlock
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField

# Forms

class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_mapping = getattr(settings, 'EMAIL_MAPPING', [])

        self.fields['category'].choices = [
            (item['category'], item['category']) for item in email_mapping
        ]

        if 'category' not in self.initial:
            default_item = next((item for item in email_mapping if item.get('default') is True), None)
            if default_item:
                self.initial['category'] = default_item['category']

    email = forms.EmailField(
        required=True,
        label='Your Email Address',
        widget=forms.EmailInput()
    )
    
    subject = forms.CharField(
        required=True,
        label='Subject',
        max_length=255,
        widget=forms.TextInput()
    )

    category = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=True,
        label='Message'
    )

# Blocks

class LinkBlock(blocks.StructBlock):
    splash_label = MarkdownBlock(required=False)
    link = blocks.URLBlock(required=True)

    image = blocks.ChoiceBlock(
        choices=[
            ('images/icons/github.svg', 'GitHub'),
            ('images/icons/linkedin.svg', 'LinkedIn')
        ],
        required=True
    )

    class Meta:
        template = 'home/link_block.html'

class DonationButtonBlock(blocks.StructBlock):
    splash_label = MarkdownBlock(required=False)
    button_text = MarkdownBlock(required=False, default='Send me a tip!')

    class Meta:
        template = 'home/dono_button.html'

# Page templates

class GenericRedirectPage(Page):
    '''
    The most basic page of my site. 
    Redirects automatically to a specified page or otherwise its first child.
    As a last resort, it redirects to the root page.
    '''

    redirect_to = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='The page to redirect to.'
    )

    content_panels = Page.content_panels + [
        PageChooserPanel('redirect_to'),
    ]

    def serve(self, request):

        if self.redirect_to:
            return redirect(self.redirect_to.url, permanent=False)
        
        first_child = self.get_children().live().first()
        if first_child:
            return redirect(first_child.url, permanent=False)

        if hasattr(request, 'site') and request.site.root_page:
            return redirect(request.site.root_page.url, permanent=False)

        return super().serve(request)

class MarkdownPage(Page):
    body = MarkdownField(blank=True)

    donation_button = StreamField(
        [('donation_button', DonationButtonBlock())],
        blank=True,
        null=True,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        FieldPanel('donation_button')
    ]

class LandingPage(Page):
    picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = MarkdownField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('picture'),
        FieldPanel('body')
    ]

class ContactPage(Page):
    intro = MarkdownField(blank=True)
    thank_you_text = MarkdownField(blank=True)

    from_address = models.CharField(max_length=255, blank=True)
    to_address = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255, blank=True)

    link_block = StreamField(
        [('link_block', LinkBlock())],
        blank=True,
        null=True,
        use_json_field=True
    )

    donation_button = StreamField(
        [('donation_button', DonationButtonBlock())],
        blank=True,
        null=True,
        use_json_field=True
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address'),
                FieldPanel('to_address'),
            ]),
            FieldPanel('subject')
        ], heading='Email Settings'),
        FieldPanel('link_block'),
        FieldPanel('donation_button')
    ]

    def serve(self, request):
        email_mapping = getattr(settings, 'EMAIL_MAPPING', [])

        if request.method == 'POST':
            form = ContactForm(request.POST)
            if form.is_valid():
                selected_category = form.cleaned_data['category']
                visitor_email = form.cleaned_data['email']
                user_subject = form.cleaned_data['subject']

                matched_item = next((item for item in email_mapping if item['category'] == selected_category), None)
                recipient = matched_item['address'] if matched_item else self.to_address

                base_subject = self.subject or 'Contact Form Submission'
                custom_subject = f'[{selected_category}] {user_subject}'

                content = (
                    f'From: {visitor_email}\n'
                    f'Category: {selected_category}\n'
                    f'Subject: {user_subject}\n\n'
                    f'Message:\n{form.cleaned_data["message"]}'
                )

                send_mail(
                    subject=custom_subject,
                    message=content,
                    from_email=self.from_address or settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    reply_to=[visitor_email]
                )

                return render(request, self.get_template(request), {
                    'page': self,
                    'form_submitted': True
                })
        else:
            initial_data = {}

            category_param = request.GET.get('category')
            if category_param:
                matched_item = next((item for item in email_mapping if item.get('parameter') == category_param), None)
                if matched_item:
                    initial_data['category'] = matched_item['category']

            form = ContactForm(initial=initial_data)

        return render(request, self.get_template(request), {
            'page': self,
            'form': form,
            'form_submitted': False,
            'email_mapping': email_mapping
        })