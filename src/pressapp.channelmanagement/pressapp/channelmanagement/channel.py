from five import grok
from Acquisition import aq_inner
from plone.directives import form

from plone.namedfile.interfaces import IImageScaleTraversable
from Products.CMFCore.utils import getToolByName

from plone.app.contentlisting.interfaces import IContentListing
from pressapp.channelmanagement.subscriber import ISubscriber

from pressapp.channelmanagement import MessageFactory as _


class IChannel(form.Schema, IImageScaleTraversable):
    """
    A specific channel holding subscriber objects
    """


class View(grok.View):
    grok.context(IChannel)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_subscribers = len(self.subscribers()) > 0
        self.subscriber_index = len(self.subscribers())

    def subscribers(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=ISubscriber.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='sortable_title')
        subscribers = IContentListing(results)
        return subscribers
