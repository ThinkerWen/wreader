import re
from functools import wraps

from py_mini_racer import JSEvalException

from core.parser.js import execute_js


def js_interceptor(func):
    @wraps(func)
    def wrapper(*args):
        result = None
        self, node, exp = args
        expr, js_code = parse_rule(exp)
        try:
            result = func(self, node=node, exp=expr)
            if js_code:
                return execute_js(js_code, result)
        except JSEvalException:
            return result
        except Exception as e:
            return str(e)
        return result
    return wrapper


def parse_rule(rule):
    xpath_pattern = r"(.+?)<js>(.*?)</js>"
    match = re.match(xpath_pattern, rule, re.DOTALL)
    if match:
        xpath_expr = match.group(1).strip()
        js_code = match.group(2).strip()
        return xpath_expr, js_code
    else:
        return rule, None
