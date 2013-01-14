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
        self.index_active = len(self.active_jobs())
        self.index_inactive = len(self.inactive_jobs())
        self.has_filter = self.request.get('filter', None)

    def filter_info(self):
        info = {}
        if self.has_filter:
            value = self.request.get('filter')
            if value == 'published':
                info['state'] = _(u"Active")
                info['klass'] = 'label label-success'
            else:
                info['state'] = _(u"Inactive")
                info['klass'] = 'label label-important'
        return info

    def active_jobs(self):
        jobs = self.get_data(state='published')
        return jobs

    def inactive_jobs(self):
        jobs = self.get_data(state='private')
        return jobs

    def job_listing(self):
        statefilter = self.request.get('filter', None)
        if statefilter is None:
            jobs = self.get_data()
        else:
            jobs = self.get_data(state=statefilter)
        return jobs

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


class Overview(grok.View):
    grok.context(IJobCenter)
    grok.require('cmf.ModifyPortalContent')
    grok.name('overview')

    def get_percental_value(self, index):
        jobs = self.jobs_index()
        one_percent = float(jobs) / 100
        if index == '0':
            index_value = index
        else:
            index_value = index / one_percent
        return str(index_value)

    def jobs_index(self):
        context = aq_inner(self.context)
        return len(context.items())

    def active_index(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='jobtool.jobcontent.jobopening',
            review_state='published')
        return len(items)

    def inactive_index(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='jobtool.jobcontent.jobopening',
            review_state='private')
        return len(items)


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
