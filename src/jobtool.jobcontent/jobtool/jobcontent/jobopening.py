import json
import datetime
from Acquisition import aq_inner
from five import grok
from plone import api

from plone.directives import dexterity, form

from zope import schema
from zope.schema.vocabulary import getVocabularyRegistry

from plone.app.textfield import RichText

from plone.namedfile.interfaces import IImageScaleTraversable

from jobtool.jobcontent import MessageFactory as _


class IJobOpening(form.Schema, IImageScaleTraversable):
    """
    A job opening describing the vacancy
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Start date"),
        required=False,
    )
    jobtype = schema.Choice(
        title=_(u"Job Type"),
        vocabulary=u"jobtool.jobcontent.jobTypes",
        required=True,
    )
    institution = schema.Choice(
        title=_(u"Institution"),
        vocabulary=u"jobtool.jobcontent.jobInstitutions",
        required=True,
    )
    location = schema.Choice(
        title=_(u"Location"),
        vocabulary=u"jobtool.jobcontent.jobLocations",
        required=True,
    )
    locationOverride = schema.TextLine(
        title=_(u"Location Override"),
        required=False,
    )
    distributor = schema.List(
        title=_(u"Selected Distributors"),
        description=_(u"Select external distributors to filter display in "
                      u"the press archive listing"),
        value_type=schema.Choice(
            title=_(u"Distributor"),
            vocabulary='jobtool.jobcontent.externalDistributors',
        ),
        required=False,
    )
    category = schema.List(
        title=_(u"Category"),
        value_type=schema.Choice(
            title=_(u"Category Selection"),
            vocabulary=u"jobtool.jobcontent.jobCategory",
        ),
        required=True,
    )
    preview = schema.Bool(
        title=_(u"Preview"),
        description=_(u"Mark this job opening as available for preview pages"),
        required=False,
    )
    text = RichText(
        title=_(u"Job Description"),
        description=_(u"Enter Summary of the job opening"),
        required=True,
    )


@form.default_value(field=IJobOpening['start'])
def startDefaultValue(data):
    return datetime.datetime.today() + datetime.timedelta(7)


class JobOpening(dexterity.Item):
    grok.implements(IJobOpening)


class View(grok.View):
    grok.context(IJobOpening)
    grok.require('zope2.View')
    grok.name('view')

    def last_modified(self):
        context = aq_inner(self.context)
        modified = context.modified
        return api.portal.get_localized_time(datetime=modified)

    def pretty_jobtype(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        records = vr.get(context, 'jobtool.jobcontent.jobTypes')
        selected = getattr(context, 'jobtype', None)
        try:
            vocabterm = records.getTerm(selected)
            prettyname = vocabterm.title
        except KeyError:
            prettyname = selected
        return prettyname

    def pretty_category(self, category):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        records = vr.get(context, 'jobtool.jobcontent.jobCategory')
        try:
            vocabterm = records.getTerm(category)
            prettyname = vocabterm.title
        except KeyError:
            prettyname = category
        return prettyname

    def pretty_distributor(self, distributor):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        records = vr.get(context, 'jobtool.jobcontent.externalDistributors')
        try:
            vocabterm = records.getTerm(distributor)
            prettyname = vocabterm.title
        except KeyError:
            prettyname = distributor
        return prettyname

    def pretty_term(self, vocab, term):
        context = aq_inner(self.context)
        vocabulary = 'jobtool.jobcontent.' + vocab
        vr = getVocabularyRegistry()
        records = vr.get(context, vocabulary)
        try:
            vocabterm = records.getTerm(term)
            prettyname = vocabterm.title
        except KeyError:
            prettyname = term
        return prettyname

    def is_active(self):
        context = aq_inner(self.context)
        active = False
        current_state = api.content.get_state(obj=context)
        if current_state == 'published':
            active = True
        return active


class JobPreviewSettings(grok.View):
    grok.context(IJobOpening)
    grok.require('cmf.ModifyPortalContent')
    grok.name('update-job-preview')

    def update(self):
        context = aq_inner(self.context)
        state = self.request.form.get('state', '')
        results = {'results': None,
                   'success': False,
                   'message': ''
                   }
        if state:
            if state == 'true':
                setattr(context, 'preview', False)
                results['success'] = True
            else:
                setattr(context, 'preview', True)
                results['success'] = True
            results['results'] = {
                'state': 'changed',
                'transitions': (),
            }
        self.results = results

    def render(self):
        results = self.results
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(results)


class JobStateTransition(grok.View):
    grok.context(IJobOpening)
    grok.require('cmf.ModifyPortalContent')
    grok.name('update-job-state')

    def update(self):
        context = aq_inner(self.context)
        state = self.request.form.get('state', '')
        results = {'results': None,
                   'success': False,
                   'message': ''
                   }
        if state:
            transition = 'publish'
            if state == 'true':
                transition = 'retract'
            try:
                api.content.transition(obj=context, transition=transition)
                results['success'] = True
            except api.exc.InvalidParameterError, e:
                results['message'] = "%s" % e
            results['results'] = {
                'state': api.content.get_state(self.context),
                'counter': self.jobs_counter(),
            }
        self.results = results

    def render(self):
        results = self.results
        self.request.response.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return json.dumps(results)

    def jobs_counter(self):
        active = self.get_data(state='published')
        inactive = self.get_data(state='private')
        counter = [len(active), len(inactive)]
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

    def get_possible_transitions(self, item):
        """
        Return the posible transitions for an item. This should
        eventually get out of this tutorial, since its NASTY.
        """
        workflow_tool = api.portal.get_tool('portal_workflow')
        items = workflow_tool.getTransitionsFor(item)
        return [item['id'] for item in items]
