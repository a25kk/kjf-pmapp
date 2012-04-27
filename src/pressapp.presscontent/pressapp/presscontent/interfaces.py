from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class IPressContent(Interface):
    """A general Interface to mark all press content """


class IPressAppPolicy(Interface):
    """ A marker inteface for a specific theme layer """
