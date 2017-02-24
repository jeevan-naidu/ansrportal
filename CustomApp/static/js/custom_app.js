/**
 * Created by vivekpradhan on 15/2/17.
 */
    //ajax request for registering a leave on modal popup open
  $("#modal-container-process").on('shown.bs.modal', function(e) {
      button = e.relatedTarget;
      button_details = button.id.split("-")
      $.ajax({
         type: "GET",
          url: '/'+ button_details[0] + '/update/' + button_details[1] + "/",

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
