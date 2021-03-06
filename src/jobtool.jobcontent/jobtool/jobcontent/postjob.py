from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from plone.dexterity.utils import createContentInContainer
from Products.statusmessages.interfaces import IStatusMessage
from jobtool.jobcontent.jobcenter import IJobCenter

from jobtool.jobcontent import MessageFactory as _


class IJobAdd(form.Schema):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )
    start = schema.Datetime(
        title=_(u"Start date"),
        required=True,
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


class JobAddForm(form.SchemaEditForm):
    grok.context(IJobCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('add-job')

    schema = IJobAdd
    ignoreContext = True
    css_class = 'overlayForm shop-form'

    label = _(u"Add new image attachment")

    def updateActions(self):
        super(JobAddForm, self).updateActions()
        self.actions['save'].addClass("btn btn-primary")
        self.actions['cancel'].addClass("btn")

    @button.buttonAndHandler(_(u"Add job opening"), name="save")
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

    def applyChanges(self, data):
        context = aq_inner(self.context)
        container = context
        item = createContentInContainer(
            container,
            'jobtool.jobcontent.jobopening',
            checkConstraints=True, **data)
        modified(item)
        item.reindexObject(idxs='modified')
        IStatusMessage(self.request).addStatusMessage(
            _(u"A new job opening has successfully been added"),
            type='info')
        next_url = item.absolute_url()
        return self.request.response.redirect(next_url)
