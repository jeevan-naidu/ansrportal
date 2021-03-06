{% extends 'master.html' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load fontawesome %}

{% load bootstrap3 %}

{% block siteTitle %}myansrsource:Manager{% endblock %}



{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-half {% block MPactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">My Projects</label>
    </li>
    <li class="form-step one-half {% block PSactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Project Summary</label>
    </li>
</ul>
<div class="col-xs-12 col-md-12 col-lg-12 jumbotron shadow">
	{% block viewProjectContent %}{% endblock  %}
</div>
{% endblock %}
