import json
from five import grok
from Acquisition import aq_inner
from plone import api

from plone.directives import dexterity, form

from zope.schema.vocabulary import getVocabularyRegistry

from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.contentlisting.interfaces import IContentListing

from Products.CMFCore.interfaces import IContentish
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class IJobCenter(form.Schema, IImageScaleTraversable):
    """
    Folderish jobcenter and managing unit
    """


class JobCenter(dexterity.Container):
    grok.implements(IJobCenter)


class View(grok.View):
    grok.context(IJobCenter)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.has_jobs = len(self.get_data()) > 0

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
        brains = catalog.searchResults(**query)
        results = IContentListing(brains)
        return results

    def base_query(self):
        obj_provides = IJobOpening.__identifier__
        return dict(object_provides=obj_provides,
                    sort_on='modified',
                    sort_order='reverse')

    def pretty_jobtype(self, jobtype):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        records = vr.get(context, 'jobtool.jobcontent.jobTypes')
        selected = jobtype
        try:
            vocabterm = records.getTerm(selected)
            prettyname = vocabterm.title
        except KeyError:
            prettyname = selected
        return prettyname


class JobsCounterJSON(grok.View):
    grok.context(IContentish)
    grok.require('zope2.View')
    grok.name('json-jobs-counter')

    def render(self):
        data = self.jobs_counter()
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)

    def jobs_counter(self):
        active = self.get_data(state='published')
        inactive = self.get_data(state='private')
        counter = {'active_idx': len(active),
                   'inactive_idx': len(inactive)}
        return counter

    def get_data(self, state=None):
        catalog = api.portal.get_tool(name='portal_catalog')
        query = self.base_query()
        if state is not None:
            query['review_state'] = state
        brains = catalog.searchResults(**query)
        return brains

    def base_query(self):
        obj_provides = IJobOpening.__identifier__
        return dict(object_provides=obj_provides,
                    sort_on='modified',
                    sort_order='reverse')
