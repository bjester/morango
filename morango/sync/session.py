import logging

from requests import exceptions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.connectionpool import HTTPConnectionPool
from requests.packages.urllib3.connectionpool import HTTPSConnectionPool
from requests.packages.urllib3.connection import HTTPConnection
from requests.packages.urllib3.connection import HTTPSConnection
from requests.sessions import Session
from requests.utils import super_len

logger = logging.getLogger(__name__)


class SyncSignal(object):
    """
    Helper class for firing signals during sync
    """

    def __init__(self, **kwargs_defaults):
        """
        Default keys/values that the signal consumer can depend on being present.
        """
        self._handlers = []
        self._defaults = kwargs_defaults

    def connect(self, handler):
        """
        Adds a callable handler that will be called when the signal is fired.

        :type handler: function
        """
        self._handlers.append(handler)

    def fire(self, **kwargs):
        """
        Fires the handler functions connected via `connect`.
        """
        fire_kwargs = self._defaults.copy()
        fire_kwargs.update(kwargs)

        for handler in self._handlers:
            handler(**fire_kwargs)


class TransferMixin(object):
    """
    Generic mixin that adds a signal attribute for tracking bytes sent and received
    """
    def __init__(self, *args, **kwargs):
        super(TransferMixin, self).__init__(*args, **kwargs)
        self.transfer_signal = SyncSignal(bytes_sent=0, bytes_received=0)


class FileWrapper(TransferMixin):
    """
    Minimal file object wrapper handling methods used for reading the response descriptor and
    tracking how much data was read, firing the signal to track those amounts
    """
    def __init__(self, fp):
        super(FileWrapper, self).__init__()
        self.fp = fp

    def read(self, *args, **kwargs):
        data = self.fp.read(*args, **kwargs)
        self.transfer_signal.fire(bytes_received=super_len(data))
        return data

    def readline(self, *args, **kwargs):
        data = self.fp.readline(*args, **kwargs)
        self.transfer_signal.fire(bytes_received=super_len(data))
        return data

    def readinto(self, *args, **kwargs):
        bytes_read = self.fp.readinto(*args, **kwargs)
        self.transfer_signal.fire(bytes_received=bytes_read)
        return bytes_read

    def flush(self):
        self.fp.flush()

    def close(self):
        fp = self.fp
        self.fp = None
        fp.close()


class HTTPResponseWrapper(TransferMixin, HTTPConnection.response_class):
    """
    Wraps the HTTPResponse to wrap the file object, and connect the signals to bubble up the
    bytes received signals
    """
    def __init__(self, *args, **kwargs):
        super(HTTPResponseWrapper, self).__init__(*args, **kwargs)
        self.fp = FileWrapper(self.fp)
        self.fp.transfer_signal.connect(self.transfer_signal.fire)


class ConnectionMixin(TransferMixin):
    """
    Mixin that will track data sent over the connection socket, and connect response signals
    to bubble up bytes received
    """
    response_class = HTTPResponseWrapper

    def send(self, data):
        """
        Override this method, which is used in requests, so we can trigger the bytes sent signal
        """
        try:
            # this tracks the data sent over the socket
            self.transfer_signal.fire(bytes_sent=super_len(data))
        finally:
            super(ConnectionMixin, self).send(data)

    def getresponse(self, *args, **kwargs):
        """
        Override this method to connect signals from response to ourselves, so we can bubble up
        """
        response = super(ConnectionMixin, self).getresponse(*args, **kwargs)
        response.transfer_signal.connect(self.transfer_signal.fire)
        return response


class HTTPConnectionWrapper(ConnectionMixin, HTTPConnection):
    pass


class HTTPSConnectionWrapper(ConnectionMixin, HTTPSConnection):
    pass


class ConnectionPoolMixin(TransferMixin):
    """
    Mixin that overrides the creation of a new connection to connect the signals from the
    connection to this pool, so bytes sent and received are bubbled up
    """
    def _new_conn(self):
        conn = super(ConnectionPoolMixin, self)._new_conn()
        conn.transfer_signal.connect(self.transfer_signal.fire)
        return conn


class HTTPConnectionPoolWrapper(ConnectionPoolMixin, HTTPConnectionPool):
    ConnectionCls = HTTPConnectionWrapper


class HTTPSConnectionPoolWrapper(ConnectionPoolMixin, HTTPSConnectionPool):
    ConnectionCls = HTTPSConnectionWrapper


class HTTPAdapterWrapper(TransferMixin, HTTPAdapter):
    def init_pool(self, PoolCls):
        """
        Helper function that will instantiate the pool class and connect signals to bubble up
        signals from the pool class
        """
        def init(*args, **kwargs):
            pool = PoolCls(*args, **kwargs)
            pool.transfer_signal.connect(self.transfer_signal.fire)
            return pool
        return init

    def init_poolmanager(self, *args, **kwargs):
        """
        Overrides the definition of what pool classes to use, indexed by key, such that we can
        use our own pool classes which will bubble up events from closer to the connection socket
        """
        super(HTTPAdapterWrapper, self).init_poolmanager(*args, **kwargs)
        self.poolmanager.pool_classes_by_scheme = dict(
            http=self.init_pool(HTTPConnectionPoolWrapper),
            https=self.init_pool(HTTPSConnectionPoolWrapper),
        )


class SessionWrapper(Session):
    """
    Wrapper around `requests.sessions.Session` in order to implement logging around all request
    errors, and to track the data sent and received
    """

    bytes_sent = 0
    bytes_received = 0

    def request(self, method, url, **kwargs):
        try:
            response = super(SessionWrapper, self).request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except exceptions.RequestException as req_err:
            # we want to log all request errors for debugging purposes
            response_content = (
                req_err.response.content if req_err.response else "(no response)"
            )
            logger.error(
                "{} Reason: {}".format(req_err.__class__.__name__, response_content)
            )
            raise req_err

    def track_transfer(self, bytes_sent=0, bytes_received=0):
        """
        Attached as a signal handler that will handle signals fired from closer to the socket
        """
        self.bytes_sent += bytes_sent
        self.bytes_received += bytes_received

    def mount(self, prefix, adapter):
        """
        Override the mount method which attaches an adapter to a scheme, so when we've attached
        our own adapter above, we can connect our signals to track bytes sent and received
        during the session
        """
        super(SessionWrapper, self).mount(prefix, adapter)
        if isinstance(adapter, HTTPAdapterWrapper):
            adapter.transfer_signal.connect(self.track_transfer)

