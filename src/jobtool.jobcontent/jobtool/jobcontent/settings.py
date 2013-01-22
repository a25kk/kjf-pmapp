from five import grok
from Acquisition import aq_inner
from zope import schema
from plone import api

from zope.schema import getFieldsInOrder
from zope.component import getUtility

from zope.lifecycleevent import modified

from plone.directives import form
from z3c.form import button

from plone.dexterity.interfaces import IDexterityFTI
from Products.statusmessages.interfaces import IStatusMessage
from jobtool.jobcontent.jobcenter import IJobCenter

from jobtool.jobcontent import MessageFactory as _


class ISettingsEdit(form.Schema):

    institutions = schema.List(
        title=_(u"Institutions"),
        description=_(u"Enter a list of institutions (one entry per line) "
                      u"that should be selectable in job opening edit forms"),
        value_type=schema.TextLine(
            title=_(u"Institution"),
        ),
        required=False,
    )
    locations = schema.List(
        title=_(u"Available Locations"),
        description=_(u"Provide a list of locations (one entry per line) that "
                      u"will be available to job opening edit forms as "
                      u"selection vocabulary"),
        value_type=schema.TextLine(
            title=_(u"Location"),
        ),
        required=False,
    )


class IPreviewSettingsEdit(form.Schema):

    width = schema.TextLine(
        title=_(u"Width Preview"),
        required=False,
    )
    limit = schema.TextLine(
        title=_(u"Limit Preview Display"),
        required=False,
    )


class SettingsEditForm(form.SchemaEditForm):
    grok.context(IJobCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('settings-jobtool')

    schema = ISettingsEdit
    ignoreContext = False
    css_class = 'shop-form'

    label = _(u"Edit jobcenter settings")

    def updateWidgets(self):
        super(SettingsEditForm, self).updateWidgets()
        self.widgets['institutions'].rows = 8
        self.widgets['locations'].rows = 8

    def updateActions(self):
        super(SettingsEditForm, self).updateActions()
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
            _(u"Update of jobcenter settings has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobcenter')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobcenter')
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
            _(u"Jobcenter settings successfully updated"),
            type='info')
        next_url = context.absolute_url() + '/@@settings'
        return self.request.response.redirect(next_url)


class PreviewSettingsEditForm(form.SchemaEditForm):
    grok.context(IJobCenter)
    grok.require('cmf.AddPortalContent')
    grok.name('settings-preview')

    schema = IPreviewSettingsEdit
    ignoreContext = False
    css_class = 'shop-form'

    label = _(u"Edit jobcenter settings")

    def updateActions(self):
        super(PreviewSettingsEditForm, self).updateActions()
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
            _(u"Jobcenter update has been cancelled."),
            type='info')
        return self.request.response.redirect(context.absolute_url())

    def getContent(self):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobcenter')
        schema = fti.lookupSchema()
        fields = getFieldsInOrder(schema)
        data = {}
        for key, value in fields:
            data[key] = getattr(context, key, value)
        return data

    def applyChanges(self, data):
        context = aq_inner(self.context)
        fti = getUtility(IDexterityFTI,
                         name='jobtool.jobcontent.jobcenter')
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
            _(u"Jobcenter preview settings successfully updated"),
            type='info')
        next_url = context.absolute_url() + '/@@settings'
        return self.request.response.redirect(next_url)
