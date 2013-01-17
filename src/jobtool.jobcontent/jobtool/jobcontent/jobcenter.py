import json
from five import grok
from Acquisition import aq_inner
from zope import schema
from plone import api

from plone.directives import dexterity, form

from zope.schema.vocabulary import getVocabularyRegistry
from plone.app.layout.viewlets.content import ContentHistoryView

from plone.namedfile.interfaces import IImageScaleTraversable

from plone.app.contentlisting.interfaces import IContentListing

from Products.CMFCore.interfaces import IContentish
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class IJobCenter(form.Schema, IImageScaleTraversable):
    """
    Folderish jobcenter and managing unit
    """
    institution = schema.List(
        title=_(u"Institutions"),
        value_type=schema.TextLine(
            title=_(u"Institution"),
        ),
        required=False,
    )


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
                info['klass'] = 'success'
            else:
                info['state'] = _(u"Inactive")
                info['klass'] = 'important'
        return info

    def jobs_index(self):
        return len(self.job_listing())

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

    def get_state_info(self, state):
        info = _(u"Inactive")
        if state == 'published':
            info = _(u"Active")
        return info


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
        index = round(float(index_value))
        return str(index)

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

    def get_history(self):
        context = aq_inner(self.context)
        history = context.restrictedTraverse('@@changes').jobtool_history()
        return history


class Settings(grok.View):
    grok.context(IJobCenter)
    grok.require('cmf.ModifyPortalContent')
    grok.name('settings')

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

    def distributor_list(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        records = vr.get(context, 'jobtool.jobcontent.externalDistributors')
        terms = []
        for r in records:
            info = {}
            info['term'] = r.title
            info['token'] = r.value
            terms.append(info)
        return terms

    def get_history(self):
        context = aq_inner(self.context)
        history = context.restrictedTraverse('@@changes').jobtool_history()
        return history


class JoblistingSettings(grok.View):
    grok.context(IJobCenter)
    grok.require('cmf.ModifyPortalContent')
    grok.name('settings-joblisting')

    def update(self):
        self.has_items = len(self.preview_items()) > 0

    def jobs_index(self):
        context = aq_inner(self.context)
        return len(context.items())

    def preview_index(self):
        return len(self.preview_items())

    def preview_items(self):
        context = aq_inner(self.context)
        items = context.restrictedTraverse('@@folderListing')(
            portal_type='jobtool.jobcontent.jobopening',
            preview=True,
            review_state='published')
        return items

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

    def get_state_info(self, state):
        info = _(u"Inactive")
        if state == 'published':
            info = _(u"Active")
        return info

    def get_history(self):
        context = aq_inner(self.context)
        history = context.restrictedTraverse('@@changes').jobtool_history()
        return history


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


class JobCenterHistory(grok.View):
    grok.context(IJobCenter)
    grok.require('cmf.ModifyPortalContent')
    grok.name('changes')

    def render(self):
        data = self.jobtool_history()
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(data)

    def jobtool_history(self):
        history = []
        status = self.status_list()
        timestamps = list()
        for x in status:
            pit = x['timestamp']
            timestamps.append(pit)
        pit_sorted = sorted(timestamps, reverse=True)
        for pit in pit_sorted:
            for x in status:
                if x['timestamp'] == pit:
                    history.append(x)
        return history

    def status_list(self):
        items = self.last_modified_jobs()
        state_info = []
        idx = 0
        for item in items:
            obj = item.getObject()
            history = self.history_info(obj)
            if len(history) > 0:
                event = history[0]
                idx += 1
                info = {}
                info['idx'] = idx
                timestamp = event['time']
                time = api.portal.get_localized_time(datetime=timestamp,
                                                     long_format=False)
                time_only = api.portal.get_localized_time(datetime=timestamp,
                                                          time_only=True)
                info['time'] = time
                info['time_only'] = time_only
                info['timestamp'] = timestamp.ISO8601()
                actor = event['actor']
                info['actor'] = actor['username']
                info['action'] = event['transition_title']
                info['title'] = item.Title
                info['url'] = item.getURL()
                #info['details'] = event
                state_info.append(info)
        return state_info

    def history_info(self, item):
        context = aq_inner(self.context)
        chv = ContentHistoryView(item, context.REQUEST).fullHistory()
        return chv

    def last_modified_jobs(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IJobOpening.__identifier__,
                          sort_on='modified',
                          sort_order='reverse',
                          sort_limit=5)[:5]
        return results
