// JavaScript Document
jQuery(document).ready(function($){
	//Put Your Custom Jquery or Javascript Code Here


	// Height script for text section


	heightFunction = function(){
		hgt1=$('.jsh1').css('height');
		$('.jsh2').css('height', hgt1);
	}

	// Height for navbar

	navHeight = function(){
		vph = $(window).height();
		console.log(vph);
		vphp = parseInt(vph);
		vphp -= 106;
		console.log(vphp);
		$('.nbh').css('height', vphp + 'px' );
	}

	// navHeight();
	heightFunction();





	$(window).resize(function(){
	// navHeight();
		heightFunction();
	})





	
});