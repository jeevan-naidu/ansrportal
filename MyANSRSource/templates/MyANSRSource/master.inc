<!DOCTYPE html>
<html lang="en">
    <head>
       {% load static from staticfiles %}
       <meta charset="utf-8">
       <meta http-equiv="X-UA-Compatible" content="IE=edge">
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <title>{% block siteTitle %}myansrsource{% endblock %}</title>

       {# Ansrsource Favicon #}
       <link rel="icon" type="image/png" href="{% static 'images/favicon-32x32.png' %}" sizes="32x32" />
       <link rel="icon" type="image/png" href="{% static 'images/favicon-16x16.png' %}" sizes="16x16" />

       {# Load Pace JS #}
       <script src="{% static 'js/pace.js' %}"></script>

       {# Load the tag library #}
       {% load bootstrap3 %}
       {% load fontawesome %}

       {# Load Bootstrap CSS and JS #}
           {# We can initialize boostrap css as bootstrap javascript       #}
           {# The reason we are using bootstrap CDN is for report printing #}
           {# boostrap css must have media set to all, so that we can have #}
           {# same styles for both screen and printing. Unfortunately      #}
           {# in the plugin django-boostrap3 we don't have an option       #}
           {# to change media from screen to all.                          #}
       <link rel="stylesheet" type="text/css" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
       {% bootstrap_javascript %}

       {# Load SweetAlert CSS and JS #}
       <link rel="stylesheet" type="text/css" href="//cdnjs.cloudflare.com/ajax/libs/sweetalert/1.0.1/sweetalert.min.css" media="screen">
       <script src="//cdnjs.cloudflare.com/ajax/libs/sweetalert/1.0.1/sweetalert.min.js"></script>

       {# Load OpenSans Google Font #}
       <link href='http://fonts.googleapis.com/css?family=Droid+Sans' rel='stylesheet' type='text/css'>

       {# Load Ansr CSS and JS #}
       <link rel="stylesheet" type="text/css" href="{% static 'css/site.min.css' %}" media="screen">
       <link rel="stylesheet" type="text/css" href="{% static 'css/print.css' %}" media="print">

       {# Load FullCalendar CSS and JS #}
       <script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/2.8.4/moment.min.js"></script>
       <link href="//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.2.3/fullcalendar.min.css" media="screen" rel="stylesheet">
       <script src="//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.2.3/fullcalendar.min.js"></script>

       {# Load Font-Awesome CSS #}
       {% fontawesome_stylesheet %}

       <script>
            $(document).ready(function() {
                $('#calendar').fullCalendar({
                    eventOrder:'id',
                    aspectRatio: 2.12,
                    eventLimit: true,
                    events: [
                        {% block events %}{% endblock %}

                    ],
                    header:{
                      left: 'prev, next today ',
                      center: 'title',
                      right: 'month, basicWeek, basicDay'
                    },
                    eventClick: function(calEvent, jsEvent, view) {
                      eId = Number(calEvent._id);
                        $('#calendar').fullCalendar('removeEvents', eId);
                        if (eId === parseInt(eId, 10))
                            swal({
                              title: "Are you sure?",
                              text: "Do you want me to forget your remainder?",
                              type: "warning",
                              showCancelButton: true,
                              confirmButtonColor: "#DD6B55",
                              confirmButtonText: "Yes, Please!",
                              closeOnConfirm: false,
                              cancelButtonText: "No, Cancel!",
                              closeOnCancel: false
                            },
                            function(isConfirm) {
                              urlVar = "/myansrsource/remainder/delete/" + eId + "/";
                              if (isConfirm) {
                                  $.ajax({
                                    dataType: "json",
                                    url: urlVar,
                                  });
                                  swal("Done!", "I forgot your remainder", "success");
                              }
                              else
                                  swal("Stay Cool", "I will remaind you :). Please refresh the page.", "success");
                            });
                    },
                })
            });
       </script>
       <script>
            $(function () {
              $('[data-toggle="tooltip"]').tooltip()
            })
       </script>

       {% block addFormMedia %}{% endblock %}

       {% include 'autocomplete_light/static.html' %}

       {% include 'session_security/all.html' %}
    </head>
    <body>
	<!-- Ansr -->
	<div class={% block container %}"container"{% endblock %}>
		<!-- Ansr Logo and role based menuset -->
		<div class="row">
			<nav class="navbar navbar-default navbar-fixed-top ansrMenuShadow" role="navigation">
				<!-- Ansr brand logo -->
				<div class="navbar-header">
					{% block responsiveMenu %}{% endblock %}
					<a class="navbar-brand">
						<img src="{% static 'images/ansrlogo.png' %}"
						     class="img-responsive ansrLogo" />
					</a>
				</div> <!-- End of the Ansr Brand Logo -->
				<!-- Ansr role based menuset -->
				 <div class="collapse navbar-collapse" id="example-navbar-collapse">
					 <ul class="nav navbar-nav navbar-right" style="padding-right: 15px;">
						{% block ansrMenu %}{% endblock %}
					 </ul>
				</div>
			</nav>
		</div><!-- End of Ansr Logo and role based menuset-->
		<!-- Ansr body -->
		<div class="row">
		{% block content  %}{% endblock  %}
		</div><!-- End of Ansr body -->
		<!-- Ansr footer -->
		<div class="row">
			<nav class="navbar navbar-default navbar-fixed-bottom col-lg-12 col-xs-12 col-md-12" role="navigation">
				<div class="navbar-inner navbar-content-center">
					<span class="col-lg-6 col-xs-12 col-md-12 col-lg-offset-3 ansrFooterText">
						<small>&copy; 2015. ansrsource. All rights reserved.</small>
					</span>
				</div>
			</nav>
		</div><!-- End of Ansr Footer -->
      	</div>
       <script src='{% static 'js/main.js' %}' type="text/javascript"></script>

        <!--   block to be inherited for page specific JavaScript -->
       {% block page_specific_JS %}{% endblock %}

    </body>
</html>
