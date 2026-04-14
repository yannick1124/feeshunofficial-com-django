from django.db import models

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

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

    content_panels = Page.content_panels + [
        FieldPanel('friend_name', heading='My name is ___:'),
        FieldPanel('friend_know_from', heading='I know Yannick from ___:'),
        FieldPanel('friend_contact', heading='I can be reached at ___:'),
        FieldPanel('friend_bday', heading='My birthday is at ___ and I am [autofill] years old:')
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