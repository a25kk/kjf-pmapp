from five import grok
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.component import queryUtility
from Products.CMFPlone.utils import safe_unicode
from z3c.formwidget.query.interfaces import IQuerySource
from plone.registry.interfaces import IRegistry


class ChannelSource(object):
    grok.implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        self.key = 'pressapp.channelmanagement.availableChannels'
        self.channel_list = self.getChannelList()
        self.vocab = self.createVocabulary(self.channel_list)

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

    def createVocabulary(self, channel_list):
        terms = []
        for value in channel_list:
            terms.append(SimpleVocabulary.createTerm(value, value.encode('utf-8'), value))
        return SimpleVocabulary(terms)


class ChannelSourceBinder(object):
    grok.implements(IContextSourceBinder)

    def __call__(self, context):
        return ChannelSource(context)
