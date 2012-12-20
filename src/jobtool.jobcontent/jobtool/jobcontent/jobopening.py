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
    jobtype = schema.Choice(
        title=_(u"Job Type"),
        vocabulary=u"jobtool.jobcontent.jobTypes",
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
