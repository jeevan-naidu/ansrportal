/* following for choose tabs and dashboard page */
// Get the html for .form-group
var domObj = $('.qms-allocators').html();
var globalObj;

// Clear the existing html in .form-group
var clearDom = function(){
    $('.form-group').remove();
}
 function populateNames(theObj){

    $('.qms-allocators select').html('');

    for (var key in theObj['team_members']) {
      if (theObj['team_members'].hasOwnProperty(key)) {

        // changes all the select boxes simultaneously
        $('.qms-allocators select').append("<option value="+ key +">" + theObj['team_members'][key] + "</option>");
        var option_length = $('#select-field> option').length;

        if(option_length>0) {
             $('.qms-allocators,.qms-add-field ,.submit').show();

        }
        else { $('.qms-allocators,.submit,.qms-add-field').show();

        }
      }
    }
}

function array_flip( trans )
{
    var key, tmp_ar = {};

    for ( key in trans )
    {
        if ( trans.hasOwnProperty( key ) )
        {
            tmp_ar[trans[key]] = key;
        }
    }

    return tmp_ar;
}

function resetBtn(){
    if($('#select-field > option').length > 0){
        $('#qms-add-field').removeAttr('disabled');
    }
}


function assignMandatory(theObj){
    for (var key in theObj['user_tab']){
        if(theObj['user_tab'].hasOwnProperty(key)){
            <!--console.log('the key is ' + key + ' and the value is ' + theObj['user_tab'][key]);-->
            $('.form-group span:contains('+ key +')').parent().parent().find('select option[value=' + theObj['user_tab'][key] + ']').prop("selected", true);
            // console.log(the_form_group);
            // $('#id_author option[value=""]').prop("selected", true);
        }
    }
}
function load_chapters(chapters){
    $( "#search" ).empty();
    for (var key in chapters) {
        if(chapters.hasOwnProperty(key)){
//            console.log("key"+key+"value"+chapters[key]);

            $( "#search" ).append("<option value=" + key + " >" + chapters[key] + "</option>");
        }
    }
}

// Main function : populating the DOM
function populateForm (theObj){
// debugger
    var i = 0 ;
    clearDom();

    <!--console.log(theObj);-->

    theObj['tab_name'] = array_flip(theObj['tab_name'])

    for (var key in theObj['tab_name']) {


      if (theObj['tab_name'].hasOwnProperty(key)) {     // opening object
        if (theObj['tabs'][theObj['tab_name'][key]] == true || typeof(theObj['user_tab'][theObj['tab_name'][key]]) == 'number') {
            $('.qms-allocators').append(domObj);
            $('.qms-allocators .form-group:last-child select').attr({name:"user_"+key ,id:"user_"+key});
            $('.qms-allocators .form-group:last-child input.order-number').attr({name:"order_"+key ,id:"order_"+key});
            $('.qms-allocators .form-group:last-child input.order-number').attr('required',  true);
//            if (theObj['current_tab'] === false ) {
//                console.log("c"+theObj['current_tab'] +typeof(theObj['current_tab']))
//                $('.qms-allocators .form-group:last-child input.tab_complete').attr({name:"tab_complete_"+key ,id:key});
//                if(key ==1)
//                $('.tab-order-1').next().show()
//            }
//            else{
                $('.qms-allocators .form-group:last-child input.tab_complete').attr({name:"tab_complete_"+key ,id:key});
                if(theObj['current_tab']!== false){
                    if(parseInt(theObj['current_tab'])!=NaN  && parseInt(theObj['current_tab']) == parseInt(key) ) {
//                    console.log("if");
                        $('.qms-allocators .form-group:last-child input.tab_complete').attr({name:"tab_complete_"+key ,id:key});
                        $('#'+key).show();

                        }

                }

            if(theObj['show_lead_complete']==true){
               $('.qms-allocators2').show();
            }
            $('.qms-allocators .form-group:last-child .field-name span:first-child').html(theObj['tab_name'][key]);

            populateNames(theObj);

        }else{
            <!--$('select#select-field').html('');-->
            $('select#select-field').append("<option name=" + key + " >" + theObj['tab_name'][key] + "</option>");
        }

      }
    }

    resetBtn();

} // end of populate form

