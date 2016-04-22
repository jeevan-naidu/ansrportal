//JavaScript for User grievances - Front-end only
		
$(document).ready(function(){
			
			
            //ajax request for registering a grievance on modal popup open
            $("#add_grievance_popup").on('shown.bs.modal', function(){
                    
                            $.ajax(
                                            {
                                                type : "GET",
                                                url : '/grievances/add/',
                                                data :"" ,
                                                success : function(data)
                                                {
                                                    $("#modal_body").html(data);
                                                    reloadJS();
                                                },
                                                error: function(XMLHttpRequest, textStatus, errorThrown) {
                                                $("#modal_body").html("<p style='color:red'>Oops! Something went wrong on the server. The details are below: " 
                                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a screenshot of this message and send it to <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
                                                HideAjaxLoader(ajax_loader_element);
                                                },
                                            }
                                        );
                        });
            
             
            //$('#add_grievance_popup').on('hidden.bs.modal', function () {
            //        $("#modal_body").html("Loading.. please wait..");
            //        
            //        if ($(".new_notification").length) {
            //            setTimeout(function(){
            //                $(".new_notification").fadeOut("slow");
            //             }, 10000);
            //        }
            //        })
            
                RateAndClosureFormSubmit();
                EscalationFormSubmit();
                
                
                $(".panel-title").click(function(){
                     $(this).find(".glyphicon").toggleClass("expand1");
                });
                
                
                // File size validation
                var fileExtension = ['jpg', 'csv','png', 'pdf', 'xlsx', 'xls', 'docx', 'doc', 'jpeg', 'eml'];
				$('.filestyle').bind('change', function() {
				if (this.files[0].size > 1000000) {
					alert("File size greater than 1MB not allowed");
					$(this).filestyle('clear');
				}
                else
                {
                    if ($.inArray($(this).val().split('.').pop().toLowerCase(), fileExtension) == -1) {
                        alert("Allowed file types : "+fileExtension.join(', '));
                        $(this).filestyle('clear');
                }
                }
                
                
                
				});
                
                
            
            }); // dom ready
    
    function reloadJS(){
                // reload the js for file field for ajax requests
                $.getScript( "/static/js/jquery.ui.widget.js", function( data, textStatus, jqxhr ) {
                console.log( textStatus ); // Success
                console.log( jqxhr.status ); // 200
                });
                
                // reload the js for file field for ajax requests
                $.getScript( "/static/js/bootstrap-filestyle.min.js", function( data, textStatus, jqxhr ) {
                console.log( textStatus ); // Success
                console.log( jqxhr.status ); // 200
                });
    }
    
  
    
    $(".HowItWorksContainer").click(function(){
        $(".DivRotate").toggleClass("DivVer");
        if ($(this).hasClass("how_it_works_hide")) {
            $(this).removeClass("how_it_works_hide");
        }
        else{
            $(this).addClass("how_it_works_hide");
        }
        
        });
    
    function RateAndClosureFormSubmit(event){
        $(".RateAndClosureForm").submit(function(){
                
            var formData = new FormData($(this)[0]);
            form_id = $(this)[0].grievance_id.value;
            form_element = $(this);
            ajax_loader_element = $("#SubmitAndCLoseFormAjaxLoader_" + form_id);
            
            swal({   title: "Are you sure you want to close this grievance?",
                text: "You will not be able to edit this grievance after submission!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Yes, Submit it!",
                cancelButtonText: "cancel",
                closeOnConfirm: true,
                closeOnCancel: true
                },
                function(isConfirm){
                    // If user clicks on ok;
                    if (isConfirm) {
                        ShowAjaxLoader(ajax_loader_element, form_element.width(), form_element.height());
                        $.ajax({
                            url: '/grievances/rate_and_close/',
                            type: 'POST',
                            data: formData,
                            success: function (data) {
                                if (data.errors) {
                                    $("#RateAndClosureForm_errors_"+form_id).html(data.errors);
                                }
                                if (data.record_added == true) {
                                    $("#RateAndClosureForm_"+form_id).parent().parent().parent().html(data.success_data_template);
                                    $("#status_"+form_id).html('<label type="label" class="label label-danger">Closed</label>');
                                }
                                HideAjaxLoader(ajax_loader_element);
                            },
                            error: function(XMLHttpRequest, textStatus, errorThrown) {
                                $("#RateAndClosureForm_errors_"+form_id).html("Oops! Something went wrong on the server. The details are below: " 
                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a screenshot of this message and send it to  <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a>.");
                                HideAjaxLoader(ajax_loader_element);
                            },
                            cache: false,
                            contentType: false,
                            processData: false
                        });
                    
                    } 
                    
                    
                   });
                    
            return false;
        });
}

function EscalationFormSubmit(event){
        
        // form_id is the grievance_id
    
        $(".EscalationForm").submit(function(){
                
            var formData = new FormData($(this)[0]);
            form_id = $(this)[0].grievance_id.value;
            form_element = $(this);
            ajax_loader_element = $("#EscalationFormAjaxLoader_" + form_id);
            
            swal({   title: "Are you sure?",
                text: "You will not be able to edit this grievance after submission!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Yes, Submit it!",
                cancelButtonText: "cancel",
                closeOnConfirm: true,
                closeOnCancel: true
                },
                function(isConfirm){
                    // If user clicks on ok;
                    if (isConfirm) {
                        ShowAjaxLoader(ajax_loader_element, form_element.width(), form_element.height());
                        $.ajax({
                            url: '/grievances/escalate/',
                            type: 'POST',
                            data: formData,
                            async: true,
                            success: function (data) {
                                if (data.errors) {
                                    $("#EscalationForm_errors_"+form_id).html(data.errors);
                                }
                                if (data.record_added == true) {
                                    $("#EscalationForm_"+form_id).parent().html(data.success_message);
                                }
                                HideAjaxLoader(ajax_loader_element);
                            },
                            error: function(XMLHttpRequest, textStatus, errorThrown) {
                                $("#EscalationForm_errors_"+form_id).html("Oops! Something went wrong on the server. The details are below:  " 
                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br>Please take a screenshot of this message and send it to  <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a>.");
                                HideAjaxLoader(ajax_loader_element);
                            },
                            cache: false,
                            contentType: false,
                            processData: false
                        });
                    } 
                   });

            return false;
        });
}
    
function ShowAjaxLoader(element, width, height){
    element.show();
    element.width(width).height(height);
    return false;
}
function HideAjaxLoader(element){
    element.fadeOut();
    return false;
}


