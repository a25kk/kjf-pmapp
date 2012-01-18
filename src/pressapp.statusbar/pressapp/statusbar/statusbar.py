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

    def update(self):
        self.has_activities = len(self.recent_activities(10)) > 0

    def recent_activities(self, number):
        activities = queryUtility(IRecentActivity, name=u"RecentActivity")
        if number:
            recent = activities.get_recent_activity(number)
        else:
            recent = activities.get_recent_activities(10)
        recentlist = []
        if recent:
            for action in recent:
                activity = action[1]
                actionlist = dict(time=self.prettyprint_time(
                                int(time.time()) - action[0]),
                           action=activity['action'],
                           user=activity['user'],
                           obj=activity['object'],
                           pbj_url=activity['object_url'],
                           parent=activity['parent'],
                           parent_url=activity['parent_url'])
                recentlist.append(actionlist)
        return recentlist

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


class MemberStatusBar(grok.View):
    grok.context(IContentish)
    grok.require('cmf.ModifyPortalContent')
    grok.name('my-activities')

    def update(self):
        self.has_activities = len(self.my_activities()) > 0

    def my_activities(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        activitylist = self.recent_activities()
        mylist = []
        for entry in activitylist:
            if entry['user'] == member.getId():
                mylist.append(entry)
        return mylist

    def recent_activities(self):
        activities = queryUtility(IRecentActivity, name=u"RecentActivity")
        recent = activities.get_recent_activity(5)
        recentlist = []
        if recent:
            for action in recent:
                activity = action[1]
                actionlist = dict(time=self.prettyprint_time(
                                int(time.time()) - action[0]),
                           action=activity['action'],
                           user=activity['user'],
                           obj=activity['object'],
                           pbj_url=activity['object_url'],
                           parent=activity['parent'],
                           parent_url=activity['parent_url'])
                recentlist.append(actionlist)
        return recentlist

    def prettyprint_time(self, seconds):
        minutes = seconds/60
        days = minutes/1440
        hours = minutes/60 - (days * 24)
        exact_minutes = minutes - (hours * 60) - (days * 24 * 60)
        return {'days': days, 'hours': hours, 'minutes': exact_minutes}
