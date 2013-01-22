from zope.interface import Interface


class IJobContent(Interface):
    """A general Interface to mark all jobtool content """


class IJobTool(Interface):
    """ A marker inteface for a specific theme layer """
