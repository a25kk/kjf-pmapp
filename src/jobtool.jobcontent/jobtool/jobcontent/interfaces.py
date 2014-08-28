# -*- coding: UTF-8 -*-
""" Jobtool interfaces"""

from zope import schema
from zope.interface import Interface
from jobtool.jobcontent import MessageFactory as _


class IJobContent(Interface):
    """A general Interface to mark all jobtool content """


class IJobTool(Interface):
    """ A marker inteface for a specific theme layer """


class IJobToolSettings(Interface):
    """ Job tool settings stored in the registry """
    api_access_keys = schema.Tuple(
        title=_(u"API Access Keys"),
        value_type=schema.TextLine(
            title=_(u"Access key")
        ),
        required=False,
        missing_value=(),
    )
