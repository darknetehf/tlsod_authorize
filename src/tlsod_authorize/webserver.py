import json
import logging
import re
from contextlib import closing
from functools import cached_property
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer as HTTPServer
from urllib.parse import parse_qsl, urlparse


class TlsodHTTPServer(HTTPServer):
    def __init__(self, db_handle, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self.RequestHandlerClass.db_handle = db_handle


class WebRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args):
        self.logger = logging.getLogger(__name__)
        BaseHTTPRequestHandler.__init__(self, *args)

    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    def domain_exists(self, domain) -> bool:
        """Check whether the domain name exists in the inventory (case-insensitive search)"""

        with closing(self.db_handle.cursor()) as cursor:
            cursor.execute(
                "SELECT * FROM domains WHERE LOWER(domain) = ? LIMIT 1",
                (domain.lower(),),
            )
            record = cursor.fetchone()
            return record is not None

    def do_GET(self):
        self.logger.debug(f"GET request received: {self.query_data}")

        try:
            domain = self.query_data.get("domain")

            if domain is None:
                message = "Domain name missing from request"
                status_code = 400
            else:
                # accept both domain.com AND www.domain.com
                pattern = r"^www\."
                domain = re.sub(pattern, "", domain)

                if self.domain_exists(domain):
                    message = f"Domain name found: {domain}"
                    status_code = 200
                else:
                    message = f"Domain name not found: {domain}"
                    status_code = 404

        except Exception as ex:
            exception_type = ex.__class__.__name__
            self.logger.exception(f"Unhandled exception: {exception_type}")
            message = "Server error - see logs for details"
            status_code = 500
        finally:
            self.logger.info(message)
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"message": message}
            self.wfile.write(json.dumps(response).encode("utf-8"))
