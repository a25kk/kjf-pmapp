from five import grok
from Acquisition import aq_parent
from DateTime import DateTime
from AccessControl import getSecurityManager
from zope.component import getUtility
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from Products.CMFCore.interfaces import IContentish

from pressapp.statusbar.recentactivity import IRecentActivity


@grok.subscribe(IContentish, IObjectAddedEvent)
def trackAddActivity(obj, event):
    activities = getUtility(IRecentActivity, name=u"RecentActivity")
    username = getSecurityManager().getUser().getId()
    activities.add_activity(DateTime(), u"added", username,
                            obj, aq_parent(obj))


@grok.subscribe(IContentish, IObjectModifiedEvent)
def trackEditActivity(obj, event):
    activities = getUtility(IRecentActivity, name=u"RecentActivity")
    username = getSecurityManager().getUser().getId()
    activities.add_activity(DateTime(), u"edited", username,
                            obj, aq_parent(obj))
