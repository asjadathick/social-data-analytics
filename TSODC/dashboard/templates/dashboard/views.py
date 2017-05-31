# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import visualisation
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader


def index(request):
	stats_data = {
		"nbn" : visualisation.calculateMeanByServiceDomain("fb_post", "nbn", 24),
		"foxtel" : visualisation.calculateMeanByServiceDomain("fb_post", "foxtel", 24),
		"bigpond" : visualisation.calculateMeanByServiceDomain("fb_post", "bigpond", 24),
		"pots" : visualisation.calculateMeanByServiceDomain("fb_post", "pots", 24),
		"customer_service" : visualisation.calculateMeanByServiceDomain("fb_post", "customer_service", 24),
		"mobile" : visualisation.calculateMeanByServiceDomain("fb_post", "mobile", 24),
	}
	context = {'stats_data' : stats_data}
	template = loader.get_template('index.html')
	return HttpResponse(template.render(context, request))