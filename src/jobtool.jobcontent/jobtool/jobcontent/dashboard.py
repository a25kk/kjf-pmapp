from five import grok
from Acquisition import aq_inner

from plone.app.layout.navigation.interfaces import INavigationRoot
from jobtool.jobcontent.interfaces import IJobTool


class JobcenterDashboard(grok.View):
    grok.context(INavigationRoot)
    grok.layer(IJobTool)
    grok.require('cmf.ModifyPortalContent')
    grok.name('jobcenter-dashboard')
