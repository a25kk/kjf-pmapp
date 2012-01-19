from five import grok
from Acquisition import aq_parent
from DateTime import DateTime
from AccessControl import getSecurityManager
from zope.interface import Interface
from zope.component import getUtility
from zope.app.component.hooks import getSite
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from Products.PlonePAS.events import IUserLoggedInEvent

from Products.CMFCore.interfaces import IContentish

from pressapp.statusbar.recentactivity import IRecentActivity

from pressapp.statusbar import MessageFactory as _


@grok.subscribe(IContentish, IObjectAddedEvent)
def trackAddActivity(obj, event):
    activities = getUtility(IRecentActivity, name=u"RecentActivity")
    username = getSecurityManager().getUser().getId()
    activities.add_activity(DateTime(), _(u"added"), username,
                            obj, aq_parent(obj))


@grok.subscribe(IContentish, IObjectModifiedEvent)
def trackEditActivity(obj, event):
    activities = getUtility(IRecentActivity, name=u"RecentActivity")
    username = getSecurityManager().getUser().getId()
    activities.add_activity(DateTime(), _(u"edited"), username,
                            obj, aq_parent(obj))


@grok.subscribe(Interface, IUserLoggedInEvent)
def userLoggedInActivity(self, event):
    site = getSite()
    activities = getUtility(IRecentActivity, name=u"RecentActivity")
    username = getSecurityManager().getUser().getId()
    activities.add_activity(DateTime(), _(u"logged in"), username, site, site)
