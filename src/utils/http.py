import json
from django.http import Http404, HttpResponse


def JSONResponse(data = {}): return HttpResponse(json.dumps(data), content_type="application/json")


def JSONErrorResponse(msg, data=None):
    if data:
        data['error'] = msg
        return JSONResponse(data)
    else:
        return JSONResponse({'error': msg})

