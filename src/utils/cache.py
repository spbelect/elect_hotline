
from django.conf import settings
from django.core.cache import get_cache, DEFAULT_CACHE_ALIAS
from django.core.exceptions import DisallowedHost
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.utils.cache import get_cache_key, _generate_cache_header_key, _generate_cache_key


def expire_cache(path, args=[], cache_name=None, isview=True, lang_code=None, method='GET'):
    if cache_name is None:
        cache_name = DEFAULT_CACHE_ALIAS

    cache = get_cache(cache_name)
    key_prefix = settings.CACHES[cache_name].get('KEY_PREFIX', '')

    # Page cached depending on absolute uri, so we should reset cache for all possible ALLOWED_HOSTS.
    for host in settings.ALLOWED_HOSTS:
        for port in ['80', '443', '8000', '8080']:
            request = HttpRequest()
            request.META['SERVER_NAME'] = host
            request.META['SERVER_PORT'] = port
            try:
                request.get_host()
            except DisallowedHost:
                continue

            if isview:
                request.path = reverse(path, args=args)
            else:
                request.path = path

            language_code = lang_code or getattr(settings, 'LANGUAGE_CODE')
            if language_code:
                request.LANGUAGE_CODE = language_code

            header_key = _generate_cache_header_key(key_prefix, request)

            if not header_key:
                return False

            headerlist = cache.get(header_key, None)
            if headerlist is not None:
                cache.set(header_key, None, 0)
                page_key = _generate_cache_key(request, method, headerlist, key_prefix)

                if not page_key:
                    return False

                cache.set(page_key, None, 0)
    return True

#expire_cache('apps.yourapp.views.function')
