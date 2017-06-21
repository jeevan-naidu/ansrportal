{% extends 'master.html' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load bootstrap3 %}

{% load fontawesome %}

{% block siteTitle %}Projects{% endblock %}

{% block pageTitle %}{{ wizard.steps.current }}{% endblock %}

{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-third {% block MPactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">Rejected Projects</label>
    </li>
    <li class="form-step one-third {% block CBIactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Modify Basic Information</label>
    </li>
    <li class="form-step one-third {% block SactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">3</span>
        <label class="form-step-label">Summary</label>
    </li>
</ul>
<div>
<style type="text/css">
.table-condensed>thead>tr>th, .table-condensed>tbody>tr>th, .table-condensed>tfoot>tr>th, .table-condensed>thead>tr>td, .table-condensed>tbody>tr>td, .table-condensed>tfoot>tr>td {
    padding: 5px 8px;
}

.yourlabs-autocomplete{
    max-height: 200px !important;
    max-width: 350px !important;
    overflow: auto;
}
</style>
 <div id="create">
    <form id="modifyProject" method="post" action="" enctype="multipart/form-data">
        {% csrf_token %}
	
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
                        <i class="fa fa-arrow-circle-left fa-lg"></i>
		        <b>Previous</b>
                    </button>
        {% endif %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
                        <i class="fa fa-upload fa-lg"></i>
		    <b>Update Project</b>
                {% else %}
		    <b>Next</b>
                    <i class="fa fa-arrow-circle-right fa-lg"></i>
                {% endif %}
            </button>
        {% endbuttons %}
    </form>
 </div>
</div>
<script>
</script>
{% endblock %}
