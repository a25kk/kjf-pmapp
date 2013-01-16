from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from Products.CMFPlone.utils import safe_unicode

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage
from jobtool.jobcontent.jobopening import IJobOpening

from jobtool.jobcontent import MessageFactory as _


class IJobDistributorEdit(form.Schema):

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


class JobDistributorEditForm(form.SchemaEditForm):
    grok.context(IJobOpening)
    grok.require('cmf.AddPortalContent')
    grok.name('edit-job-distributors')

    schema = IJobDistributorEdit
    ignoreContext = False
    css_class = 'popover-form'

    label = _(u"Edit job opening distributors")

    def updateActions(self):
        super(JobDistributorEditForm, self).updateActions()
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
        if context.distributor is not None:
            data['distributor'] = [safe_unicode(k) for
                                   k in context.distributor]
        else:
            data['distributor'] = []
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
