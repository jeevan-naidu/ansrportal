{% extends 'master.html' %}

{% block addFormMedia %}

{{ wizard.form.media }}

{% endblock %}

{% load i18n %}

{% load bootstrap3 %}

{% load fontawesome %}

{% block siteTitle %}Projects{% endblock %}

{% block loggedStatus %}
{% endblock %}

{% block pageTitle %}{{ wizard.steps.current }}{% endblock %}
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
        <label class="form-step-label">Manage Project Leader(s)</label>
    </li>
</ul>
<div>

<style type="text/css">
    
.yourlabs-autocomplete{
    max-height: 300px;
    overflow: auto;
}

</style>



<div class="panel clearfix">
<div class="panel-body">
 <div id="create">
    <form id="changeProject" method="post" action="" enctype="multipart/form-data">
        {% csrf_token %}
    <legend>
        
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
                        <i class="fa fa-arrow-circle-left fa-lg"></i>
                <b>Choose Project</b>
                    </button>
        {% endif %}
            <button type="submit" value="submit" class="btn btn-info pull-right">
                {% if wizard.steps.current == wizard.steps.last %}
                <i class="fa fa-upload fa-lg"></i>
            <b>Update Project Leader(s)</b>
                {% else %}
            <b>View Project Leader(s)</b>
                    <i class="fa fa-arrow-circle-right fa-lg"></i>
                {% endif %}
            </button>
        {% endbuttons %}
    </form>
 </div>
</div>
</div>




</div>
{% endblock %}
