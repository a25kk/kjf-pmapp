from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from zope.interface import Interface
from zope.component import getMultiAdapter
from plone import api

from plone.app.layout.viewlets.interfaces import IAboveContent
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent.interfaces import IJobTool


class ActionBar(grok.Viewlet):
    grok.name('jobtool.jobcontent.ActionBarViewlet')
    grok.context(Interface)
    grok.layer(IJobTool)
    grok.require('zope2.View')
    grok.viewletmanager(IAboveContent)

    def update(self):
        context = aq_inner(self.context)
        self.context_url = context.absolute_url()
        self.parent_url = aq_parent(context).absolute_url()
        self.portal_state = getMultiAdapter((context, self.request),
                                            name='plone_portal_state')
        self.anonymous = self.portal_state.anonymous()

    def jobcenter(self):
        portal = api.portal.get()
        return portal['jobcenter']

    def active_jobs(self):
        jobs = self.get_data(state='published')
        return len(jobs)

    def inactive_jobs(self):
        jobs = self.get_data(state='private')
        return len(jobs)

    def get_data(self, state=None):
        catalog = api.portal.get_tool(name='portal_catalog')
        query = self.base_query()
        if state is not None:
            query['review_state'] = state
        results = catalog.searchResults(**query)
        return results

    def base_query(self):
        obj_provides = IJobOpening.__identifier__
        return dict(object_provides=obj_provides,
                    sort_on='modified',
                    sort_order='reverse')
