from five import grok
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.layout.navigation.interfaces import INavigationRoot

from pressapp.presscontent import MessageFactory as _


class Subscriptions(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('press-subscription')

    def update(self):
        self.presscenter = self.presscenter_obj()
        self.errors = {}
        if 'form.button.Subscribe' in self.request:
            context = aq_inner(self.context)
            context_url = context.absolute_url()
            pcenter = self.presscenter
            email = self.request.get('email', None)
            feedback = (
                '/@@press-subscription-success?type=subscribe&email=%s'
                % email)
            if email is None or email is '':
                self.errors['email'] = _(u"Email address is required")
            else:
                addresses = pcenter.subscribers
                if email in addresses:
                    self.errors['email'] = _(u"The entered email address is "
                                             u"already subscribed")
                else:
                    addresses.append(email)
                    setattr(pcenter, 'subscribers', addresses)
                    pcenter.reindexObject(idxs='modified')
                    IStatusMessage(self.request).addStatusMessage(
                        _(u"Your subscription settings have been updated"),
                        type='info')
                    return self.request.response.redirect(
                        context_url + feedback)
        if 'form.button.Unsubscribe' in self.request:
            context = aq_inner(self.context)
            context_url = context.absolute_url()
            pcenter = self.presscenter
            email = self.request.get('email', None)
            feedback = (
                '/@@press-subscription-success?type=unsubscribe&email=%s'
                % email)
            if email is None or email is '':
                self.errors['email'] = _(u"Email address is required")
            else:
                addresses = pcenter.subscribers
                if email not in addresses:
                    self.errors['email'] = _(u"The entered email address is "
                                             u"not subscribed")
                else:
                    addresses.remove(email)
                    setattr(pcenter, 'subscribers', addresses)
                    pcenter.reindexObject(idxs='modified')
                    IStatusMessage(self.request).addStatusMessage(
                        _(u"Your subscription settings have been updated"),
                        type='info')
                    return self.request.response.redirect(
                        context_url + feedback)

    def _getRecipients(self):
        presscenter = self.presscenter
        recipients = presscenter.subscribers
        return recipients

    def presscenter_obj(self):
        portal = getSite()
        presscenter = portal['presscenter']
        return presscenter


class SubscriptionSuccess(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('press-subscription-success')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name='plone_portal_state')
        self.portal_url = self.portal_state.portal_url
        self.action_type = self.request.get('type', '')
        self.address = self.request.get('email', 'Unkown')
