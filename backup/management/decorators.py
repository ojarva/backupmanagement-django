from django.template import RequestContext
from functools import wraps
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings
import json
import subprocess
from disk import Disk

__all__ = ["json_render", "render", "disk_no_required", "disk_required"]

def json_render(func):
    """ if view returns dictionary, print out json. Otherwise return original data. """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict):
            return HttpResponse(json.dumps(response), mimetype="text/json")
        else:
            return response
    return wrapper

def render(template_name):
    """ Render to template, if argument is dictionary, otherwise pass it forward """
    def inner_render(fn):
        def wrapped(request, *args, **kwargs):
            ret_dict = fn(request, *args, **kwargs)
            if type(ret_dict).__name__=='dict':
                return render_to_response(template_name,
                                       ret_dict,
                                       context_instance = RequestContext(request))
            else:
                return ret_dict
        return wraps(fn)(wrapped)
    return inner_render

def _disk_exists(username):
    """ Check whether disk exists or not """
    disk = Disk(username)
    return disk.exists()

def disk_no_required(redirect_url):
    """ Redirect to "redirect_url" if disk exists """
    def _inner(fn):
        def wrapped(request, *args, **kwargs):
            if _disk_exists(request.user.username):
                return HttpResponseRedirect(redirect_url)
            return fn(request, *args, **kwargs)
        return wraps(fn)(wrapped)

    return _inner

def disk_required(redirect_url):
    """ Redirect to "redirect_url" if disk doesn't exist """
    def _inner(fn):
        def wrapped(request, *args, **kwargs):
            if not _disk_exists(request.user.username):
                return HttpResponseRedirect(redirect_url)
            return fn(request, *args, **kwargs)
        return wraps(fn)(wrapped)

    return _inner
