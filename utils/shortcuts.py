import json

from django.http import Http404, HttpResponse


def get_object_or_404(model, select_related=None, prefetch=None, **kwargs):
    ''' related is a list of arguments to select_related '''
    try:
        if select_related:
            res = model.objects.select_related(*select_related)
        if prefetch:
            res = model.objects.prefetch_related(*prefetch)
        else:
            res = model.objects
        return res.get(**kwargs)
    except model.DoesNotExist:
        raise Http404


def JSONResponse(data):
    return HttpResponse(json.dumps(data), mimetype='application/json')
