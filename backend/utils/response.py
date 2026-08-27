def make_response(code: int = 200, msg: str = 'success', data=None):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={'code': code, 'msg': msg, 'data': data}
    )