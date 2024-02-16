import tornado.web
import tornado.httpserver


class SwaggerStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header(
            "Cache-Control", "no-store, no-cache, " "must-revalidate, max-age=0"
        )
