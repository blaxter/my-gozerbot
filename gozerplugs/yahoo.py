# Yahoo! search
# (c) Wijnand 'tehmaze' Modderman - http://tehmaze.com
# (c) Leif Hedstrom <leif@ogre.com>, creator of pYsearch (License: BSD)

__author__ = 'Wijnand Modderman <gozerbot@tehmaze.com>'
__copyright__ = 'BSD'

import time
import urllib
import xml.dom.minidom
from gozerbot.aliases import aliases
from gozerbot.commands import cmnds
from gozerbot.generic import geturl, waitforqueue
from gozerbot.persist.persistconfig import PersistConfig
from gozerbot.plughelp import plughelp

plughelp.add('yahoo', 'query yahoo search engine')

cfg = PersistConfig()
cfg.define('appid', '')

# Function: string_to_bool
#   Convert a string argument to a boolean
#
# Parmeters:
#   s - The input string
#
# Returns:
#   bool
def string_to_bool(s):
    sb = {'false': False, 'true': True}
    if sb.has_key(s.lower()):
        return sb[s.lower()]
    return bool(s)

class YahooException(Exception):
    pass

class YahooError(Exception):
    pass

class YahooXMLError(Exception):
    pass

class YahooResultDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("Result object has no attribute '%s'" % key)

# Class: YahooResultParser
#   Parse the results found by a <YahooResultParser> 
class YahooResultParser(object):
    # Constructor: __init__
    # Parameters:
    #   service - ...
    #   res_dict - ...
    def __init__(self, service, res_dict=YahooResultDict):
        self._service = service
        self._total_results_available = 0
        self._total_results_returned = 0
        self._first_result_position = 0
        self._results = []
        self._res_dict = res_dict
        self._res_fields = []
        self._init_res_fields()

    def __iter__(self):
        return iter(self._results)

    def _init_res_fields(self):
        """Initialize the valid result fields."""
        self._res_fields = [('Title', None, None),
                            ('Summary', None, None),
                            ('Url', None, None),
                            ('ClickUrl', None, None)]

    def _get_results(self):
        """Get the results."""
        return self._results
    results = property(_get_results, None, None,
                       "The list of all results")

    def _get_service(self):
        """Get the service for this DOM parser."""
        return self._service
    def _set_service(self, service):
        """Set the service for this DOM parser."""
        self._service = service
    service = property(_get_service, _set_service, None,
                       "The Search Web Service object for this results parser")

    def parse_results(self, result_set):
        """Parse the results."""
        err = "Search Result class %s must implement a parse_result()" % (
            self._service.svc_name)
        raise ClassError(err)

    def _get_total_results_available(self):
        """Get the total number of results for the query."""
        return self._total_results_available

    def _get_total_results_returned(self):
        """Get the number of results returned."""
        return self._total_results_returned
    total_results_returned = property(_get_total_results_returned, None, None,
                                      "The number of results returned")
    totalResultsReturned = property(_get_total_results_returned, None, None,
                                    "The number of results returned")

    def _get_first_result_position(self):
        """Get the first result position."""
        return self._first_result_position
    first_result_position = property(_get_first_result_position, None, None,
                                     "The first result position")
    firstResultPosition = property(_get_first_result_position, None, None,
                                   "The first result position") 