function check_input() {
    var is_set=0;
    $('.filter_form').each(function(i, obj) {
            <!--console.log(obj.name+'&#45;&#45;'+obj.value);-->
            if (obj.value != '') is_set++;
       });
       if (is_set!=0 && is_set==$('.filter_form').length) return true;
       else return false;
}


function getTabOrder(){
    $('.qms-allocators .form-group').each(function(){
        var tab_order_key = $(this).find('.field-name span').html();
        if(!$(this).find('input.order-number').val()){
            /*console.log('has no value ' + $(this).find('input.order-number').val());*/
            var tab_order_value = '0';
            /*console.log('tab_order_value is ' + tab_order_value);*/
        }else {
            /*console.log('has a value which is ' + $(this).find('input.order-number').val());*/
            var tab_order_value = $(this).find('input.order-number').val();
            /*console.log('tab_order_value is ' + tab_order_value);*/
        }

        globalObj.tab_order[tab_order_key] = tab_order_value;
    })
        <!--console.log(globalObj);-->
}

// Function to order the tabs
function orderTabs(theObj){
    theObj['tab_order'] = array_flip(theObj['tab_order'])

    // Assigning values to input field

    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key)){
            <!--console.log(order_key, theObj['tab_order'][order_key]);-->
            if(order_key > 0){
                $('.field-name span:contains(' + theObj['tab_order'][order_key] + ')').parent().parent().find('input.order-number').val(order_key);
                $('.field-name span:contains(' + theObj['tab_order'][order_key] + ')').parent().parent().find('input.order-number').addClass('tab-order-'+order_key);
                if(theObj['current_tab'] === false &&  order_key == '1')  {
//                console.log("false"+order_key);
                    $('.tab-order-'+order_key).next().show()
                }
            }
        }
    }

    /*debugger*/

    // Re-arranging

/*    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key) && order_key > 0){
            $('input.order-number').hasClass('tab-order-'+ order_key + '').closest('.form-group').addClass('marked');
            debugger;
        }
    }*/

/*    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key) && order_key > 0){
            $('input.order-number[value="' + order_key + '"]').closest('.form-group').addClass('marked');
            debugger;
        }
    }*/

    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key) && order_key > 0){
            $('input.order-number.tab-order-' + order_key + '').closest('.form-group').addClass('marked');
            var the_form_group = $('.qms-allocators .form-group.marked').html();
            <!--console.log(the_form_group);-->
            $('.qms-allocators .form-group.marked').remove();
            $('.qms-allocators').append('<div class="form-group"></div>');
            $('.qms-allocators .form-group:last-child').html(the_form_group);
            /*debugger*/

        }
    }

    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key) && order_key == 0){
            $('input.order-number.tab-order-' + order_key + '').closest('.form-group').addClass('marked');
            var the_form_group = $('.qms-allocators .form-group.marked').html();
            <!--console.log(the_form_group);-->
            $('.qms-allocators .form-group.marked').remove();
            $('.qms-allocators').append('<div class="form-group"></div>');
            $('.qms-allocators .form-group:last-child').html(the_form_group);
           /* debugger*/

        }
    }


    // Re-assigning input values

    for (var order_key in theObj['tab_order']){
        if(theObj['tab_order'].hasOwnProperty(order_key)){
            <!--console.log(order_key, theObj['tab_order'][order_key]);-->
            if(order_key > 0){
                $('.field-name span:contains(' + theObj['tab_order'][order_key] + ')').parent().parent().find('input.order-number').val(order_key);
                $('.field-name span:contains(' + theObj['tab_order'][order_key] + ')').parent().parent().find('input.order-number').attr('name', 'order_'+order_key);
            }
        }
    }





    // Flipping again so that submit function doesn't add keys that were values before
    theObj['tab_order'] = array_flip(theObj['tab_order'])


    $('.qms-allocators .form-group select').each(function(){
        theNum = $(this).attr('name');
        theNum = theNum.replace(/[^0-9]/g, '');
        $(this).parent().find('input.order-number').attr('name', 'order_'+theNum);
    })
} // end of order tabs functions



