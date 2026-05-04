from django.db import models
from django.apps import apps
from django.shortcuts import redirect

from wagtail import blocks
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.models import Page
from wagtail_color_panel.fields import ColorField
from wagtail_color_panel.edit_handlers import NativeColorPanel
from wagtail.images.models import Image

from datetime import date

THEMES = {
    'dino': {
        'label': 'Dino Theme',
        'image': '/static/images/examples/dino_example.png',
        'class': 'friends.DinoFriendPage'
    },
    'magic': {
        'label': 'Magic Theme',
        'image': '/static/images/examples/magic_example.png',
        'class': 'friends.MagicFriendPage'
    },
}

class FriendPage(Page):
    theme_questions = []

    friend_name = models.CharField(
        max_length=255,
        verbose_name='"My name is ___:"',
        default='[How did you do this? This is a required field!]'
    )
    friend_know_from = models.CharField(
        max_length=255,
        verbose_name='"I know Yannick from ___:"',
        default='[How did you do this? This is a required field!]'
    )
    friend_contact = models.CharField(
        max_length=255,
        verbose_name='"I can be reached at ___:"',
        null=True,
        blank=True
    )
    friend_bday = models.DateField(
        verbose_name='"My birthday is at ___ and I am [autofill] years old:"',
        default=date(1900, 1, 1)
    )
    friend_siblings = models.CharField(
        max_length=255,
        verbose_name='"I have ___ siblings:"',
        null=True,
        blank=True
    )
    friend_color = ColorField(
        verbose_name='"My favorite color is ___:"',
        null=True,
        blank=True
    )
    friend_animal = models.CharField(
        max_length=255,
        verbose_name='"My favorite animal is ___:"',
        null=True,
        blank=True
    )
    friend_book = models.CharField(
        max_length=255,
        verbose_name='"My favorite book is ___:"',
        null=True,
        blank=True
    )
    friend_movie = models.CharField(
        max_length=255,
        verbose_name='"My favorite movie is ___:"',
        null=True,
        blank=True
    )
    friend_food = models.CharField(
        max_length=255,
        verbose_name='"My favorite food is ___:"',
        null=True,
        blank=True
    )
    friend_likes = StreamField(
        [(
            'item', 
            blocks.CharBlock(label="Like")
        )],
        verbose_name='"I like these things:"',
        use_json_field=True,
        blank=True
    )
    friend_dislikes = StreamField(
        [(
            'item', 
            blocks.CharBlock(label="Dislike")
        )],
        verbose_name='"These are the things I don\'t like:"',
        use_json_field=True,
        blank=True
    )
    friend_cool = models.CharField(
        max_length=255,
        verbose_name='"Yannick is cool because ___:"',
        default='[How did you do this? This is a required field!]'
    )

    friend_picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Profile picture:'
    )

    content_panels = Page.content_panels + [
        FieldPanel('friend_picture'),
        
        FieldPanel('friend_name'),
        FieldPanel('friend_know_from'),
        FieldPanel('friend_contact'),
        FieldPanel('friend_bday'),
        FieldPanel('friend_siblings'),
        NativeColorPanel('friend_color'),
        FieldPanel('friend_animal'),
        FieldPanel('friend_book'),
        FieldPanel('friend_movie'),
        FieldPanel('friend_food'),
        FieldPanel('friend_likes'),
        FieldPanel('friend_dislikes'),
        FieldPanel('friend_cool')
    ]
    # TODO: MOVE verbose_nameS TO VERBOSE NAMES

    @property
    def friend_age(self):
        if not self.friend_bday or self.friend_bday == date(1900, 1, 1):
            return '???'
        
        today = date.today()
        return today.year - self.friend_bday.year - (
            (today.month, today.day) < (self.friend_bday.month, self.friend_bday.day)
        )

    class Meta:
        abstract = True

class AddPageTheme(Page):
    theme_choice = models.CharField(
        max_length=50,
        choices=[(k, v['label']) for k, v in THEMES.items()],
        default='dino'
    )

    form_target = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('theme_choice'),
        PageChooserPanel('form_target'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Pass the THEMES dictionary to the template
        context['THEMES'] = THEMES
        return context
    
class AddPageContent(Page):
    def get_context(self, request):
        context = super().get_context(request)
        theme_key = request.GET.get('theme')
        questions = []

        if theme_key in THEMES:
            try:
                class_path = THEMES[theme_key]['class']
                app_label, model_name = class_path.split('.')
                model_class = apps.get_model(app_label, model_name)
                
                if model_class:
                    for field in model_class._meta.get_fields():
                        if field.name == 'title' or field.name.startswith('friend'):
                            if isinstance(field, ColorField):
                                assigned_type = 'ColorField'
                            elif field.__class__.__name__ == 'StreamField':
                                assigned_type = 'StreamField'
                            elif field.get_internal_type() == 'ForeignKey':
                                related = getattr(field, 'related_model', None)
                                if related == Image:
                                    assigned_type = 'ImageChooser'
                                else:
                                    assigned_type = 'ForeignKey'
                            else:
                                assigned_type = field.get_internal_type()
                            
                            questions.append({
                                'label': getattr(field, 'verbose_name', field.name),
                                'name': field.name,
                                'type': assigned_type,
                                'choices': getattr(field, 'choices', None),
                                'required': not getattr(field, 'blank', True)
                            })

            except Exception as e:
                print(f"Error gathering fields: {e}")
        
        context['theme_questions'] = questions
        return context

class DinoFriendPage(FriendPage):
    template = 'friends/theme_dino.html'
    theme_questions = [
        'friend_dino'
    ]

    friend_dino = models.CharField(
        max_length=255,
        verbose_name="My favorite dinosaur is ___",
        default='[How did you do this? This is a required field!]'
    )

    for theme_question in theme_questions:
        content_panels = FriendPage.content_panels + [
            FieldPanel(theme_question)
        ]

class MagicFriendPage(FriendPage):
    template = 'friends/theme_magic.html'
    theme_questions = [
        'friend_magic'
    ]

    friend_magic = models.CharField(
        max_length=255,
        verbose_name="If I had magic, it would be ___ magic",
        default='[How did you do this? This is a required field!]'
    )

    for theme_question in theme_questions:
        content_panels = FriendPage.content_panels + [
            FieldPanel(theme_question)
        ]