class YahooDOMResultParser(YahooResultParser):
    """DomResultParser - Base class for Yahoo Search DOM result parsers

    This is a DOM specific parser that is used as a base class for all
    Yahoo Search result parsers. It obviously must implement the main entry
    entry point, parse_results().
    """
    def parse_results(self, dom_object):
        """This is a simple DOM parser for all Yahoo Search services. It
        expects to find a top-level node named ResultSet. This is the main
        entry point for the DOM parser, and it requires a properly con-
        structed DOM object (e.g. using minidom).
        """
        try:
            result_set = dom_object.getElementsByTagName('ResultSet')[0]
        except:
            raise YahooXMLError("DOM object has no ResultSet")
        self._parse_result_set(result_set)

    def _get_text(self, nodelist, casting=None):
        """Find all text nodes for the nodelist, and concatenate them
        into one resulting strings. This is a helper method for the
        DOM parser.
        """
        rcode = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rcode = rcode + node.data
        if casting is not None:
            if rcode == "":
                return rcode
            else:
                return casting(rcode)
        else:
            return rcode

    def _tag_to_list(self, node, tag, casting=None):
        """Turn a number of tag elements into a list of values."""
        ret = []
        if casting is not None:
            for item in node.getElementsByTagName(tag):
                ret.append(casting(self._get_text(item.childNodes)))
        else:
            for item in node.getElementsByTagName(tag):
                ret.append(self._get_text(item.childNodes))

    def _tags_to_dict(self, node, tags):
        """Internal method to parse and extract a list of tags from a
        particular node. We return a dict, which can potentially be empty.
        The tags argument is a list of lists, where each sub-list is

            (tag-name, default value/None, casting function/None)

        The default "type" of a value is string, so there is no reason
        to explicitly cast to a str.
        """
        res = self._res_dict()
        for tag in tags:
            elem = node.getElementsByTagName(tag[0])
            if elem:
                val = self._get_text(elem[0].childNodes, tag[2])
            elif tag[1] is not None:
                val = tag[1]
            else:
                raise parser.XMLError("Result is missing a %s node" % tag[0])
            res[tag[0]] = val
        return res

    def _id_attribute_to_dict(self, node):
        """Internal method to parse and extract a node value, which
        has an "id" attribute as well. This will return a result dict
        with two values:

            { 'Name' :  <node-text>, 'Id' : <id attribute> }
        """
        res = self._res_dict()
        res['Name'] = self._get_text(node.childNodes)
        node_id = node.attributes.getNamedItem('id')
        if node_id:
            res['Id'] = str(node_id.nodeValue)
        else:
            raise parser.XMLError("%s node has no id attribute" % node.nodeName)
        return res

    def _parse_list_node(self, node, tag):
        """Internal method to parse a result node, which contains one
        or more data nodes. Each such node is converted to a dict (see
        _id_attribute_to_dict), and we return a list of such dicts.
        """
        res = []
        for elem in node.getElementsByTagName(tag):
            res.append(self._id_attribute_to_dict(elem))
        return res

    def _parse_result_set(self, result_set):
        """Internal method to parse a ResultSet node"""
        attributes = result_set.attributes
        if not attributes:
            raise parser.XMLError("ResultSet has no attributes")

        attr = attributes.getNamedItem('totalResultsAvailable')
        if attr:
            self._total_results_available = int(attr.nodeValue)
        else:
            raise parser.XMLError("ResultSet has no totalResultsAvailable attr")
        attr = attributes.getNamedItem('totalResultsReturned')
        if attr:
            self._total_results_returned = int(attr.nodeValue)
        else:
            raise parser.XMLError("ResultSet has no totalResultsReturned attr")
        attr = attributes.getNamedItem('firstResultPosition')
        if attr:
            self._first_result_position = int(attr.nodeValue)
        else:
            raise parser.XMLError("ResultSet has no firstRestultPosition attr")
        for res in result_set.getElementsByTagName('Result'):
            self._results.append(self._parse_result(res))

    def _parse_result(self, result):
        """Internal method to parse one Result node"""
        return self._tags_to_dict(result, self._res_fields)

#
# The actual parsers
#

class YahooQueryImageSearch(YahooDOMResultParser):
    """ImageSearch - DOM parser for Image Search

    Each result is a dictionary populated with the extracted data from the
    XML results. The following keys are always available:

        Title            - The title of the image file.
        Summary          - Summary text associated with the image file.
        Url              - The URL for the image file or stream.
        ClickUrl         - The URL for linking to the image file.
        RefererUrl       - The URL of the web page hosting the content.
        FileSize         - The size of the file, in bytes.
        FileFormat       - One of bmp, gif, jpg or png.
        Thumbnail        - The URL of the thumbnail file.

    The following attributes are optional, and might not be set:

        Height           - The height of the image in pixels.
        Width            - The width of the image in pixels.
        Publisher        - The creator of the image file.
        Restrictions     - Provides any restrictions for this media
                           object. Restrictions include noframe and
                           noinline.
        Copyright        - The copyright owner.

    The Thumbnail is in turn another dictionary, which will have the
    following keys:

        Url             - URL of the thumbnail.
        Copyright        - The copyright owner.

    The Thumbnail is in turn another dictionary, which will have the
    following keys:

        Url             - URL of the thumbnail.
        Height          - Height of the thumbnail, in pixels (optional).
        Width           - Width of the thumbnail, in pixels (optional).


    Example:
        results = ws.parse_results(dom)
        for res in results:
            print "%s - %s bytes" % (res.Title, res.FileSize)
    """
    def _init_res_fields(self):
        """Initialize the valid result fields."""
        super(YahooQueryImageSearch, self)._init_res_fields()
        self._res_fields.extend((('RefererUrl', None, None),
                                 ('FileSize', None, int),
                                 ('FileFormat', None, None),
                                 ('Height', 0, int),
                                 ('Width', 0, int),
                                 ('Publisher', "", None),
                                 ('Restrictions', "", None),
                                 ('Copyright', "", None)))

    def _parse_result(self, result):
        """Internal method to parse one Result node"""
        res = super(YahooQueryImageSearch, self)._parse_result(result)
        node = result.getElementsByTagName('Thumbnail')
        if node:
            res['Thumbnail'] = self._tags_to_dict(node[0], (('Url', None, None),
                                                            ('Height', 0, int),
                                                            ('Width', 0, int)))
        else:
            raise parser.XMLError("ImageSearch DOM object has no Thumbnail")
        return res

