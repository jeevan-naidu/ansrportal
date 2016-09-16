{% extends 'master.html' %}

{% block addFormMedia %}

{{ wizard.form.media }}



<!-- <link rel="stylesheet" type="text/css" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"> -->
<style type="text/css">
    
.table-condensed>thead>tr>th, .table-condensed>tbody>tr>th, .table-condensed>tfoot>tr>th, .table-condensed>thead>tr>td, .table-condensed>tbody>tr>td, .table-condensed>tfoot>tr>td {
    padding: 5px 8px;
}
    
</style>


{% endblock %}

{% load i18n %}

{% load fontawesome %}

{% load bootstrap3 %}

{% block siteTitle %}Projects{% endblock %}

{% block pageTitle %}{{ wizard.steps.current }}{% endblock %}

{% block loggedStatus %}
{% endblock %}
{% block content %}
<ul class="form-steps clearfix">
    <li class="form-step one-half {% block MPactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">1</span>
        <label class="form-step-label">My Projects</label>
    </li>
    <li class="form-step one-half {% block CMSactiveClass %}{% endblock %}">
        <span class="form-step-bor"></span>
        <span class="form-step-no">2</span>
        <label class="form-step-label">Create / Update Milestone(s)</label>
    </li>
</ul>
<div class="panel clearfix">
    <div class="panel-body col-xs-12">
        <div id="create">
            <form id="closeProjectMilestone" method="post" action="" enctype="multipart/form-data">
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
                                {% fontawesome_icon 'arrow-circle-left' large=True %}
                        <b>Choose Project</b>
                            </button>
                {% endif %}
                    <button type="submit" value="submit" class="btn btn-info pull-right">
                        {% if wizard.steps.current == wizard.steps.last %}
                            {% fontawesome_icon 'upload' large=True %}
                    <b>Create / Update Milestone(s)</b>
                        {% else %}
                    <b>View Milestone(s)</b>
                            {% fontawesome_icon 'arrow-circle-right' large=True %}
                        {% endif %}
                    </button>
                {% endbuttons %}
            </form>
        </div>
    </div>
</div>
{% endblock %}
