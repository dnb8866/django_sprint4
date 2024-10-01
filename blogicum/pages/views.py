from django.shortcuts import render
from django.views.generic import TemplateView


def handler404(request, *args, **kwargs):
    return render(request, 'pages/404.html', status=404)


def handler500(request, *args, **kwargs):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


class AboutTemplateView(TemplateView):
    """View about page."""

    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    """View rules page."""

    template_name = 'pages/rules.html'
