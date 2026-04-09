from django.db import models

from django.shortcuts import redirect
from wagtail.models import Page
from wagtail.admin.panels import PageChooserPanel

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
        help_text="The page to redirect to."
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