from zope.interface import alsoProvides
from zope import schema
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider

from pressapp.channelmanagement.vocabulary import ChannelSourceBinder

from pressapp.presscontent import MessageFactory as _


class IRecipients(form.Schema):
    """
       Marker/Form interface for Recipients
    """
    form.fieldset(
        'recipients',
        label=u"Recipients",
        fields=['channel', 'recipients'],
    )
    channel = schema.List(
        title=_(u"Channels"),
        description=_(u"Please select the channels this content should be "
                      u"dispatched to."),
        value_type=schema.TextLine(
            title=_(u"Channel"),
        ),
        required=False,
    )
    recipients = schema.List(
        title=_(u"Recipient List"),
        description=_(u"A customized channel/recipient list used for this "
                      u"single press content. Note: If you don't require "
                      u"any changes, it is faster to just keep the channels."),
        required=False,
        value_type=schema.TextLine(
            title=_(u"Recipient Details"),
        )
    )


alsoProvides(IRecipients, IFormFieldProvider)
