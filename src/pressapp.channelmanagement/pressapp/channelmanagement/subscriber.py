from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import queryUtility
from zope.interface import invariant, Invalid

from z3c.form import group, field
from z3c.formwidget.query.interfaces import IQuerySource
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.registry.interfaces import IRegistry

from pressapp.channelmanagement import MessageFactory as _


class ChannelSource(object):
    grok.implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        self.key = 'pressapp.channelmanagement.availableChannels'
        self.channel_list = self.getChannelList()
        self.vocab = SimpleVocabulary.fromItems(
            [(x, x) for x in self.channel_list])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        return self.vocab.getTerm(value)

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [self.getTerm(kw)
                for kw in self.channel_list if q in kw.lower()]

    def getChannelList(self):
        registry = queryUtility(IRegistry)
        terms = []
        if registry:
            for value in registry.get(self.key, ()):
                terms.append(value)
        return terms


class ChannelSourceBinder(object):
    grok.implements(IContextSourceBinder)

    def __call__(self, context):
        return ChannelSource(context)


class ISubscriber(form.Schema):
    """
    A single recipient/subscriber object
    """
    title = schema.TextLine(
        title=_(u"Contact Title"),
        required=True,
    )
    email = schema.TextLine(
        title=_(u"Email"),
        required=True,
    )
    contact = schema.TextLine(
        title=_(u"Contact Person"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    mobile = schema.TextLine(
        title=_(u"Mobile Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    comment = schema.Text(
        title=_(u"Comment"),
        required=False,
    )
    form.widget(channel=AutocompleteMultiFieldWidget)
    channel = schema.List(
        title=_(u"Channels"),
        description=_(u"Please select the channels this recipient "
                      u"is subscribed to."),
        value_type=schema.Choice(
            title=_(u"Channel"),
            source=ChannelSourceBinder(),
        )
    )


class View(grok.View):
    grok.context(ISubscriber)
    grok.require('zope2.View')
    grok.name('view')