function checkIfArrayIsUnique(myArray) {
  return myArray.length === new Set(myArray).size;
}

function isInArray(needle, haystack) {
 var length = haystack.length;
 for (var i = 0; i < length; i++) {
 if (haystack[i] == needle)
  return true;
 }
 return false;
}

function checkIfConsecutive(myArray){
    myArray = myArray.sort();
    var arrayLength = myArray.length - 1;
    var arrayDIff;
    for(var i = 0; i < arrayLength; i++){
        arrayDIff = parseInt(myArray[i+1]) - parseInt(myArray[i]);
        if(arrayDIff != 1){
            return false
        }
    }
}


function checkOrder(){
    var the_order_array = [];
    var i=1;
    var orderStatus;
    $('.qms-allocators .form-group input.order-number').each(function(){
        var entry = $(this).val()
        the_order_array.push(entry);
        i++;
    })
    if (checkIfArrayIsUnique(the_order_array) == false) {
        alert('there is a duplicate');
        orderStatus = false;
    }
    if (isInArray(1,the_order_array) == false) {
        alert('please start with 1');
        orderStatus = false;
    }
    if (checkIfConsecutive(the_order_array) == false) {
        alert('please enter consecutive numbers');
        orderStatus = false;
    }
    return orderStatus;

}

function disableOrder(theObj){
//console.log("theObj"+JSON.stringify(theObj));
    disable_count = 0;
    loop_counter = 0 ;
    for (var disableKey in theObj['can_edit']){
        if(theObj['can_edit'].hasOwnProperty(disableKey)){
            loop_counter++;
            if (theObj['can_edit'][disableKey] == false) {
                var order = "order_" + disableKey;
                var drop_down = "user_" + disableKey;
                $('input[name=' + order + '] ,[name=' + drop_down + '] ').prop('disabled',"True");
                 $('input[name=' + order + '],[name=' + drop_down + ']').attr('title', "This step is completed/on progress can't be edited");
                 disable_count ++;
            }

        }
    }
      if(loop_counter == disable_count && disable_count !=0) {
        globally_locked = true;
//        console.log("im here");
        $('#qms-submit').prop("disabled",true);
      }
}




function mark_as_complete(element=null) {
        is_lead = false;
        if ($("#lead_tab_complete").attr('data-diffvalue') ){
            if($(element).data("diffvalue") == 0 ) text = "You are going to mark this project as completed!";
            if ($(element).data("diffvalue") !=1 && $(element).data("diffvalue") != 0) {s = " chapters are "} else {s= " chapter is "}
            text = $(element).data("diffvalue") + " " +s + " not created yet, do you still want to mark it as completed ?"
            title = "You are going to mark this project as completed!"
            project_id = $(element).data('project')
            lead_review = $('#review_feedback_'+project_id).val()
            data = {"is_lead":true ,"project_id":$(element).data('project'),"feedback":lead_review };
            is_lead = true;
            success_msg = "Project is marked as completed!"
        }
        else{
            text = "You are going to mark this review group as completed!";
            data = {"tab_id": element.id ,"is_lead":is_lead };
            success_msg = "Review is marked as completed!"
            title = "Are you sure?"
        }
        swal({
          title: title,
          text: text,
          type: "warning",
          showCancelButton: true,
          confirmButtonColor: "#DD6B55",
          confirmButtonText: "Yes, Mark it!",
          cancelButtonText: "No, cancel plx!",
          closeOnConfirm: false,
          closeOnCancel: false
        },
        function(isConfirm){
            if (isConfirm) {
            $('#reviewComplete').show();
                $.ajax({
                    url: '/qms/mark_as_completed/',
                    type: 'GET',
                    dataType :'json',
                    data: data,
                    success: function (data) {
//                    console.log(JSON.stringify(data));
                        if(!is_lead ) {
                            if (data['result'] == true) {
                                var num_items = $('.order-number').length;
                                var disabled_count = 0;
                                sweetAlert("Heya...", success_msg, "success");
                                if(!is_lead){
                                    $(element).hide();
                                    var new_id = parseInt(element.id)+1;
//                                    console.log("new_id"+new_id);
                                    $('#'+new_id).show();
                                    $("#user_"+element.id).prop('disabled',true);
                                    $("#order_"+element.id).prop('disabled',true);
                                    count = 0;

                                    $(".order-number").each(function(index) {
//                                    console.log(this.id+"-"+element.id);
                                    id = this.id.split('_')
                                     if (id[1] == element.id) {
//                                        console.log("if");
                                        count++;
                                        if (index === num_items - 1 && data['can_show_button']) {
//                                            console.log("last");
    //                                         $('.qms-allocators2').show();
                                        }
                                        return true;
                                     }
                                     if (count ==1 ) {
//                                        console.log("im in");
                                        id = this.id.split('_')
                                        $('#'+id[1]).show();
                                        $(".order-number").each(function() {
                                            if($(this).is(':disabled')) {
                                                disabled_count++;
                                            }
                                        });
//                                        console.log("disabled_count"+disabled_count+"num_items"+num_items);
                                        if(disabled_count!=0 && disabled_count == num_items && data['can_show_button']){
    //                                        $('.qms-allocators2').show();
                                        }
                                        return false;

                                     }
                                    });

                                }
                                else{globally_locked = true;
//        console.log("im here");
                                    $("[name^=user_],[name^=order_]").prop('disabled',"True");
                                    $('.qms-allocators2').hide();

                                }

                            }
                            else {
                                swal("Oops", "Please contact admin unable to complete the request)", "error");
                            }
                        } else {
                            if (data['result'] == true) {
                                sweetAlert("Heya...", success_msg, "success");
                                $(element).removeClass("btn-danger").addClass("btn-white").prop('onclick',null).off('click');
                                $('#reviewComplete').hide();
                                $('#review_modal').prop('disabled',true)
                            }

                            }
                    },

                });
            }
            else {
                swal("Cancelled", "Cool  :)", "error");
            }


        });
}

