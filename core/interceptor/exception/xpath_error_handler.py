from lxml.etree import XPathEvalError
from core.interceptor.exception.error_handler import error_handler_factory, handle_index_error, handle_xpath_eval_error

xpath_error_handler = error_handler_factory({
    IndexError: handle_index_error,
    XPathEvalError: handle_xpath_eval_error
})