class YahooQueryPageData(YahooDOMResultParser):
    """PageData - DOM parser for PageData results

        Title            - The title of the web page.
        Url              - The URL for the web page.
        ClickUrl         - The URL for linking to the page.

    """
    def _init_res_fields(self):
        """Initialize the valid result fields."""
        self._res_fields = [('Title', None, None),
                            ('Url', None, None),
                            ('ClickUrl', None, None)]

class YahooQueryWebSearch(YahooDOMResultParser):
    """WebSearch 

    Each result is a dictionary populated with the extracted data from the
    XML results. The following keys are always available:

        Title            - The title of the web page.
        Summary          - Summary text associated with the web page.
        Url              - The URL for the web page.
        ClickUrl         - The URL for linking to the page.

    The following attributes are optional, and might not be set:

        ModificationDate - The date the page was last modified, Unix time.
        MimeType         - The MIME type of the page.
        Cache            - The URL of the cached result, and its size.

    If present, the Cache value is in turn another dictionary, which will
    have the following keys:

        Url             - URL to cached data.
        Size            - Size of the cached entry, in bytes.
    """
    def _init_res_fields(self):
        """Initialize the valid result fields."""
        super(YahooQueryWebSearch, self)._init_res_fields()
        self._res_fields.extend((('ModificationDate', "", None),
                                 ('MimeType', "", None)))

    def _parse_result(self, result):
        """Internal method to parse one Result node"""
        res = super(YahooQueryWebSearch, self)._parse_result(result)
        node = result.getElementsByTagName('Cache')
        if node:
            res['Cache'] = self._tags_to_dict(node[0], (('Url', None, None),
                                                        ('Size', None, None)))
        else:
            res['Cache'] = None
        return res

class YahooQueryVideoSearch(YahooDOMResultParser):
    """VideoSearch - DOM parser for Video Search

    Each result is a dictionary populated with the extracted data from the
    XML results. The following keys are always available:

        Title            - The title of the video file.
        Summary          - Summary text associated with the video file.
        Url              - The URL for the video file or stream.
        ClickUrl         - The URL for linking to the video file.
        RefererUrl       - The URL of the web page hosting the content.
        FileSize         - The size of the file, in bytes.
        FileFormat       - One of avi, flash, mpeg, msmedia, quicktime
                           or realmedia.
        Duration         - The duration of the video file in seconds.
        Streaming        - Whether the video file is streaming or not.

    The following attributes are optional, and might not be set:

        Height           - The height of the keyframe Yahoo! extracted
                           from the video, in pixels.
        Width            - The width of the keyframe Yahoo! extracted
                           from the video, in pixels.
        Channels         - Channels in the audio stream.
        Thumbnail        - The URL of the thumbnail file.
        Publisher        - The creator of the video file.
        Restrictions     - Provides any restrictions for this media
                           object. Restrictions include noframe and
                           noinline.
        Copyright        - The copyright owner.

    If present, the Thumbnail value is in turn another dictionary, which will
    have these keys:

        Url             - URL of the thumbnail.
        Height          - Height of the thumbnail in pixels (optional).
        Width           - Width of the thumbnail in pixels (optional).


    Example:
        results = ws.parse_results(dom)
        for res in results:
            print "%s - %s bytes" % (res.Title, res.FileSize)
    """
    def _init_res_fields(self):
        """Initialize the valid result fields."""
        super(YahooQueryVideoSearch, self)._init_res_fields()
        self._res_fields.extend((('RefererUrl', None, None),
                                 ('FileSize', None, int),
                                 ('FileFormat', None, str),
                                 ('Height', 0, int),
                                 ('Width', 0, int),
                                 ('Streaming', None, string_to_bool),
                                 ('Duration', None, float),
                                 ('Channels', "", str),
                                 ('Publisher', "", None),
                                 ('Restrictions', "", str),
                                 ('Copyright', "", None)))

    def _parse_result(self, result):
        """Internal method to parse one Result node"""
        res = super(YahooQueryVideoSearch, self)._parse_result(result)
        node = result.getElementsByTagName('Thumbnail')
        if node:
            res['Thumbnail'] = self._tags_to_dict(node[0], (('Url', None, None),
                                                            ('Height', 0, int),
                                                            ('Width', 0, int)))
        else:
            res['Thumbnail'] = None
        return res

