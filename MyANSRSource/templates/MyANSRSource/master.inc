<!DOCTYPE html>   
<html lang="en">
    <head>
       {% load static from staticfiles %}                                                                                                                     
       <meta charset="utf-8">                                                                                                                                  
       <meta http-equiv="X-UA-Compatible" content="IE=edge">                                                                                                   
       <meta name="viewport" content="width=device-width, initial-scale=1">                                                                                   
       <title>{% block siteTitle %}MyANSRSource{% endblock %}</title>

       {# Load the tag library #}
       {% load bootstrap3 %}

       {# Load Bootstrap CSS and JS #}
       {% bootstrap_css %}
       {% bootstrap_javascript %}

       {# Load Ansr CSS and JS #}
       <link rel="stylesheet" type="text/css" href="{% static 'css/site.css' %}">

       {# Load FullCalendar CSS and JS #}
       <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.8.4/moment.min.js"></script>
       <link href="//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.2.3/fullcalendar.min.css" media="screen" rel="stylesheet">
       <script src="//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.2.3/fullcalendar.min.js"></script>
       
       <script>
	$(document).ready(function() {
		$('#calendar').fullCalendar({
			aspectRatio: 2,
			events: [
				{% block events %}{% endblock %}
			]
		})

	});
       </script>
       
       {% block addFormMedia %}{% endblock %}

       {% include 'autocomplete_light/static.html' %}

       {% include 'session_security/all.html' %}
    </head>
    <body>
	<!-- Ansr -->
	<div class="container">
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
						<small>&copy; 2014.Fantain Sports Pvt. Ltd.,</small>
					</span>
				</div>
			</nav>
		</div><!-- End of Ansr Footer -->
      	</div>
       <script src='{% static 'js/main.js' %}' type="text/javascript"></script>
    </body>
</html>
