# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import visualisation
import datetime
import analytics
from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader


def index(request):
	stats_data_12 = {
		"nbn" : visualisation.calculateStatsByServiceDomain("fb_post", "nbn", 12),
		"foxtel" : visualisation.calculateStatsByServiceDomain("fb_post", "foxtel", 12),
		"bigpond" : visualisation.calculateStatsByServiceDomain("fb_post", "bigpond", 12),
		"pots" : visualisation.calculateStatsByServiceDomain("fb_post", "pots", 12),
		"customer_service" : visualisation.calculateStatsByServiceDomain("fb_post", "customer_service", 12),
		"mobile" : visualisation.calculateStatsByServiceDomain("fb_post", "mobile", 12),
	}
	
	stats_data_24 = {
		"nbn" : visualisation.calculateStatsByServiceDomain("fb_post", "nbn", 24),
		"foxtel" : visualisation.calculateStatsByServiceDomain("fb_post", "foxtel", 24),
		"bigpond" : visualisation.calculateStatsByServiceDomain("fb_post", "bigpond", 24),
		"pots" : visualisation.calculateStatsByServiceDomain("fb_post", "pots", 24),
		"customer_service" : visualisation.calculateStatsByServiceDomain("fb_post", "customer_service", 24),
		"mobile" : visualisation.calculateStatsByServiceDomain("fb_post", "mobile", 24),
	}

	stats_data_168 = {
		"nbn" : visualisation.calculateStatsByServiceDomain("fb_post", "nbn", 168),
		"foxtel" : visualisation.calculateStatsByServiceDomain("fb_post", "foxtel", 168),
		"bigpond" : visualisation.calculateStatsByServiceDomain("fb_post", "bigpond", 168),
		"pots" : visualisation.calculateStatsByServiceDomain("fb_post", "pots", 168),
		"customer_service" : visualisation.calculateStatsByServiceDomain("fb_post", "customer_service", 168),
		"mobile" : visualisation.calculateStatsByServiceDomain("fb_post", "mobile", 168),
	}
	
	overall_activity = {
		"data24" : visualisation.getTimeSeries("fb_post", 1, 24),
		"data168" : visualisation.getTimeSeries("fb_post", 2, 84),
		"total_posts" : visualisation.getTotalPosts("fb_post"),
	}
	context = {'stats_data_12' : stats_data_12, 'stats_data_24' : stats_data_24, 'stats_data_168' : stats_data_168, "overall_activity" : overall_activity}
	template = loader.get_template('templates/index.html')
	return HttpResponse(template.render(context, request))