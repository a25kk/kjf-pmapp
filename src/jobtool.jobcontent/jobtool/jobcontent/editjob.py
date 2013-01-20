from five import grok
from Acquisition import aq_inner
from zope import schema
from plone import api

from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from zope.schema.vocabulary import getVocabularyRegistry

from plone.app.textfield import RichText

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class IJobEdit(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    jobtype = schema.Choice(
        title=_(u"Job Type"),
        vocabulary=u"jobtool.jobcontent.jobTypes",
        required=True,
    )
    organization = schema.Choice(
        title=_(u"Organization"),
        vocabulary=u"jobtool.jobcontent.jobInstitutions",
        required=True,
    )
    institution = schema.TextLine(
        title=_(u"Institution"),
        required=True,
    )
    location = schema.TextLine(
        title=_(u"Location"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Start date"),
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


class IJobSummaryEdit(form.Schema):

    text = RichText(
        title=_(u"Job Description"),
        description=_(u"Enter Summary of the job opening"),
        required=True,
    )


class JobEditForm(form.SchemaEditForm):
    grok.context(IJobOpening)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-job-opening')

    schema = IJobEdit
    ignoreContext = False
    css_class = 'shop-form'

    label = _(u"Edit orderable item")

    def updateActions(self):
        super(JobEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Orderable item edit has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobopening')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobopening')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The job opening has successfully been updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')

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

    def is_active(self):
        context = aq_inner(self.context)
        active = False
        current_state = api.content.get_state(obj=context)
        if current_state == 'published':
            active = True
        return active


class JobSummaryEditForm(form.SchemaEditForm):
    grok.context(IJobOpening)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-job-summary')

    schema = IJobSummaryEdit
    ignoreContext = False
    css_class = 'shop-form'

    label = _(u"Edit job opening")

    def updateActions(self):
        super(JobSummaryEditForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Save"), name="save")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)

    @button.buttonAndHandler(_(u"cancel"))
    def handleCancel(self, action):
        context = aq_inner(self.context)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Summary edit has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobopening')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobopening')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        for key, value in fields:
            try:
                new_value = data[key]
                setattr(context, key, new_value)
            except KeyError:
                continue
        modified(context)
        context.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"The job opening has successfully been updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')

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
