{% extends 'master.inc' %}
{% load permissions %}
{% block addFormMedia %}

{{ form.media }} 

{% endblock %}
{% load bootstrap3 %}
{% block siteTitle %}myansrsource:Reports{% endblock %}

{% block ansrMenu %}
 <li><a href="/myansrsource/dashboard">
     <span class="glyphicon glyphicon-home"></span>
     Dashboard
</a></li>
<li class="ansrLogout"><a href="{% url 'logout' %}">
	<span class="glyphicon glyphicon-off ansrLogoutIcon"></span>
	<span class="ansrLogout">Logout</span>
</a></li>
{% endblock %}

{%block content %}
    {%block childcontent %}{% endblock %}
{% endblock %}