# Class: Yahoo
#   Generic interface to all YahooQuerySearch classes
class Yahoo:

    # Variable: meta
    #   Information about lookup methods, their YahooQuerySearch class and the base URL
    meta = {
        'ImageSearch': [YahooQueryImageSearch, 'http://search.yahooapis.com/ImageSearchService/V1/imageSearch'],  
        'PageData':    [YahooQueryPageData, 'http://search.yahooapis.com/SiteExplorerService/V1/pageData'],
        'VideoSearch': [YahooQueryVideoSearch, 'http://search.yahooapis.com/VideoSearchService/V1/videoSearch'],  
        'WebSearch':   [YahooQueryWebSearch, 'http://search.yahooapis.com/WebSearchService/V1/webSearch']
    }
    parser = None

    def _get(self, app, parameters):
        url  = self._url(app, parameters)
        data = geturl(url)
        return self._parse(app, data)

    def _parse(self, app, data):
        if not self.parser:
            self.parser = xml.dom.minidom.parseString
        xmlobj = self.parser(data)
        parser = self.meta[app][0](app)
        parser.parse_results(xmlobj)
        return parser

    def _url(self, app, parameters={}):
        if not self.meta.has_key(app):
            raise YahooException('Invalid service "%s"' % app)
        if not cfg.get('appid'):
            raise YahooException('No appid configured, see http://developer.yahoo.com/search/')
        parameters['appid'] = cfg.get('appid')
        return '%s?%s' % (self.meta[app][1], urllib.urlencode(parameters))

    # Function: imageSearch
    #   Search for an image by keyword on the web
    #
    # Parameters:
    #   query - keywords to search for
    #   format - image format to filter on
    #   adult_ok - include adult content in the search result
    #   results - limit the number of results
    #
    # Returns:
    #   results
    def imageSearch(self, query, format='any', adult_ok=0, results=10):
        return self._get('ImageSearch', {'query': query, 'format': format, 'results': results, 'adult_ok': adult_ok})

    def pageData(self, website, results=10):
        return self._get('PageData', {'query': website, 'results': results})

    # Function: webSearch
    #   Search for a keyword on the web
    #
    # Parameters:
    #   query - keywords to search for
    #   results - limit the number of results
    #
    # Returns:
    #   results
    def webSearch(self, query, results=10):
        return self._get('WebSearch', {'query': query, 'results': results})

    # Function: videoSearch
    #   Search for an video by keyword on the web
    #
    # Parameters:
    #   query - keywords to search for
    #   format - video format to filter on
    #   adult_ok - include adult content in the search result
    #   results - limit the number of results
    #
    # Returns:
    #   results
    def videoSearch(self, query, format='any', adult_ok=0, results=10):
        return self._get('VideoSearch', {'query': query, 'format': format, 'results': results, 'adult_ok': adult_ok})

yahoo = Yahoo()

