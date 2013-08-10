# encoding:utf-8

from commons import *
from edge_console.forms_model import Username_CheckForm
from django.contrib.auth.models import User, Group
from edge_console.models import *
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext


def create_username(request):
    """用户自己创建账户以便创建APP
    Args:
        request:
    """

    cleaned_data = {}
    modelid = None
    return_message = {}
    if request.method == 'POST':
        for k, v in request.POST.items():
            cleaned_data[k] = v

        ccf = Username_CheckForm(modelid, cleaned_data)
        model_error = ccf.is_clean()
        username = cleaned_data['username']
        if not model_error:
            password = cleaned_data['password']
            cleaned_data.pop('password')
            cleaned_data.pop('confirm_password')
            use = User(**cleaned_data)
            use.set_password(password)
            use.save()
            u = User.objects.filter(username=username)
            g = Group.objects.get(name='客户创建APP')
            g.user_set.add(u[0])

            return HttpResponseRedirect('/apps/app/show/')
        else:
            return_message = {'error_msg': model_error, 'user_name': username}
            return render_to_response('portal/account/create_username.html',return_message,context_instance=RequestContext(request))

    return render_to_response('portal/account/create_username.html',return_message,context_instance=RequestContext(request))
