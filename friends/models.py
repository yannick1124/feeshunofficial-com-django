from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from datetime import date

class FriendPage(Page):
    friend_name = models.CharField(
        max_length=255,
        default='[How did you do this? This is a required field!]'
    )
    friend_know_from = models.CharField(
        max_length=255,
        default='[How did you do this? This is a required field!]'
    )
    friend_contact = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_bday = models.DateField(
        verbose_name="Birthdate",
        default=date(1900, 1, 1)
    )
    friend_siblings = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_color = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_animal = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_book = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_movie = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_food = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    friend_likes = StreamField(
        [(
            'item', 
            blocks.CharBlock(label="Like")
        )],
        use_json_field=True,
        blank=True
    )
    friend_dislikes = StreamField(
        [(
            'item', 
            blocks.CharBlock(label="Dislike")
        )],
        use_json_field=True,
        blank=True
    )
    friend_cool = models.CharField(
        max_length=255,
        default='[How did you do this? This is a required field!]'
    )

    friend_picture = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('friend_picture'),
        
        FieldPanel('friend_name', heading='My name is ___:'),
        FieldPanel('friend_know_from', heading='I know Yannick from ___:'),
        FieldPanel('friend_contact', heading='I can be reached at ___:'),
        FieldPanel('friend_bday', heading='My birthday is at ___ and I am [autofill] years old:'),
        FieldPanel('friend_siblings', heading='I have ___ siblings:'),
        FieldPanel('friend_color', heading='My favorite color is ___:'),
        FieldPanel('friend_animal', heading='My favorite animal is ___:'),
        FieldPanel('friend_book', heading='My favorite book is ___:'),
        FieldPanel('friend_movie', heading='My favorite movie is ___:'),
        FieldPanel('friend_food', heading='My favorite food is ___:'),
        FieldPanel('friend_likes', heading='I like these things:'),
        FieldPanel('friend_dislikes', heading="These are the things I don't like:"),
        FieldPanel('friend_cool', heading='Yannick is cool because ___:')
    ]

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

class DinoFriendPage(FriendPage):
    template = 'friends/theme_dino.html'

    friend_dino = models.CharField(
        max_length=255,
        default='[How did you do this? This is a required field!]'
    )

    content_panels = FriendPage.content_panels + [
        FieldPanel('friend_dino', heading='My favorite dinosaur is ___:')
    ]