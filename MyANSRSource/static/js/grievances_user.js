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
                                                $("#modal_body").html("<p style='color:red'>Oops.. something went wrong at server end. Below are the details: " 
                                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a snapshot of this error and send it to the administrator</p>");
                                                alert("Server error" + "-" + textStatus + "-" + errorThrown);
                                                HideAjaxLoader(ajax_loader_element);
                                                },
                                            }
                                        );
                        });
            
            // refresh the parent url when modal is 
            $('#add_grievance_popup').on('hidden.bs.modal', function () {
                    $("#modal_body").html("Loading.. please wait..");
                    
                    if ($(".new_notification").length) {
                        setTimeout(function(){
                            $(".new_notification").fadeOut("slow");
                         }, 10000);
                    
                    }
                    
                    })
            
            
            
            
            
            }); // dom ready
    
    function reloadJS(){
    // reload the js for file field
                $.getScript( "/static/js/jquery.ui.widget.js", function( data, textStatus, jqxhr ) {
                console.log( textStatus ); // Success
                console.log( jqxhr.status ); // 200
                console.log( "1 Load was performed." );
              });
                
                // reload the js for file field
                $.getScript( "/static/js/bootstrap-filestyle.min.js", function( data, textStatus, jqxhr ) {
                console.log( textStatus ); // Success
                console.log( jqxhr.status ); // 200
                console.log( "2 Load was performed." );
              });
    }
    
    RateAndClosureFormSubmit();
    EscalationFormSubmit();
    
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
                                    $("#status_"+form_id).html('<i class="fa fa-lock fa-lg" style="color:#d9534f;"></i>');
                                }
                                HideAjaxLoader(ajax_loader_element);
                            },
                            error: function(XMLHttpRequest, textStatus, errorThrown) {
                                $("#RateAndClosureForm_errors_"+form_id).html("Oops.. something went wrong at server end. Below are the details: " 
                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a snapshot of this error and send it to the administrator");
                                alert("Server error" + "-" + textStatus + "-" + errorThrown);
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
                                $("#EscalationForm_errors_"+form_id).html("Oops.. something went wrong at server end. Below are the details: " 
                                    + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a snapshot of this error and send it to the administrator");
                                alert("Server error" + "-" + textStatus + "-" + errorThrown);
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


