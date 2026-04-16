from django.db import models

import os

from django.conf import settings
from django.templatetags.static import static

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

def get_icon_choices():
    icon_path = os.path.join(settings.BASE_DIR, 'website', 'static', 'images', 'icons')
    try:
        return [(f, f) for f in os.listdir(icon_path) if f.endswith('.svg')]
    except FileNotFoundError:
        return []

@register_snippet
class WaffleMenu(ClusterableModel):
    title = models.CharField(max_length=100, default="Main Waffle Menu")

    panels = [
        FieldPanel('title'),
        InlinePanel('menu_items', label="Menu Items"),
    ]

    def __str__(self):
        return self.title

class WaffleMenuItem(Orderable):
    parent = ParentalKey('website.WaffleMenu', related_name='menu_items')
    label = models.CharField(
        max_length=50
    )
    link_url = models.CharField(
        max_length=255
    )
    icon_name = models.CharField(
        max_length=100,
        choices=get_icon_choices()
    )
    hide_on_url_keyword = models.CharField(
        max_length=100,
        blank=True
    )

    @property
    def icon_url(self):
        return static(f"images/icons/{self.icon_name}")

    panels = [
        FieldPanel('label'),
        FieldPanel('link_url'),
        FieldPanel('icon_name'),
        FieldPanel('hide_on_url_keyword')
    ]