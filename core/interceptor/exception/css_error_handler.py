from core.interceptor.exception.error_handler import error_handler_factory, handle_css_error


class CSSError(Exception):
    pass


css_error_handler = error_handler_factory({
    CSSError: handle_css_error
})
