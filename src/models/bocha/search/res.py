class WebPage:
    def __init__(self, id=None, name=None, url=None, displayUrl=None, snippet=None, summary=None, siteName=None, siteIcon=None, datePublished=None, dateLastCrawled=None, cachedPageUrl=None, language=None, isFamilyFriendly=None, isNavigational=None):
        self.id = id
        self.name = name
        self.url = url
        self.displayUrl = displayUrl
        self.snippet = snippet
        self.summary = summary
        self.siteName = siteName
        self.siteIcon = siteIcon
        self.datePublished = datePublished
        self.dateLastCrawled = dateLastCrawled
        self.cachedPageUrl = cachedPageUrl
        self.language = language
        self.isFamilyFriendly = isFamilyFriendly
        self.isNavigational = isNavigational

class Images:
    def __init__(self, id=None, readLink=None, webSearchUrl=None, value=None, isFamilyFriendly=None):
        self.id = id
        self.readLink = readLink
        self.webSearchUrl = webSearchUrl
        self.value = [Image(**img) for img in value]
        self.isFamilyFriendly = isFamilyFriendly


class Image:
    def __init__(self, webSearchUrl=None, name=None, thumbnailUrl=None, datePublished=None, contentUrl=None, hostPageUrl=None, contentSize=None, encodingFormat=None, hostPageDisplayUrl=None, width=None, height=None, thumbnail=None):
        self.webSearchUrl = webSearchUrl
        self.name = name
        self.thumbnailUrl = thumbnailUrl
        self.datePublished = datePublished
        self.contentUrl = contentUrl
        self.hostPageUrl = hostPageUrl
        self.contentSize = contentSize
        self.encodingFormat = encodingFormat
        self.hostPageDisplayUrl = hostPageDisplayUrl
        self.width = width
        self.height = height
        self.thumbnail = thumbnail

class QueryContext:
    def __init__(self, originalQuery=None):
        self.originalQuery = originalQuery

class WebPages:
    def __init__(self, webSearchUrl=None, totalEstimatedMatches=None, value=None, someResultsRemoved=None):
        self.webSearchUrl = webSearchUrl
        self.totalEstimatedMatches = totalEstimatedMatches
        self.value = [WebPage(**page) for page in value]
        self.someResultsRemoved = someResultsRemoved

class Data:
    def __init__(self, _type=None, queryContext=None, webPages=None, images=None, videos=None):
        self.videos = videos
        self._type = _type
        self.queryContext = QueryContext(**queryContext)
        self.webPages = WebPages(**webPages)
        self.images = Images(**images)

class SearchResponse:
    def __init__(self, code=None, log_id=None, msg=None, data=None):
        self.code = code
        self.log_id = log_id
        self.msg = msg
        self.data = Data(**data)
