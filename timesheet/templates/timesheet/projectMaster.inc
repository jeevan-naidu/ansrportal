{% extends 'master.inc' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load bootstrap3 %}

{% block siteTitle %}ANSR-Manager{% endblock %}

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
 <li><a href="/timesheet/dashboard">
    <span class="glyphicon glyphicon-home"></span>
    Dashboard
 </a></li>
 <li class="dropdown">
    <a href="#" class="dropdown-toggle" data-toggle="dropdown">
	    <span class="glyphicon glyphicon-book"></span>
	    Project
    <span class="caret"></span></a>
    <ul class="dropdown-menu" role="menu">
	<li {% block createProjectActive %}{% endblock %}><a href="/timesheet/project/add">
		<span class="glyphicon glyphicon glyphicon-pencil"></span>
		Create New
	</a></li>
	<li class="divider"></li>
	<li {% block manageProjectActive %}{% endblock %}><a href="#">
		<span class="glyphicon glyphicon-cog"></span>
		Manage
	</a></li>
	<li class="divider"></li>
	<li {% block projectProgressActive %}{% endblock %}><a href="#">
		<span class="glyphicon glyphicon-tasks"></span>
		Progress
	</a></li>
	<li class="divider"></li>
	<li {% block projectStatusActive %}{% endblock %}><a href="#">
    		<span class="glyphicon glyphicon-dashboard"></span>
		Status
	</a></li>
    </ul>
 </a></li>
 <li {% block timesheetActive %}{% endblock %} class="dropdown">
    <a href="#" class="dropdown-toggle" data-toggle="dropdown">
	    <span class="glyphicon glyphicon-list-alt"></span>
	    Timesheet
    <span class="caret"></span></a>
    <ul class="dropdown-menu" role="menu">
	<li><a href="#">
    		<span class="glyphicon glyphicon-plus"></span>
		Entry
	</a></li>
	<li class="divider"></li>
	<li><a href="#">
    		<span class="glyphicon glyphicon-cog"></span>
		Manage
	</a></li>
    </ul>
 </a></li>
 <li {% block teamMemberPerfomanceActive %}{% endblock %}><a href="#perfomance">
    <span class="glyphicon glyphicon-user"></span>
    Team&nbsp;Member's&nbsp;Perfomance
 </a></li>
 <li class="ansrLogout"><a href="{% url 'logout' %}">
    <span class="glyphicon glyphicon-off ansrLogoutIcon"></span>
    <span class="ansrLogout">Logout</span>
  </a></li>
{% endblock %}

{% block loggedStatus %}
{% endblock %}

{% block content %}
<div class="col-xs-12 col-md-12 col-lg-9 col-lg-offset-1 jumbotron shadow">
 <div id="create">
    <form id="createProject" method="post" action="" enctype="multipart/form-data">
        {% csrf_token %}
	<legend>
		<b>{{ wizard.steps.current }}</b>
		{% block addForm %}{% endblock %}
	</legend>
        {{ wizard.management_form }}
	{% if wizard.form.forms %}
		{{ wizard.form.management_form }}
		{% for form in wizard.form.forms %}
		{% block childform %}{% endblock %}
		{% endfor %}
	{% else %}
		{{ wizard.form.management_form }}
		{% with form=wizard.form %}
		{% block masterform %}{% endblock %}
		{% endwith %}
	{% endif %}
        {% if wizard.steps.prev %}
            <span class="col-md-6 col-xs-6">
                {% buttons %}
                <button name="wizard_goto_step" value="{{ wizard.steps.prev }}" 
                    type="submit" class="btn btn-info">
                        <span class="glyphicon glyphicon-chevron-left"></span>
		        <b>Previous</b>
                    </button>
                {% endbuttons %}
            </span>
        {% endif %}
    	<span class="col-md-6 col-xs-6">
        {% buttons %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
		    <b>Create</b>
                {% else %}
		    <b>Next</b>
                    <span class="glyphicon glyphicon-chevron-right"></span>
                {% endif %}
            </button>
        {% endbuttons %}
	</span>
    </form>
 </div>
</div>
{% endblock %}
