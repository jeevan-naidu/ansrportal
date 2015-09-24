{% extends 'master.inc' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load fontawesome %}

{% load bootstrap3 %}

{% block siteTitle %}myansrsource:FB360&deg;{% endblock %}

{% block responsiveMenu %}
<button type="button" class="navbar-toggle" data-toggle="collapse" 
    data-target="#example-navbar-collapse">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>                                  
</button>
{% endblock %}

{% block ansrMenu %}
 <li><a href="/myansrsource/dashboard">
    {% fontawesome_icon 'university' large=True %}
    Dashboard
 </a></li>
 <li class="ansrLogout"><a href="{% url 'logout' %}">
    {% fontawesome_icon 'sign-out' large=True color='red' %}
    <span class="ansrLogout">Logout</span>
  </a></li>
{% endblock %}

{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-half {% block MRactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">My Requestee(s)</label>
    </li>
    <li class="form-step one-half {% block QAactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Feedback QA</label>
    </li>
</ul>
<div class="col-xs-12 col-md-12 col-lg-12 jumbotron shadow">
	{% block feedbackChild %}{% endblock  %}
</div>
{% endblock %}
