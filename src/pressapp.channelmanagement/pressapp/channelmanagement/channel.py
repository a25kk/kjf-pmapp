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
        context = aq_inner(self.context)
        self.has_subscribers = len(self.subscribers()) > 0
        self.subscriber_index = len(self.subscribers())
        form = self.request.form
        self.errors = {}
        if 'form.button.Submit' in self.request:
            context = aq_inner(self.context)
            target_id = form['channel-address-select']
            context_url = context.absolute_url()
            next_url = context_url + '/' + target_id
            return self.request.response.redirect(next_url)

    def subscribers(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=ISubscriber.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='sortable_title')
        subscribers = IContentListing(results)
        return subscribers
