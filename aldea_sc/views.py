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
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect
from django.template.response import TemplateResponse
from django.views.defaults import page_not_found



class HomeView(generic.TemplateView):
    template_name = 'home.html'