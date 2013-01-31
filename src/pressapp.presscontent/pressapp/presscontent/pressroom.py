from five import grok
from plone.directives import form

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing

from pressapp.presscontent.pressrelease import IPressRelease
from pressapp.presscontent.pressinvitation import IPressInvitation
from pressapp.presscontent.interfaces import IPressContent

from pressapp.presscontent import MessageFactory as _


class IPressRoom(form.Schema):
    """
    A single press room that will be the workspace for members.
    """


class View(grok.View):
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_releases = len(self.contained_pressreleases()) > 0
        self.pressreleases = self.contained_pressreleases()
        self.has_invitations = len(self.contained_invitations()) > 0

    def contained_pressreleases(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRelease.__identifier__,
                          path='/'.join(context.getPhysicalPath()),
                          sort_on='modified',
                          sort_order='reverse')
        items = IContentListing(results)
        return items

    def contained_invitations(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressInvitation.__identifier__,
                          path='/'.join(context.getPhysicalPath()),
                          sort_on='modified',
                          sort_order='reverse')
        items = IContentListing(results)
        return items

    def get_state_info(self, state):
        info = _(u"draft")
        if state == 'published':
            info = _(u"sent")
        return info


class DashboardReleases(grok.View):
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.name('dashboard-releases')

    def update(self):
        self.has_pressreleases = len(self.contained_pressreleases()) > 0

    def contained_pressreleases(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressRelease.__identifier__,
                          path='/'.join(context.getPhysicalPath()))
        items = IContentListing(results)
        return items


class DashboardInvitations(grok.View):
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.name('dashboard-invitations')

    def update(self):
        self.has_pressinvitations = len(self.contained_pressinvitations()) > 0

    def contained_pressinvitations(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressInvitation.__identifier__,
                          path='/'.join(context.getPhysicalPath()))
        items = IContentListing(results)
        return items


class DashboardStats(grok.View):
    grok.context(IPressRoom)
    grok.require('zope2.View')
    grok.name('dashboard-statistics')

    def update(self):
        self.has_content = len(self.published_presscontent()) > 0

    def presscontent_index(self):
        context = aq_inner(self.context)
        return len(context.items())

    def pressrelease_index(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='pressapp.presscontent.pressrelease',)
        return len(items)

    def pressinvitations_index(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='pressapp.presscontent.pressinvitation',)
        return len(items)

    def published_presscontent(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IPressContent.__identifier__,
                          review_state='published')
        items = IContentListing(results)
        return items
