from five import grok
from plone.directives import form
from Acquisition import aq_inner
from zope import schema
from AccessControl import getSecurityManager
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing

from pressapp.channelmanagement.subscriber import ISubscriber
from pressapp.presscontent.pressroom import IPressRoom

from pressapp.presscontent import MessageFactory as _


class IPressCenter(form.Schema):
    """
    Press center that will act as the global members folder.
    """
    email = schema.TextLine(
        title=_(u"Sender E-Mail-Address"),
        description=_(u"Please enter default send from E-mail address"),
        required=True,
    )
    name = schema.TextLine(
        title=_("Sender Name"),
        description=_(u"Provide a default sender name to be included"),
        required=True,
    )
    testEmail = schema.TextLine(
        title=_(u"E-Mail Address for Tests"),
        description=_(u"Default email address used in test despatches"),
        required=True,
    )
    testRecipients = schema.List(
        title=_(u"Test Recipients"),
        description=_(u"A list of test recipients - one address per line "
                      u"comma seperated in the format: E-mail, Name"),
        value_type=schema.TextLine(
            title=_(u"Recipient"),
        ),
        required=False,
    )
    subscribers = schema.List(
        title=_(u"Subscribers"),
        description=_(u"A list of subscribers - one address per line "
                      u"- these are available as default list"),
        value_type=schema.TextLine(
            title=_(u"Subscriber"),
        ),
        required=False,
    )
    stylesheet = schema.Text(
        title=_(u"Stylesheet"),
        description=_(u"CSS used for the HTML Email"),
        required=False,
    )
    mailtemplate = schema.SourceText(
        title=_(u"E-Mail Template Press Release"),
        required=False,
    )
    mailtemplate_pi = schema.SourceText(
        title=_(u"E-Mail Template Press Invitation"),
        required=False,
    )


class View(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_pressrooms = len(self.contained_pressrooms()) > 0
        self.pressrooms = self.contained_pressrooms()

    def contained_pressrooms(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRoom.__identifier__,
                          path=dict(query='/'.join(context.getPhysicalPath()),
                                    depth=1),
                          sort_on='sortable_title')
        return results

    def memberinfo(self, owner):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getMemberById(owner)
        if member is None:
            member = mtool.getAuthenticatedMember()
        login_time = member.getProperty('last_login_time', '2011/01/01')
        return login_time

    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission(
                    'Portlets: Manage own portlets', self.context))

    def statistics(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=ISubscriber.__identifier__,)
        channels = catalog.uniqueValuesFor('channel')
        stats = {}
        stats['recipients'] = len(results)
        stats['channels'] = len(channels)
        return stats


class PressCenterSettings(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('global-settings')

    def updates(self):
        pass


class Workspaces(grok.View):
    grok.context(IPressCenter)
    grok.require('zope2.View')
    grok.name('workspaces')

    def update(self):
        self.has_workspaces = len(self.workspaces()) > 0

    def workspaces(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRoom.__identifier__,
                         path=dict(query='/'.join(context.getPhysicalPath()),
                                   depth=1),
                         sort_on='sortable_title')
        spaces = IContentListing(results)
        return spaces

    def memberdetails(self, member_id):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        info = {}
        member = mtool.getMemberById(member_id)
        info['fullname'] = member.getProperty('fullname', '')
        info['organization'] = member.getProperty('organization', '')
        info['home_page'] = member.getProperty('home_page', '')
        info['location'] = member.getProperty('location', '')
        info['last_login_time'] = member.getProperty('last_login_time',
                                                         '2011/01/01')
        return info
