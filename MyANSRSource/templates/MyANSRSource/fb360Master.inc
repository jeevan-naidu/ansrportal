{% extends 'master.inc' %}
{% load permissions %}
{% block addFormMedia %}
{% load fontawesome %}

{{ form.media }} 

{% endblock %}
{% load bootstrap3 %}
{% block siteTitle %}myansrsource:Reports{% endblock %}

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

{%block content %}
    {%block childcontent %}{% endblock %}
{% endblock %}
