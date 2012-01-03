from five import grok
from plone.memoize.instance import memoize
from Products.CMFCore.interfaces import IContentish


class OverlayContainer(grok.View):
    """View that provides a main_template replacement for overlays.
    Use metal:use-macro="context/@@overlay-container/macros/master"
    and then fill the main macro.
    """
    grok.context(IContentish)
    grok.name('overlay-container')
    grok.require('zope2.View')

    def __call__(self):
        # Disable theming
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.index()

    @property
    def macros(self):
        return self.index.macros
