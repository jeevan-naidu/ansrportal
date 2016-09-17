{% extends 'master.html' %}

{% load bootstrap3 %}
{% load fontawesome %}

{% block siteTitle %}Enter Timesheet{% endblock %}

{% block content  %}





<div class="timesheet-carousel text-center">
<div class="carousel slide row" data-ride="carousel" data-type="multi" data-interval="false" id="fruitscarousel">

    <div class="carousel-inner">


        <div class="item active">
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 15 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 25 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 35 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 45 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 55 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 65 - Aug 21</span></div></a></div>
        </div>
        <div class="item">
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week"><span class="week-start-date">Aug 21 - Aug 28</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 15 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week"><span class="week-start-date">Aug 21 - Aug 28</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 15 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week"><span class="week-start-date">Aug 21 - Aug 28</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 15 - Aug 21</span></div></a></div>
        </div>
        <div class="item">
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Sep 01 - Sep 07</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 15 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 16 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 17 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 18 - Aug 21</span></div></a></div>
            <div class="col-md-2 week-container"><a href="#"><div class="timesheet-week timesheet-closed"><span class="week-start-date">Aug 19 - Aug 21</span></div></a></div>
        </div>

    </div>

    <a class="left carousel-control" href="#fruitscarousel" data-slide="prev"><i class="glyphicon glyphicon-chevron-left"></i></a>
    <a class="right carousel-control" href="#fruitscarousel" data-slide="next"><i class="glyphicon glyphicon-chevron-right"></i></a> 

</div>
</div>

















<legend class="clearfix pad-bot-10 bb0">
 <div class="col-md-1">
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
 </form>
 </div>

	<div class="col-md-7 text-right"><b>Enter Timesheet :</b> <i>{% block startDate %}{% endblock %} - {% block endDate %}{% endblock %}</i></div>

 <div class="col-md-4 text-right">
 <form id="nextWeek" method="get" action="" enctype="multipart/form-data">
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
    {% fontawesome_icon 'university' large=True %}
    Dashboard
 </a></li>
<li class="ansrLogout"><a href="{% url 'logout' %}">
    {% fontawesome_icon 'sign-out' large=True color='red' %}
      <span class="ansrLogout">Logout</span>
  </a></li>
{% endblock %}
