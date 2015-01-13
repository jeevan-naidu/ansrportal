{% extends 'master.inc' %}

{% load bootstrap3 %}

{% block siteTitle %}myansrsource:Timesheet Entry{% endblock %}

{% block content  %}
<legend class="clearfix pad-bot-10">
 <div class="col-md-6">
 <form id="prevWeek" method="get" action="" enctype="multipart/form-data">
	<input type="hidden" name="week" value="prev" />
	<input type="hidden" name="enddate" value="{{ weekendDate|date:"dmY" }}" />
	<input type="hidden" name="startdate" value="{{ weekstartDate|date:"dmY" }}" />
	{% if disabled == 'prev' %}
		<button type="submit" value="submit" disabled="disabled" class="btn btn-default">
			<span class="glyphicon glyphicon-arrow-left"></span>
		</button>
	{% else %}
		<button type="submit" value="submit" class="btn btn-default">
			<span class="glyphicon glyphicon-arrow-left"></span>
		</button>
	{% endif %}
 	<span>Start : {% block startDate %}{% endblock %}</span>
 </form>
 </div>
 <div class="col-md-6 text-right">
 <form id="nextWeek" method="get" action="" enctype="multipart/form-data">
 	<span>End : {% block endDate %}{% endblock %}</span>
	<input type="hidden" name="week" value="next" />
	<input type="hidden" name="startdate" value="{{ weekstartDate|date:"dmY" }}" />
	<input type="hidden" name="endDate" value="{{ weekendDate|date:"dmY" }}" />
	{% if disabled == 'next' %}
		<button type="submit" value="submit" disabled="disabled" class="btn btn-default">
			<span class="glyphicon glyphicon-arrow-right"></span>
		</button>
	{% else %}
		<button type="submit" value="submit" class="btn btn-default">
			<span class="glyphicon glyphicon-arrow-right"></span>
		</button>
	{% endif %}
 </form>
 </div>
</legend>

<div class="text-center">
	<b>{% bootstrap_messages %}</b>
</div>
{% block timesheetContent %}{% endblock %}
{% endblock %}

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
