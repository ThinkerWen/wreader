from core.util.keyword_tool import replace_params


def get_request_params(source: dict, process: str, keyword: str = "", url: str = "") -> dict:
    if process == "search":
        process_source = source.get("ruleSearch")
    elif process == "chapter":
        process_source = source.get("ruleChapter")
    elif process == "content":
        process_source = source.get("ruleContent")
    else:
        raise Exception("Process not in [search | chapter | content]")
    result = {
        key: value for key, value in {
            "url": url or process_source.get("url"),
            "method": process_source.get("method"),
            "params": replace_params(process_source.get("params"), keyword),
            "headers": process_source.get("header") or source.get("header"),
            "cookies": process_source.get("cookie") or source.get("cookie")
        }.items() if value
    }
    return result
