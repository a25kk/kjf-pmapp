from five import grok
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabualryFactory

from pressapp.presscontent import MesageFactory as _


class DistributorsVocabulary(object):
    grok.implements(IVocabualryFactory)
