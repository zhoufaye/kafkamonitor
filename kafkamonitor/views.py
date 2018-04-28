from django.shortcuts import render, render_to_response
from django.template import RequestContext, loader
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout,login
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
import json

import logging



def login_view(request):
    redirect_to = settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        redirect_to = request.POST.get('next','/')
        logging.info(redirect_to)
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            logging.info('hello')
            return HttpResponseRedirect("/")

    else:
        if request.GET.has_key('next'):
            redirect_to = request.GET['next']

        if not bool(User.objects.all().count()):
            return HttpResponseRedirect('/superuser/')

        form = AuthenticationForm(request)

    context = {
        'form': form,
        'next': redirect_to
    }

    return render(request,'login.html',locals())

def create_superuser(request):
    redirect_to = settings.LOGIN_REDIRECT_URL
    logging.info('1')
    if bool(User.objects.all().count()):
        logging.info('1')
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        try:
            post = json.loads(request.body)
            User.objects.create_superuser(post['username'],'admin@123.com',post['password'])
            context = {'flag':"Success",}
        except Exception,e:
            context = { "flag":"Error","context":str(e) }

        return HttpResponse(json.dumps(context))

    return render_to_response('superuser.html')

def logout_view(request):
    Session.objects.filter(expire_date__lte=timezone.now()).delete()
    logout(request)
    return HttpResponseRedirect('/login/')

def is_auth(view):
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            context = {
                'flag':"Error",
                'context':"AuthFailed"
            }
            return HttpResponse(json.dumps(context))
        else:
            return view(request, *args, **kwargs)
    return decorator