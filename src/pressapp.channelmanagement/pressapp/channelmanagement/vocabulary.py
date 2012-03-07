from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.component import queryUtility
from z3c.formwidget.query.interfaces import IQuerySource
from plone.registry.interfaces import IRegistry


class ChannelSource(object):
    grok.implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        self.key = 'pressapp.channelmanagement.channelList'
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
        return [self.getTerm(kw['name'])
                for kw in self.channel_list if q in kw['name'].lower()]

    def getChannelList(self):
        registry = queryUtility(IRegistry)
        terms = []
        if registry:
            records = registry[self.key]
            for item in records:
                term = {}
                term['name'] = item
                term['title'] = records[item]
                terms.append(term)
        return terms

    def createVocabulary(self, channel_list):
        terms = []
        for value in channel_list:
            terms.append(SimpleTerm(value=value['name'],
                title=value['title'].encode('utf-8')))
        return SimpleVocabulary(terms)


class ChannelSourceBinder(object):
    grok.implements(IContextSourceBinder)

    def __call__(self, context):
        return ChannelSource(context)


class ChannelVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        registry = queryUtility(IRegistry)
        terms = []
        if registry is not None:
            records = registry['pressapp.channelmanagement.channelList']
            for channel in records:
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleTerm(
                    value=channel, title=records[channel].encode('utf-8')))
        return SimpleVocabulary(terms)
grok.global_utility(ChannelVocabulary,
    name=u"pressapp.channelmanagement.channellisting")
