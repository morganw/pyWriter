from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pyWriter.lib.apps.story.models import Story, Chapter, Scene, Character, Artifact, Location, Getfeed 

import os
import shutil
import zipfile
from django.template import loader, Context

@login_required
def print_epub(request, story=None):
    context = {}
    if story:
        st = get_object_or_404(Story, pk=story, user=request.user)
        context['story'] = st
 
        ebookpath = os.path.join(settings.STATIC_ROOT, "library", "epub", str(st.pk))
        filename  = "%s.epub" % st.title
        zippath = os.path.join(ebookpath, filename)
        if os.path.exists(ebookpath):
            shutil.rmtree(ebookpath)
        
        os.makedirs(ebookpath)
        myfile = os.path.join(ebookpath, "index.html")
        f = file(myfile, "w")
        content = "\
        <html xmlns=\"http://www.w3.org/1999/xhtml\"> \
        <head>\
           <title>%s</title>\
        </head>\
        <body> \
        <h1>%s</h1> \
        </body>\
        </html>" % (st.title, st.title)
        f.write(content)
        f.close()      
                   
        filename  = "%s.epub" % st.title
        zippath = os.path.join(ebookpath, filename)
        epub = zipfile.ZipFile(zippath, 'w')

        # The first file must be named "mimetype"
        epub.writestr("mimetype", "application/epub+zip")

        # The filenames of the HTML are listed in html_files
        #html_files = ['foo.html', 'bar.html']
        html_files = [myfile,]

        counter = 0
        if st.get_chapters:
            for c in st.get_chapters:
                if c.get_scenes:
                    counter = counter+1
                    myfile = os.path.join(ebookpath, "%s.html" % str(counter))
                    f = file(myfile, "w")
                    content = "\
                    <html xmlns=\"http://www.w3.org/1999/xhtml\"> \
                    <head>\
                       <title>%s</title>\
                    </head>\
                    <body> \
                    <h1>%s</h1> \
                    </body>\
                    </html>" % (c, c)
                    f.write(content)
                    f.close()
                    html_files.append(myfile)
                    
                    for sc in c.get_scenes:
                        counter = counter+1
                        myfile = os.path.join(ebookpath, "%s.html" % str(counter))
                        f = file(myfile, "w")
                        content = "\
                        <html xmlns=\"http://www.w3.org/1999/xhtml\"> \
                        <head>\
                           <title>%s</title>\
                        </head>\
                        <body> \
                        <h1>%s</h1> \
                        %s \
                        </body>\
                        </html>" % (sc, sc, sc.content)
                        f.write(content)
                        f.close()
                        html_files.append(myfile)
                                
        # We need an index file, that lists all other HTML files
        # This index file itself is referenced in the META_INF/container.xml
        # file
        epub.writestr("META-INF/container.xml", '''<container version="1.0"
                   xmlns="urn:oasis:names:tc:opendocument:xmlns:container"> 
          <rootfiles>
            <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
          </rootfiles>
        </container>''');

        # The index file is another XML file, living per convention
        # in OEBPS/Content.xml
        index_tpl = '''<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/" unique-identifier="bookid" version="2.0"> 
          <metadata>
            <dc:title>%(title)s</dc:title>
            <dc:creator>%(author)s</dc:creator>
            <dc:identifier id="bookid">urn:isbn:%(uniqueid)s</dc:identifier>
            <dc:language>en-GB</dc:language>
          </metadata>
          <manifest>
            %(manifest)s
          </manifest>
          <spine toc=\"ncx\">
            %(spine)s
          </spine>
        </package>'''

        manifest = ""
        spine = ""


        # Write each HTML file to the ebook, collect information for the index
        for i, html in enumerate(html_files):
            basename = os.path.basename(html)
            manifest += '<item id="file_%s" href="%s" media-type="application/xhtml+xml"/>' % (
                          i+1, basename)
            spine += '<itemref idref="file_%s" />' % (i+1)
            epub.write(html, 'OEBPS/'+basename)

        uniquestring = "%s%s" % (st.title, st.author)
        # Finally, write the index
        epub.writestr('OEBPS/Content.opf', index_tpl % {
          'uniqueid': uniquestring,
          'title': st.title,
          'author': st.author,
          'manifest': manifest,
          'spine': spine,
        })
        
            
        

    context['booklink'] = zippath

    template = 'printing/print_epub.html'
    return render_to_response(template, context, context_instance=RequestContext(request))  
