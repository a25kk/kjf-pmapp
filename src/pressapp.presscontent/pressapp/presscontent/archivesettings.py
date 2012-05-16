from five import grok
from Acquisition import aq_inner
from zope import schema
from zope.lifecycleevent import modified
from zope.component import getUtility
from zope.schema import getFieldsInOrder

from plone.directives import form
from z3c.form import button
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from pressapp.presscontent.pressrelease import IPressRelease

from pressapp.presscontent import MessageFactory as _


class IArchiveSettingsEdit(form.Schema):

    archive = schema.Bool(
        title=_(u"Visible in Archive?"),
        description=_(u"Mark this press release as visible in the archive."),
        required=False,
        default=True,
    )
    distributor = schema.List(
        title=_(u"Selected Dsitributors"),
        description=_(u"Select external distributors to filter display in "
                      u"the press archive listing"),
        value_type=schema.Choice(
            title=_(u"Distributor"),
            vocabulary='pressapp.presscontent.externalDistributors',
        ),
        required=False,
    )


class ArchiveSettingsEditForm(form.SchemaEditForm):
    grok.context(IPressRelease)
    grok.require('cmf.AddPortalContent')
    grok.name('archive-settings')

    schema = IArchiveSettingsEdit
    ignoreContext = False
    css_class = 'overlayForm'

    label = _(u"Edit archive setting")

    def updateActions(self):
        super(ArchiveSettingsEditForm, self).updateActions()
        self.actions['save'].addClass("btn")
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
            _(u"Editing has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressrelease')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        assert IPressRelease.providedBy(context)
        fti = getUtility(IDexterityFTI,
                name='pressapp.presscontent.pressrelease')
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
            _(u"Archive settings successfully updated"),
            type='info')
        return self.request.response.redirect(context.absolute_url() + '/view')
