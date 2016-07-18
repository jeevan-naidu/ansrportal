// JavaScript Document
jQuery(document).ready(function($){
	//Put Your Custom Jquery or Javascript Code Here


	// Height script for text section


	heightFunction = function(){
		hgt1=$('.jsh1').css('height');
		$('.jsh2').css('height', hgt1);
	}

	heightFunction();
	$(window).resize(function(){
		heightFunction();
	})





	
});