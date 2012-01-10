import time
from five import grok
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IContentish

from pressapp.statusbar.recentactivity import IRecentActivity


class StatusBar(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('activity-bar')

    def activities(self):
        activities = queryUtility(IRecentActivity, name=u"RecentActivity")
        recent = activities.get_recent_activity(5)
        for action in recent:
            activity = action[1]
            yield dict(time=self.prettyprint_time(
                            int(time.time()) - action[0]),
                       action=activity['action'],
                       user=activity['user'],
                       obj=activity['object'],
                       pbj_url=activity['object_url'],
                       parent=activity['parent'],
                       parent_url=activity['parent_url'])

    def user_portrait(self, username):
        if username is None:
            return 'defaultUser.gif'
        else:
            mtool = getToolByName(self.context, 'portal_membership')
            return mtool.getPersonalPortrait(username).absolute_url()

    def prettyprint_time(self, seconds):
        minutes = seconds/60
        days = minutes/1440
        hours = minutes/60 - (days * 24)
        exact_minutes = minutes - (hours * 60) - (days * 24 * 60)
        return {'days': days, 'hours': hours, 'minutes': exact_minutes}
