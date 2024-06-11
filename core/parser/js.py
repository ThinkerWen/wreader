from py_mini_racer import MiniRacer


def execute_js(js_code, value):
    context = MiniRacer()
    context.eval("""
        function processValue(value) {
            %s
        }
    """ % js_code)
    return context.call("processValue", value)
