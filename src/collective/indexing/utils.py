from logging import getLogger
from inspect import currentframe
from zope.component import queryUtility, getUtilitiesFor
from collective.indexing.interfaces import IIndexing
from collective.indexing.interfaces import IIndexingConfig
from collective.indexing.queue import getQueue
from collective.indexing.queue import processQueue


debug = getLogger(__name__).debug


def isActive():
    config = queryUtility(IIndexingConfig)
    if config is not None:
        return config.active
    return False


def getIndexer():
    """ look for and return an indexer """
    if isActive():                  # when switched on...
        return getQueue()           # return a (thread-local) queue object...
    indexers = list(getUtilitiesFor(IIndexing))
    if len(indexers) == 1:
        return indexers[0][1]       # directly return unqueued indexer...
    elif not indexers:
        return None                 # or none...
    else:
        assert len(indexers) < 1, 'cannot use multiple direct indexers; please enable queueing'


def isAutoFlushing():
    config = queryUtility(IIndexingConfig)
    if config is not None:
        return config.auto_flush
    return True                     # on by default as a safety net...


def framespec(depth=1):
    """ formet the module, name & line for the frame at the given depth """
    frame = currentframe(depth)
    name = frame.f_globals['__name__']
    line = frame.f_lineno
    func = frame.f_code.co_name
    return '%s/%s:%d' % (name, func, line)


def autoFlushQueue(hint='??', request=None, **kw):
    """ process the queue (for this thread) immediately if the
        auto-flush feature is enabled """
    if isActive() and isAutoFlushing() and getQueue().length():
        debug('auto-flush via %s at `%s`: %r, %r',
            hint, framespec(3), request, kw)
        return processQueue()
