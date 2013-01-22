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