def handle_yahoo_image(bot, ievent):
    adult_ok = 0
    format = ''
    formats = ['any', 'all', 'bmp', 'gif', 'jpeg', 'png']
    args = ievent.args
    try:
        if '--adult' in args:
            adult_ok = 1
            args.remove('--adult')
        if '--format' in args:
            format = args.pop(args.index('--format')+1)
            args.remove('--format')
    except ValueError:
        ievent.missing('[--adult] [--format [<format>] <query>')
        return
    if not ievent.args:
        ievent.missing('[--adult] [--format [<format>] <query>')
        return
    if format and not format in formats:
        ievent.reply('invalid format, available formats: %s' % ', '.join(formats))
        return
    try:
        search = yahoo.imageSearch(' '.join(args), format, adult_ok)
    except YahooException, e:
        ievent.reply(str(e))
        return
    if search._total_results_returned > 0:
        ievent.reply('search for %s ==> %d results available, showing 1 - %d' % \
            (' '.join(args), search._total_results_available,
            search._total_results_returned))
        reply = []
        for result in search._get_results():
             reply.append('%d) %s - %s' % (len(reply)+1, result.Title, result.Url))
        ievent.reply(', '.join(reply))
    else:
        ievent.reply('search for %s ==> no results' % ' '.join(args))

cmnds.add('yahoo-image', handle_yahoo_image, 'USER')

def handle_yahoo_search(bot, ievent):
    if ievent.inqueue:
        text = ' '.join(waitforqueue(ievent.inqueue, 5))
    elif not ievent.args:
        ievent.missing('<query>')
        return
    else:
        text = ' '.join(ievent.args)
    try:
        search = yahoo.webSearch(text)
    except YahooException, e:
        ievent.reply(str(e))
        return
    if search._total_results_returned > 0:
        ievent.reply('search for %s ==> %d results available, showing 1 - %d' % \
            (text, search._total_results_available,
            search._total_results_returned))
        reply = []
        for result in search._get_results():
             reply.append('%d) %s - %s' % (len(reply)+1, result.Title, result.Url))
        ievent.reply(', '.join(reply))
    else:
        ievent.reply('search for %s ==> no results' % ' '.join(ievent.args))

cmnds.add('yahoo-search', handle_yahoo_search, 'USER')
aliases.data['y!'] = 'yahoo-search'
aliases.data['yahoo'] = 'yahoo-search'

def handle_yahoo_pagedata(bot, ievent):
    if not ievent.args:
        ievent.missing('<url>')
        return
    try:
        search = yahoo.pageData(' '.join(ievent.args))
    except YahooException, e:
        ievent.reply(str(e))
        return
    if search._total_results_returned > 0:
        reply = []
        for result in search._get_results():
            reply.append('%d) %s, %dx%d px - %s' % (len(reply)+1, result.Title, 
            result.Width, result.Height, result.Url))
        ievent.reply(', '.join(reply))
    else:
        ievent.reply('pagedata for %s ==> no results' % ' '.join(ievent.args))

cmnds.add('yahoo-pagedata', handle_yahoo_pagedata, ['USER'])


def handle_yahoo_video(bot, ievent):
    adult_ok = 0
    format = ''
    formats = ['any', 'all', 'avi', 'flash', 'mpeg', 'msmedia', 'quicktime', 'realmedia']
    args = ievent.args
    try:
        if '--adult' in args:
            adult_ok = 1
            args.remove('--adult')
        if '--format' in args:
            format = args.pop(args.index('--format')+1)
            args.remove('--format')
    except ValueError:
        ievent.missing('[--adult] [--format [<format>] <query>')
        return
    if not ievent.args:
        ievent.missing('[--adult] [--format [<format>] <query>')
        return
    if format and not format in formats:
        ievent.reply('invalid format, available formats: %s' % ', '.join(formats))
        return
    try:
        search = yahoo.videoSearch(' '.join(args), format, adult_ok)
    except YahooException, e:
        ievent.reply(str(e))
        return
    if search._total_results_returned > 0:
        ievent.reply('search for %s ==> %d results available, showing 1 - %d' % \
            (' '.join(args), search._total_results_available,
            search._total_results_returned))
        reply = []
        for result in search._get_results():
             reply.append('%d) %s, %dx%d, %s - %s' % (len(reply)+1, result.Title, 
             result.Width, result.Height, time.strftime('%T', time.localtime(result.Duration)), result.Url))
        ievent.reply(', '.join(reply))
    else:
        ievent.reply('search for %s ==> no results' % ' '.join(args))

cmnds.add('yahoo-video', handle_yahoo_video, 'USER')

