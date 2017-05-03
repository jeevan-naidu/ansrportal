$("input:checkbox").click(function(){
    var checkbox_id = this.id;
    var checkbox_detail = checkbox_id.split("_");
    var flag = {"approve":"reject", "reject":"approve"};
    var next_flag = flag[checkbox_detail[0]] + "_" + checkbox_detail[1];
    if($(this).attr("checked")){

        $(this).attr("checked", false);
        $("#" + next_flag + "").attr("checked", false);
    }
    else{

    $(this).attr("checked", true);
        $("#" + next_flag + "").attr("checked", false);
    }
});
$(".submit").on("click", function(){
                            var idSelect = function(){ return this.id;};
                            var checkedBoxId = $(":checkbox:checked").map(idSelect).get();
                            var approve_list = [];
                            var reject_list = [];
                            for(var i=0; i<checkedBoxId.length; i++){
                             var checkbox_detail = checkedBoxId[i].split("_")
                             if(checkbox_detail[0] == "approve"){
                                approve_list.push(checkbox_detail[1]);
                             }else{
                             reject_list.push(checkbox_detail[1])
                             }
                            }
                            swal({   title: "Are you sure?",
							text: "Do you want to submit your approval?",
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
                                                url:"{% url 'new_created_project_approval' %}",
                                                data:{"approve": approve_list, "reject": reject_list},
                                                type:"post",
                                                success: function(data){
                                                    window.location=window.location;
                                                },

                                            });
                                            }
							   });
						 return false;
					 });


    $(".detail").click(function(){
        var project_id = this.id
        $.ajax({
            url:"{% url 'projectdetail' %}",
            data: {"id": project_id},
            type: "get",
            success: function(data){
            $("#modal_body").html(data);
            },
        });
    });