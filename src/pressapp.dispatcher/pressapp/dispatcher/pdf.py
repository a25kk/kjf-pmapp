import os
from Globals import InitializeClass
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.Iterators import filestream_iterator
from zopyx.smartprintng.plone.browser.pdf import ProducePublishView


class CustomProducePublishView(ProducePublishView):
    """ Subclass of the Produce & Publish view
        registered for our own browser layer
    """

    template = ViewPageTemplateFile(
        'resources_pdf/pdf_template_standalone.pt')

    # default transformations used for the default PDF view.
    # 'transformations' can be overriden within a derived ProducePublishView.
    # If you don't need any transformation -> redefine 'transformations'
    # as empty list or tuple

    transformations = (
        'makeImagesLocal',
#        'removeEmptyElements',
#        'removeInternalLinks',
#        'annotateInternalLinks',
#        'cleanupTables',
        'convertFootnotes',
        'removeCrapFromHeadings',
        'fixHierarchies',
#        'addTableOfContents',
        )


class CustomPDFDownloadView(CustomProducePublishView):

    def __call__(self, *args, **kw):

        if not 'resource' in kw:
            kw['resource'] = 'pp-default'
        if not 'template' in kw:
            kw['template'] = 'pdf_template_standalone'
        kw['no-split'] = True
        import pdb; pdb.set_trace( )
        output_file = super(PDFDownloadView, self).__call__(*args, **kw)
        mimetype = os.path.splitext(os.path.basename(output_file))[1]
        R = self.request.response
        R.setHeader('content-type', 'application/%s' % mimetype)
        R.setHeader('content-disposition',
            'attachment; filename="%s.%s"' % (self.context.getId(), mimetype))
        R.setHeader('pragma', 'no-cache')
        R.setHeader('cache-control', 'no-cache')
        R.setHeader('Expires', 'Fri, 30 Oct 1998 14:19:41 GMT')
        R.setHeader('content-length', os.path.getsize(output_file))
        return filestream_iterator(output_file, 'rb').read()

InitializeClass(CustomPDFDownloadView)
