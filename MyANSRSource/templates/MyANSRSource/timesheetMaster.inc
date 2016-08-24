{% extends 'master.html' %}

{% load bootstrap3 %}
{% load fontawesome %}

{% block siteTitle %}myansrsource:Timesheet Entry{% endblock %}

{% block content  %}






<script type="text/javascript">
	
jQuery(document).ready(function() {
        
	jQuery('.carousel[data-type="multi"] .item').each(function(){
		var next = jQuery(this).next();
		if (!next.length) {
			next = jQuery(this).siblings(':first');
		}
		next.children(':first-child').clone().appendTo(jQuery(this));
	  
		for (var i=0;i<2;i++) {
			next=next.next();
			if (!next.length) {
				next = jQuery(this).siblings(':first');
			}
			next.children(':first-child').clone().appendTo($(this));
		}
	});
        
});
	
</script>



<style>
.carousel-control.left, .carousel-control.right {
	background-image:none;
}

.img-responsive{
	width:100%;
	height:auto;
}

/*@media (min-width: 992px ) {
	.carousel-inner .active.left {
		left: -25%;
	}
	.carousel-inner .next {
		left:  25%;
	}
	.carousel-inner .prev {
		left: -25%;
	}
}

@media (min-width: 768px) and (max-width: 991px ) {
	.carousel-inner .active.left {
		left: -33.3%;
	}
	.carousel-inner .next {
		left:  33.3%;
	}
	.carousel-inner .prev {
		left: -33.3%;
	}
	.active > div:first-child {
		display:block;
	}
	.active > div:first-child + div {
		display:block;
	}
	.active > div:last-child {
		display:none;
	}
}

@media (max-width: 767px) {
	.carousel-inner .active.left {
		left: -100%;
	}
	.carousel-inner .next {
		left:  100%;
	}
	.carousel-inner .prev {
		left: -100%;
	}
	.active > div {
		display:none;
	}
	.active > div:first-child {
		display:block;
	}
}*/
</style>




<div class="container text-center" style="width:500px;margin:auto">
<div class="carousel slide row" data-ride="carousel" data-type="multi" data-interval="2000" id="fruitscarousel">

    <div class="carousel-inner">


        <div class="item active">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/banana.jpg" class="img-responsive"></a></div>
        </div>
        <div class="item">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/currant.jpg" class="img-responsive"></a></div>
        </div>
        <div class="item">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/mango.jpg" class="img-responsive"></a></div>
        </div>
        <div class="item">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/strawberries.jpg" class="img-responsive"></a></div>
        </div>
        <div class="item">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/banana.jpg" class="img-responsive"></a></div>
        </div>
        <div class="item">
            <div class="col-md-2"><a href="#"><img src="http://www.jquery-az.com/boots/images/strawberries.jpg" class="img-responsive"></a></div>
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
