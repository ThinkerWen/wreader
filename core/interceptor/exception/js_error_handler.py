from core.interceptor.exception.error_handler import error_handler_factory, handle_js_error


class JSError(Exception):
    pass


js_error_handler = error_handler_factory({
    JSError: handle_js_error
})
