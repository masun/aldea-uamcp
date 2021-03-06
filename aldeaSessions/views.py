#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import datetime
import random
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import *
from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.views import generic
from aldeaSessions.forms import *
from aldeaSessions.models import *
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect
from django.template.response import TemplateResponse
from django.views.defaults import page_not_found
from django.views.generic import *


def user_registration(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = UserCreateForm(request.POST)

            if form.is_valid():
                my_user = form.save()
                username = my_user.username
                email = form.cleaned_data['email']
                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                activation_key = hashlib.sha1(salt + email).hexdigest()
                key_expires = datetime.datetime.today() +\
                    datetime.timedelta(2)
                user = User.objects.get(username=username)
                new_profile = UserProfile(user=user,
                                          activation_key=activation_key,
                                          key_expires=key_expires)
                new_profile.save()
                group = Group.objects.get(name='profesional')
                user.groups.add(group)

                return HttpResponseRedirect(
                    reverse_lazy('login'))
            else:
                context = {'form': form}
                return render_to_response(
                    'registro_usuario.html', context,
                    context_instance=RequestContext(request))
        else:
            form = UserCreateForm()
            context = {'form': form}
            return render_to_response(
                'registro_usuario.html', context,
                context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(
            reverse_lazy('login'))


def authenticate_user(username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = User.objects.get(email=username)
            if user is not None:
                return user
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
                if user is not None:
                    return user
            except User.DoesNotExist:
                return None


def login_request(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(
            reverse_lazy('register'))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_auth = authenticate_user(username, password)
            if user_auth is not None:
                user = authenticate(username=user_auth.username,
                                    password=password)
                if user:
                    login(request, user)
                    return HttpResponseRedirect(
                        reverse_lazy('register'))
                else:
                    form.add_error(
                        None, "Tu correo o contraseña no son correctos")
            else:
                form.add_error(
                    None, "Tu correo o contraseña no son correctos")
    else:
        form = LoginForm()
    context = {'form': form, 'host': request.get_host()}
    return render_to_response('login.html', context,
                              context_instance=RequestContext(request))


def generate_key(request, pk):

    if request.user.is_authenticated():
        HttpResponseRedirect(reverse_lazy('login'))

    user = User.objects.get(pk=pk)
    UserProfile.objects.filter(user=user).delete()
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    activation_key = hashlib.sha1(salt + user.email).hexdigest()
    key_expires = datetime.datetime.today() + datetime.timedelta(2)
    new_profile = UserProfile(user=user, activation_key=activation_key,
                              key_expires=key_expires)
    new_profile.save()
    return render_to_response('registro_usuario.html')


@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None,
                   html_email_template_name=None):
    post_reset_redirect = reverse_lazy('password_reset_done')
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


class NoticiaView(generic.CreateView):
    template_name = "noticia.html"
    form_class = NoticiaForm

    def get(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data(**kwargs)
        context['form'] = NoticiaForm
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save()
            noticia.user = request.user
            noticia.save()
            return HttpResponseRedirect(
                reverse_lazy('noticias_list'))
        else:
            return render(request, self.template_name, {'form': form})


class NoticiaListView(ListView):
    template_name = 'noticia_list.html'
    model = Noticia

    def get(self, request, *args, **kwargs):
        self.object_list = []
        context = super(
            NoticiaListView, self).get_context_data(**kwargs)
        noticias = Noticia.objects.all()
        context['noticias'] = noticias
        print("Image:" + noticia.image)
        return self.render_to_response(context)


def eliminarNoticia(request, id):
    noticia = Noticia.objects.get(pk=id)
    noticia.delete()
    return HttpResponseRedirect(reverse_lazy('noticias_list'))
