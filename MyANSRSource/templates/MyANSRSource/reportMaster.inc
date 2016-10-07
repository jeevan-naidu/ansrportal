{% extends 'master.html' %}
{% load permissions %}
{% block addFormMedia %}
{% load fontawesome %}

{{ form.media }} 

{% endblock %}
{% load bootstrap3 %}
{% block siteTitle %}Reports{% endblock %}

{% block ansrMenu %}
 <li><a href="/myansrsource/dashboard">
 	<i class="fa fa-university"></i>
     Dashboard
</a></li>
<li class="ansrLogout"><a href="{% url 'logout' %}">
	<i class="fa fa-sign-out" style="color: red"></i>
	<span class="ansrLogout">Logout</span>
</a></li>
{% endblock %}

{%block content %}
    {%block childcontent %}{% endblock %}
{% endblock %}
