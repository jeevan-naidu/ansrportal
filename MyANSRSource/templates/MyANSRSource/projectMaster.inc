{% extends 'master.html' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load bootstrap3 %}

{% load fontawesome %}

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



{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-fourth {% block DPactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">Define Project</label>
    </li>
    <li class="form-step one-fourth {% block BIactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Basic Information</label>
    </li>
    <li class="form-step one-fourth {% block VactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">3</span>
        <label class="form-step-label">Validate</label>
    </li>
    <li class="form-step one-fourth {% block CactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">4</span>
        <label class="form-step-label">Complete!</label>
    </li>
</ul>
<div>
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
	{% buttons %}
        {% if wizard.steps.prev %}
                <button name="wizard_goto_step" value="{{ wizard.steps.prev }}"
                    type="button" class="btn btn-info">
                        {% fontawesome_icon 'arrow-circle-left' large=True %}
		                <b id="browserPrevious">Previous</b>
                    </button>
        {% endif %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
                    {% fontawesome_icon 'upload' large=True %}
		            <b>Confirm & Create Project</b>
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
