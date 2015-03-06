{% extends 'master.inc' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load bootstrap3 %}

{% block siteTitle %}myansrsource:Manager{% endblock %}

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
    <span class="glyphicon glyphicon-home"></span>
    Dashboard
 </a></li>
 <li class="ansrLogout"><a href="{% url 'logout' %}">
    <span class="glyphicon glyphicon-off ansrLogoutIcon"></span>
    <span class="ansrLogout">Logout</span>
  </a></li>
{% endblock %}

{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-half {% block MPactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">My Projects</label>
    </li>
    <li class="form-step one-half {% block TMactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Create / Update Team</label>
    </li>
</ul>
<div>
 <div id="create">
    <form id="changeProject" method="post" action="" enctype="multipart/form-data">
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
	{% buttons %}
        {% if wizard.steps.prev %}
                <button name="wizard_goto_step" value="{{ wizard.steps.prev }}" 
                    type="submit" class="btn btn-info">
                        <span class="glyphicon glyphicon-chevron-left"></span>
		        <b>Choose Project</b>
                    </button>
        {% endif %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
                <span class="glyphicon glyphicon-check"></span>
		    <b>Create / Update Team</b>
                {% else %}
		    <b>View Team</b>
                    <span class="glyphicon glyphicon-chevron-right"></span>
                {% endif %}
            </button>
        {% endbuttons %}
    </form>
 </div>
</div>
{% endblock %}
