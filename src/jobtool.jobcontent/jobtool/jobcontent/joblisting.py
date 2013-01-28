import json
import random
from Acquisition import aq_inner
from five import grok
from plone import api

from zope.schema.vocabulary import getVocabularyRegistry

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.contentlisting.interfaces import IContentListing
from jobtool.jobcontent.jobopening import IJobOpening


class JobListing(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('joblisting')

    def update(self):
        self.has_items = len(self.active_jobs()) > 0

    def active_jobs(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        dist_id = self.request.get('distid', None)
        if dist_id:
            results = catalog(object_provides=IJobOpening.__identifier__,
                              review_state='published',
                              archive=True,
                              distributor=dist_id,
                              sort_on='modified',
                              sort_order='reverse')
        else:
            results = catalog(object_provides=IJobOpening.__identifier__,
                              review_state='published',
                              archive=True,
                              sort_on='modified',
                              sort_order='reverse')
        resultlist = IContentListing(results)
        return resultlist

    def pretty_term(self, vocab, term):
        context = aq_inner(self.context)
        vocabulary = 'jobtool.jobcontent.' + vocab
        vr = getVocabularyRegistry()
        records = vr.get(context, vocabulary)
        try:
            vocabterm = records.getTerm(term)
            prettyname = vocabterm.title
        except (LookupError, KeyError):
            prettyname = term
        return prettyname


class JobDetails(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('jobdetails')

    def update(self):
        self.has_jobinfo = self.has_job()

    def has_job(self):
        job = self.resolve_job()
        return job

    def resolve_job(self):
        uid = self.request.get('juid', '')
        if uid:
            obj = api.content.get(UID=uid)
            return obj

    def pretty_term(self, vocab, term):
        context = aq_inner(self.context)
        vocabulary = 'jobtool.jobcontent.' + vocab
        vr = getVocabularyRegistry()
        records = vr.get(context, vocabulary)
        try:
            vocabterm = records.getTerm(term)
            prettyname = vocabterm.title
        except (LookupError, KeyError):
            prettyname = term
        return prettyname


class JobListingSnippetJSON(grok.View):
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('joblisting-snippet-json')

    def update(self):
        self.has_snippet = len(self._getData()) > 0
        self.callback_param = self.request.get('callback', None)

    def render(self):
        snippet_info = self.compose_snippet()
        snippet = {'snippet': snippet_info}
        self.request.response.setHeader("Content-type", "application/json")
        if self.callback_param is None:
            return json.dumps(snippet)
        else:
            json_snippet = json.dumps(snippet)
            return '%s(%s)' % (self.callback_param, json_snippet)

    def compose_snippet(self):
        pressreleases = self._getData()
        release = random.choice(pressreleases)
        obj = release.getObject()
        uuid = api.content.get_uuid(obj=obj)
        portal_url = api.portal.get().absolute_url()
        obj_url = portal_url + '/@@jobdetails?juid=' + uuid
        job_start = api.portal.get_localized_time(datetime=obj.start,
                                                  long_format=False)
        if obj.locationOverride:
            job_location = obj.locationOverrride
        else:
            job_location = self.pretty_term('jobLocations', obj.location)
        item = {}
        item['title'] = obj.Title()
        item['url'] = obj_url
        item['institution'] = self.pretty_term('jobInstitutions',
                                               obj.institution)
        item['location'] = job_location
        item['type'] = self.pretty_term('jobTypes', obj.jobtype)
        item['date'] = job_start
        return item

    def _getData(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        results = catalog(object_provides=IJobOpening.__identifier__,
                          review_state='published',
                          preview=True,
                          sort_on='start',
                          sort_order='reverse',
                          sort_limit=10)[:10]
        return results

    def pretty_term(self, vocab, term):
        context = aq_inner(self.context)
        vocabulary = 'jobtool.jobcontent.' + vocab
        vr = getVocabularyRegistry()
        records = vr.get(context, vocabulary)
        try:
            vocabterm = records.getTerm(term)
            prettyname = vocabterm.title
        except (LookupError, KeyError):
            prettyname = term
        return prettyname
