def error_handler_factory(error_handlers):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(error_handlers.keys()) as e:
                handler = error_handlers[type(e)]
                return handler(func, e)
            except Exception as e:
                return handle_exception(e)

        return wrapper

    return decorator


def handle_index_error(func, error):
    return str()


def handle_xpath_eval_error(func, error):
    return return_default(func)


def handle_css_error(func, error):
    return "CSS Error"


def handle_js_error(func, error):
    return "JavaScript Error"


def handle_exception(e):
    return str(e)


def return_default(func):
    return_type = func.__annotations__.get("return")
    if not return_type:
        return None
    elif return_type == str:
        return str()
    elif hasattr(return_type, "__origin__") and return_type.__origin__ == list:
        return list()
    else:
        raise Exception("no match return type")
