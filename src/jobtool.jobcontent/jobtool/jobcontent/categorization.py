from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button
from zope.schema.vocabulary import getVocabularyRegistry

from Products.CMFPlone.utils import safe_unicode

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class IJobCategoryEdit(form.Schema):

    category = schema.Set(
        title=_(u"Category"),
        value_type=schema.Choice(
            title=_(u"Category Selection"),
            vocabulary=u"jobtool.jobcontent.jobCategory",
        ),
        required=True,
    )


class JobCategoryEditForm(form.SchemaEditForm):
    grok.context(IJobOpening)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-job-categorization')

    schema = IJobCategoryEdit
    ignoreContext = False
    css_class = 'popover-form'

    label = _(u"Edit job opening categorization")

    def updateActions(self):
        super(JobCategoryEditForm, self).updateActions()
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
            _(u"Process has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        data = {}
        if context.category is not None:
            data['category'] = [safe_unicode(k) for k in context.category]
        else:
            data['category'] = []
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
