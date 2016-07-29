{% extends 'master.html' %}

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
    <li class="form-step one-half {% block PChooseSurvey %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">Select Survery</label>
    </li>
    <li class="form-step one-half {% block PChoosePeer %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Choose Peer(s)</label>
    </li>
</ul>
<div class="col-xs-12 col-md-12 col-lg-9 col-lg-offset-1 jumbotron shadow">
 <div id="create">
    <form id="closeProjectMilestone" method="post" action="" enctype="multipart/form-data">
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
                        {% fontawesome_icon 'arrow-circle-left' large=True %}
		        <b>Previous</b>
                    </button>
        {% endif %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
                    {% fontawesome_icon 'upload' large=True %}
		    <b>Send Request(s)</b>
                {% else %}
		    <b>Next</b>
                    {% fontawesome_icon 'arrow-circle-right' large=True %}
                {% endif %}
            </button>
        {% endbuttons %}
    </form>
 </div>
</div>
{% endblock %}
