// /**
//  * Created by vivekpradhan on 15/2/17.
//  */
//   //   //ajax request for registering a leave on modal popup open
  $("#modal-container-process").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-")
      $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/approve/' + button_details[1] + "/",

          success : function (data) {
              $("#modal_body").html(data)
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });

  });

  $("#modal-container-Detail").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-");

          $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/update/' + button_details[1] + "/" ,
            data: {"action":button_details[2]},
          success : function (data) {
              $("#modal_body_detail").html(data);
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body_detail").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });


  });


$(".attachment").change(function(){
   var filename = $(this).val();
   var re = /(\.jpg|\.jpeg|\.gif|\.GIF|\.png|\.JPG|\.JPGEG|\.JPG|\.PNG|\.XLSX|\.xlsx|\.xls|\.XLS|\.DOCX|\.docx|\.doc|\.DOC|\.eml|\.EML)$/i;
   if(!re.exec(filename)){
       alert("File extension not supported");
       $(this).val('');
   }

});


$("#modal-container-process_update").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-");

          $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/get_process/' + button_details[1] + "/",


          success : function (data) {
              $("#modal_body_update").html(data);
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body_update").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });


  });

$("#modal-container-Detail").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-");

          $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/update/' + button_details[1] + "/",
          data: {"action": button_details[2]},
          success : function (data) {
              $("#modal_body_detail").html(data);
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body_detail").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });


  });

function delete_process(){
    button = event.target.id;
    button_details = button.split("-");
    swal({   title: "Are you sure?",
							text: "Do you want to delete your process request?",
							type: "warning",
							showCancelButton: true,
							confirmButtonColor: "#DD6B55",
							confirmButtonText: "Yes, Submit it!",
							cancelButtonText: "No, cancel it.",
							closeOnConfirm: true,
							closeOnCancel: true
							},
							function(isConfirm){
								if (isConfirm) {

								 $.ajax({
									url: '/process/'+ button_details[0] + '/update/' + button_details[1] + "/",
									type: 'DELETE',
									success: function () {

											 swal("Done!", "Process deleted", "success");
                                        window.location=window.location;


									},
									error: function(XMLHttpRequest, textStatus, errorThrown) {
												$("#modal_body_update").html("Oops! Something went wrong on the server. The details are below: "
													+ "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a screenshot of this message and send it to <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a>.");

											},
									cache: false,
									contentType: false,
									processData: false
								 });
								}
							   });
}

$("#modal-container-process_update").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-");

          $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/get_process/' + button_details[1] + "/",


          success : function (data) {
              $("#modal_body_update").html(data);
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body_update").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });


  });

$("#modal-container-Detail").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-");

          $.ajax({
         type: "GET",
          url: '/process/'+ button_details[0] + '/update/' + button_details[1] + "/",
          data: {"action": button_details[2]},
          success : function (data) {
              $("#modal_body_detail").html(data);
          },
          error: function (XMLHttpRequest, textStatus, errorThrown) {
            $("#modal_body_detail").html("<p style='color:red'>Oops! Something went wrong on the server. " +
                "The details are below: " + "<br>Status : "+ textStatus + "<br>Exception : "
                + errorThrown +
                "<br><br> Please take a screenshot of this message and send it to " +
                "<a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");
          }
      });


  });



function delete_process(){
    button = event.target.id;
      button_details = button.split("-");
    swal({   title: "Are you sure?",
							text: "Do you want to delete your process request?",
							type: "warning",
							showCancelButton: true,
							confirmButtonColor: "#DD6B55",
							confirmButtonText: "Yes, Submit it!",
							cancelButtonText: "No, cancel it.",
							closeOnConfirm: true,
							closeOnCancel: true
							},
							function(isConfirm){
								if (isConfirm) {

								 $.ajax({
									url: '/process/'+ button_details[0] + '/update/' + button_details[1] + "/",
									type: 'DELETE',
									success: function () {

											 swal("Done!", "Process deleted", "success");
                                        window.location=window.location;


									},
									error: function(XMLHttpRequest, textStatus, errorThrown) {
												$("#modal_body_update").html("Oops! Something went wrong on the server. The details are below: "
													+ "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a screenshot of this message and send it to <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a>.");

											},
									cache: false,
									contentType: false,
									processData: false
								 });
								}
							   });
}