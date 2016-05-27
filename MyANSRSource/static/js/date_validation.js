/**
 * DHTML date validation script for dd/mm/yyyy. Courtesy of SmartWebby.com (http://www.smartwebby.com/dhtml/datevalidation.asp)
 */
// Declaring valid date character, minimum year and maximum year
var dtCh= "/";
var d = new Date();
var n = d.getFullYear();
var minYear=n;
var maxYear=n;

function isInteger(s){
	var i;
    for (i = 0; i < s.length; i++){
        // Check that current character is number.
        var c = s.charAt(i);
        if (((c < "0") || (c > "9"))) return false;
    }
    // All characters are numbers.
    return true;
}

function stripCharsInBag(s, bag){
	var i;
    var returnString = "";
    // Search through string's characters one by one.
    // If character is not in bag, append to returnString.
    for (i = 0; i < s.length; i++){
        var c = s.charAt(i);
        if (bag.indexOf(c) == -1) returnString += c;
    }
    return returnString;
}

function daysInFebruary (year){
	// February has 29 days in any year evenly divisible by four,
    // EXCEPT for centurial years which are not also divisible by 400.
    return (((year % 4 == 0) && ( (!(year % 100 == 0)) || (year % 400 == 0))) ? 29 : 28 );
}
function DaysArray(n) {
	for (var i = 1; i <= n; i++) {
		this[i] = 31
		if (i==4 || i==6 || i==9 || i==11) {this[i] = 30}
		if (i==2) {this[i] = 29}
   }
   return this
}

function isDate(dtStr){
	var daysInMonth = DaysArray(12)
	var pos1=dtStr.indexOf(dtCh)
	var pos2=dtStr.indexOf(dtCh,pos1+1)
	var strDay=dtStr.substring(0,pos1)
	var strMonth=dtStr.substring(pos1+1,pos2)
	var strYear=dtStr.substring(pos2+1)
	strYr=strYear
	if (strDay.charAt(0)=="0" && strDay.length>1) strDay=strDay.substring(1)
	if (strMonth.charAt(0)=="0" && strMonth.length>1) strMonth=strMonth.substring(1)
	for (var i = 1; i <= 3; i++) {
		if (strYr.charAt(0)=="0" && strYr.length>1) strYr=strYr.substring(1)
	}
	month=parseInt(strMonth)
	day=parseInt(strDay)
	year=parseInt(strYr)
	if (pos1==-1 || pos2==-1){
		alert("The date format should be : dd/mm/yyyy")
		return false
	}
	if (strMonth.length<1 || month<1 || month>12){
		alert("Please enter a valid month")
		return false
	}
	if (strDay.length<1 || day<1 || day>31 || (month==2 && day>daysInFebruary(year)) || day > daysInMonth[month]){
		alert("Please enter a valid day")
		return false
	}
	if (strYear.length != 4 || year==0 || year<minYear || year>maxYear){
		alert("Please enter a valid 4 digit year between "+minYear+" and "+maxYear)
		return false
	}
	if (dtStr.indexOf(dtCh,pos2+1)!=-1 || isInteger(stripCharsInBag(dtStr, dtCh))==false){
		alert("Please enter a valid date")
		return false
	}
return true
}

/* following functions relates to  both grievance  and leave module sharing common functionality */
function date_validation(from,to)
{
    var is_different = false;
    if($('#'+from).val() != "" || $('#'+to).val() != "") {

        var frm_check_index  = $('#'+from).val().indexOf("/");
        if(frm_check_index != -1) {
            var frm_date = $('#'+from).val().split("/");
        }
        else {
            var frm_date = $('#'+from).val().split("-");
            is_different = true;
        }

        var converted_frm_date = new Date (frm_date[2],frm_date[1]-1,frm_date[0]);

        var to_check_index  = $('#'+to).val().indexOf("/");
        if(to_check_index != -1) {
            var id_closure_date = $('#'+to).val().split("/");
        }
        else  var id_closure_date = $('#'+to).val().split("-");

        var converted_id_closure_date = new Date (id_closure_date[2],id_closure_date[1]-1,id_closure_date[0]);

        if(converted_frm_date > converted_id_closure_date) {
            alert("Ending date Cannot Be Greater Than From Date ");
            return false
        }
        var from_date = $('#'+from).val() ;
        var to_date = $('#'+to).val()

        if(is_different) {
            from_date = $('#'+from).val().split('-');
            from_date = from_date[2]+'/'+from_date[1]+'/'+from_date[0];
            to_date = $('#'+to).val().split('-');
            to_date = to_date[2]+'/'+to_date[1]+'/'+to_date[0];
        }

        if (isDate(from_date) == false || isDate(to_date) == false ){
            alert("Please Enter The Valid Date ");
            return false
        }
    }
    return true
}


$('.page, .next, .prev').click(function(){
    if ( $( "#reset_button" ).length ) {
        $('#reset_button').trigger('click');
    }
    formToDiv();
});



function formToDiv()
{
    var attrs = { };

    $.each($("form")[0].attributes, function(idx, attr) {
        attrs[attr.nodeName] = attr.nodeValue;
    });

    $("form").replaceWith(function () {
        return $("<div>", attrs).append($(this).contents());
    });
}



function input_elements_validation(class_name, url_link_name)

{    var none_count = 0;
     <!-- looping through input fields to whether at-least one input is selected is or not -->
    $('.'+class_name).each(function() {
        if($(this).val() != "none" && $(this).attr('id') != "post_page_count" && $(this).val() !=null && $(this).val() != '') {
            none_count+=1;
        }
    });

    <!-- allow form submission only if at-least one input is changed -->
    if ( none_count > 0 )  {
        <!-- we need the following code to ensure on filter form submission the page value is always 1 to ensure the pagination to work properly-->
         window.history.pushState("object or string", url_link_name, "/"+url_link_name+"/?page=1");
        $( "#filter_form" ).submit();
    }

    else if( none_count == 0 )  {
        alert("Please Select At-least One Filtering Option");
        return false
    }
    return true

}


 $('#reset_button').click(function(){
    $('.filter_class').each(function() {
         input_type = this.tagName ;
         if(input_type == 'INPUT')
         {
            $(this).val('')
         }
         if(input_type == 'SELECT') {
            $(this).prop('selectedIndex',0);
         }
         if(this.id == 'id_user-autocomplete') {
            if($("#id_user-deck").is(":visible") == true ) {
                $("#id_user-deck").hide();
                $('#id_user-autocomplete').show();
               document.getElementById("id_user").options.length = 0;
            }
         }
         if(this.id == 'id_grievance_id-autocomplete') {
            if($("#id_grievance_id-deck").is(":visible") == true ) {
                $("#id_grievance_id-deck").hide();
                $('#id_grievance_id-autocomplete').show();
               document.getElementById("id_grievance_id").options.length = 0;
            }
         }
    });

});