from Acquisition import aq_inner
from five import grok

from Products.CMFCore.utils import getToolByName

from Products.CMFCore.interfaces import IContentish
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.contentlisting.interfaces import IContentListing
from pressapp.channelmanagement.subscriber import ISubscriber
from pressapp.presscontent import MessageFactory as _


class RecipientList(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('recipient-list')

    def update(self):
        self.has_subscribers = len(self.subscriber_listing()) > 0
        form = self.request.form
        self.errors = {}
        if 'form.button.Submit' in self.request:
            context = aq_inner(self.context)
            filter_values = ('recipient-table_length', 'form.button.Submit')
            data = []
            for value in form:
                if value not in filter_values:
                    data.append(form[value])
            setattr(context, 'recipients', data)
            context.reindexObject(idxs='modified')
            context_url = context.absolute_url()
            IStatusMessage(self.request).addStatusMessage(
            _(u"Recipient list updated"), type='info')
            return self.request.response.redirect(context_url)

    def subscriber_listing(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        channels = getattr(context, 'channel', '')
        subscribers = []
        for channelname in channels:
            results = catalog(object_provides=ISubscriber.__identifier__,
                              channel=[channelname],
                              sort_on='sortable_title')
            for item in results:
                info = {}
                info['name'] = item.Title
                info['email'] = item.getObject().email
                if info not in subscribers:
                    subscribers.append(info)
        return subscribers
