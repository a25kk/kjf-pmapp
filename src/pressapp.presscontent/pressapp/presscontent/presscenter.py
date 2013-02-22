import json
from five import grok
from plone import api
from plone.directives import form
from Acquisition import aq_inner
from zope import schema
from AccessControl import getSecurityManager
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.content import ContentHistoryView

from Products.CMFCore.interfaces import IContentish
from plone.app.contentlisting.interfaces import IContentListing

from pressapp.presscontent.interfaces import IPressContent
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

    def presscontent_index(self):
        items = self.get_data()
        return len(items)

    def pr_index(self):
        items = self.get_data(ptype='pressapp.presscontent.pressrelease')
        return len(items)

    def pi_index(self):
        items = self.get_data(ptype='pressapp.presscontent.pressinvitation')
        return len(items)

    def get_data(self, ptype=None):
        catalog = api.portal.get_tool(name='portal_catalog')
        query = self.base_query()
        presstypes = ['pressapp.presscontent.pressrelease',
                      'pressapp.presscontent.pressinvitation']
        if ptype is not None:
            query['portal_type'] = ptype
        else:
            query['portal_type'] = presstypes
        brains = catalog.searchResults(**query)
        results = IContentListing(brains)
        return results

    def base_query(self):
        return dict(sort_on='modified',
                    sort_order='reverse')

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
        login_time = member.getProperty('last_login_time', '2011/01/01')
        return login_time

    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission(
                    'Portlets: Manage own portlets', self.context))

    def get_history(self):
        context = aq_inner(self.context)
        history = context.restrictedTraverse('@@changes').pressapp_history(
            limit=5)
        return history

    def get_percental_value(self, index):
        pressitems = self.presscontent_index()
        one_percent = float(pressitems) / 100
        if index == '0':
            index_value = index
        else:
            index_value = index / one_percent
        index = round(float(index_value))
        return str(index)

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


class PressCenterHistory(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('changes')

    def render(self):
        data = self.pressapp_history()
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)

    def pressapp_history(self, limit=5):
        history = []
        status = self.status_list(limit=limit)
        timestamps = list()
        for x in status:
            pit = x['timestamp']
            timestamps.append(pit)
        pit_sorted = sorted(timestamps, reverse=True)
        for pit in pit_sorted:
            for x in status:
                if x['timestamp'] == pit:
                    history.append(x)
        return history

    def status_list(self, limit=5):
        items = self.last_modified_content(limit=limit)
        state_info = []
        idx = 0
        for item in items:
            obj = item.getObject()
            history = self.history_info(obj)
            if len(history) > 0:
                event = history[0]
                idx += 1
                info = {}
                info['idx'] = idx
                timestamp = event['time']
                time = api.portal.get_localized_time(datetime=timestamp,
                                                     long_format=False)
                time_only = api.portal.get_localized_time(datetime=timestamp,
                                                          time_only=True)
                info['time'] = time
                info['time_only'] = time_only
                info['timestamp'] = timestamp.ISO8601()
                actor = event['actor']
                info['actor'] = actor['username']
                info['actorname'] = actor['fullname']
                info['action'] = event['transition_title']
                info['title'] = item.Title
                info['url'] = item.getURL()
                info['type'] = item.portal_type
                #info['details'] = event
                state_info.append(info)
        return state_info

    def history_info(self, item):
        context = aq_inner(self.context)
        chv = ContentHistoryView(item, context.REQUEST).fullHistory()
        return chv

    def last_modified_content(self, limit=5):
        catalog = api.portal.get_tool(name='portal_catalog')
        press_types = ['pressapp.presscontent.pressrelease',
                       'pressapp.presscontent.pressinvitation']
        results = catalog(portal_type=press_types,
                          sort_on='modified',
                          sort_order='reverse',
                          sort_limit=limit)[:limit]
        return results
