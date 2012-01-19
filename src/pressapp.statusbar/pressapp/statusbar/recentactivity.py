import time
from five import grok
from zope.interface import Interface
from BTrees.OOBTree import OOBTree

from pressapp.statusbar import MessageFactory as _


class IRecentActivity(Interface):
    """ Utility storing recent activity for a status bar/stream
    """

    def get_recent_activity(items=None):
        """ Call recent activity """


class RecentActivityUtility(object):
    """ Utility for recent activities """
    grok.implements(IRecentActivity)

    def __init__(self):
        self.activities = OOBTree()

    def add_activity(self, timestamp, action, user, obj, parent):
        """ Add an activity to the BTree storage """
        timestamp = int(time.time())
        activity = {'action': action,
                    'user': user,
                    'object': obj,
                    'object_url': obj.absolute_url(),
                    'parent': parent,
                    'parent_url': parent.absolute_url(),
                    }
        self.activities.insert(timestamp, activity)
        return timestamp

    def get_recent_activity(self, items=None):
        """ Get the activities stored in the BTree """
        if self.activities:
            if items:
                return sorted(self.activities.items(), reverse=True)[:items]
            else:
                return sorted(self.activities.items(), reverse=True)

grok.global_utility(RecentActivityUtility, provides=IRecentActivity,
    name='RecentActivity', direct=False)