$(document).ready(function(){

$('#filter_form').submit(function() {
    return checkOrder();
});




   $(':input[name$=chapter]').on('change', function()  {
        if($(':input[name$=component]').val()!='') {
            $(':input[name$=component]').trigger('change');
         }
    });

    $(':input[name$=author]').on('change', function()  {

        // Clearing the optional fields list

        $('#select-field').html('The end');
        $('#qms-add-field').prop('disabled', true);


        if(check_input()) {
              $.ajax({
                url: '/qms/get_template_process_review/',
                type: 'GET',
                dataType :'json',
                async :false,
                data: {"template_id": $(':input[name$=template]').val() , "project_id" :  $(':input[name$=project]').val() ,"qms_process_model" :$(':input[name$=qms_process_model]').val(),
                "chapter" :$(':input[name$=chapter]').val(),"author" :$(':input[name$=author]').val(),"component" :$(':input[name$=component]').val() },
                success: function (data) {
                    if (data['is_completed'] == true) {
                        $('#copy_configurations,#div_submit').hide();
                        sweetAlert("Oops...", "This is project is already marked as completed!", "success");
                    }
                    if (data['config_missing'] == true) {
                        sweetAlert("Oops...", "Configuration is missing!", "error");
                        return false;

                    }
                    $("[name^=user_],[name^=order_]").prop('disabled',"False");
//                console.log("can edit keys"+Object.keys(data['can_edit']));
//                console.log("can edit values"+Object.values(data['can_edit']));
//                console.log("tab_order values"+Object.values(data['tab_order']));
                    if (data['is_completed'] == false) {
                        load_chapters(data['chapters']);
                    }
                    populateForm(data);
                    orderTabs(data);
                    assignMandatory(data);
                    disableOrder(data);

                    // globalObj to capture the order of tabs

                    globalObj = data;
                    can_edit = Object.values(data['can_edit'])
                    if (can_edit.length != 0 && $.inArray(false, can_edit) != -1)
                    {
                      // found it
                    }
                    else{
                        tab_order_obj = Object.values(data['tab_order']);
//                        console.log("len"+tab_order_obj.length);
//                        if ( tab_order_obj.length != 0) {
//                            $('#1').show();
//                        } else $('#1').hide();
                    }
                },

            });

        }
    });

$(':input[name$=component]').change(function(){
if($(':input[name$=project]').val() !='' &&  $(':input[name$=chapter]').val() !='') {
        $.ajax({
                url: '/qms/fetch_author/',
                type: 'GET',
                dataType :'json',
                data: {"project_id" :  $(':input[name$=project]').val() , "component_id" :  $(this).val() ,"chapter_id" :  $(':input[name$=chapter]').val() },
                beforeSend : function(data) { $(':input[name$=author]').empty() ; $('.select-name ').empty() ;},
                success: function (data) {
                    for (var key in data) {
                        if (data.hasOwnProperty(key)) {
                            $(':input[name$=author]').removeAttr("disabled");
                            if(key == 'team_members'){
                                $(':input[name$=author]').append($('<option>', {
                                        value: "",
                                        text: "Select An Author",
                                    }));
                                for (var k in data[key]){
                                    $(':input[name$=author]').append($('<option>', {
                                        value: k,
                                        text: data['team_members'][k],
                                    }));
                                }
                            }
                        }

                    }
                    if(data['author'] != 'None' || data['author'] != '' ) {
                        $('#id_author option[value='+data['author']+']').prop("selected", true);
                    }
                    else if (data['author'] == 'None'){
                         $('#id_author option[value=""]').prop("selected", true);
                    }
                },
                complete: function (data) { $(':input[name$=author]').trigger('change');}

        });
    }
});

    $('#qms-add-field').click(function(e){
        e.preventDefault();
        optCount = $('#select-field > option').length; // The bug

        if (optCount > 1) {

            theField = $('#select-field').val();
            theID = $('#select-field option:selected').attr('name');
            $('#select-field option:selected').remove();
            theClone = $('.qms-allocators .form-group:first-child').clone().appendTo('.qms-allocators');
            $('.qms-allocators .form-group:last-child').find('.field-name span:first-child').html(theField);
//            console.log('user_'+theID +'---'+'order_'+theID)
            $('.qms-allocators .form-group:last-child').find('select').attr('name', 'user_'+theID);
            $('.qms-allocators .form-group:last-child').find('input.order-number').attr('name', 'order_'+theID);
            $('.qms-allocators .form-group:last-child').find('input.order-number').prop('disabled',false);
            $('.qms-allocators .form-group:last-child').find('select').prop('disabled',false);
            $('.qms-allocators .form-group:last-child').find('input.order-number').val('');

        }else if (optCount == 1) {
            theField = $('#select-field').val();
            theID = $('#select-field option:selected').attr('name');
            $('#select-field option:selected').remove();
            theClone = $('.qms-allocators .form-group:first-child').clone().appendTo('.qms-allocators');
            $('.qms-allocators .form-group:last-child').find('.field-name span:first-child').html(theField);
//            console.log('user_'+theID +'---'+'order_'+theID)
            $('.qms-allocators .form-group:last-child').find('select').attr('name','user_'+theID);
            $('.qms-allocators .form-group:last-child').find('input.order-number').attr('name', 'order_'+theID);
            $('.qms-allocators .form-group:last-child').find('input.order-number').prop('disabled',false);
            $('.qms-allocators .form-group:last-child').find('select').prop('disabled',false);
            $('.qms-allocators .form-group:last-child').find('input.order-number').val('');
            $('#select-field').html('The end');
            globally_locked = true;


            $('#qms-add-field').prop('disabled', true);

        }

         $('.qms-allocators .form-group:last-child input.order-number').attr({name:"order_"+theID ,id:"order_"+theID});
         $('#order_'+theID).removeClass().addClass("form-control input-sm order-number tab-order-"+theID);
         $('.qms-allocators .form-group:last-child input.tab_complete').attr({name:"tab_complete_"+theID ,id:theID});

        $('#'+theID).hide();
    })




    $('body').addClass("nav-left-hide remove-navbar nav-left-medium");



    // Function Calls

/*    $('#qms-submit').mouseover(function(e){
        getTabOrder();
    })*/



})//./doc.ready

$(':input[name$=project]').on('change', function() {
       if(check_input()) {
            $('.reset_field ').not(this).val(null).trigger('change');
            $(".qms-allocators").empty();
       }
});





/* functions ends for choose tabs and dashboard page */

