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
		// console.log(vph);
		// vphp = parseInt(vph);
		vph -= 106;
		// console.log(vphp);
		$('.vd_content-wrapper').css('min-height', vph + 'px' );
	}


/*	extendRibbon = function(){
		$('#oneteam-ribbon').addClass('extended');
	}*/


	// Function Calls


	navHeight();
	heightFunction();


	$(window).resize(function(){
		navHeight();
		heightFunction();
	})

	$(window).load(function(){
		heightFunction();
		setTimeout(function(){ 
			extendRibbon(); 
		}, 1000);
	})





	
});