def replace_params(params: dict, keyword: str) -> dict:
    keywords = {"{keyword}": keyword}
    for k, v in params.items():
        if v not in keywords.keys():
            continue
        params[k] = keywords.get(v)
    return params
