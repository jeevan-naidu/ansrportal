//function to check for weekends pass the date with - seperator and yyyy-mm-dd format
$(document).ready(function() {
    function check_weekends(date) {
        var is_week = ""
        new_to_date = new_from_date = []
        new_to_date = date.split("-");
        var d_to_date = new Date(new_to_date[0], new_to_date[1] - 1, new_to_date[2]);
        var day_to_date = d_to_date.getDay();
        if (day_to_date == 0 || day_to_date == 6) {
            is_week = "weekend";
        } else {
            is_week = "weekdays"
        }
        return is_week
    }
    $('.input-group-addon').click(function() {
        $(this).parent().find('input').focus();
    });
    $('.date input').on('keypress', function(key) {
        if (key.charCode < 48 || key.charCode > 57) return false;
    });


    $('.userexit').on('click', function(key) {
        if ($('#id_last_date').val() != '' || $('#id_last_date').val != "") {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; //January is 0!
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd
            }
            if (mm < 10) {
                mm = '0' + mm
            }

            var from_date = document.getElementById("id_start_date").value;
            var to_date = document.getElementById("id_last_date").value;
            weekend_from = check_weekends(from_date);
            weekend_to_date = check_weekends(to_date);
            if (weekend_from == 'weekend' || weekend_to_date == 'weekend') {
                swal("You can't select Weekends as a date")
                document.getElementById("id_last_date").value = "";
                document.getElementById("id_start_date").value = "";
            }
            if (to_date) {
                if (from_date > to_date) {
                    swal("Last date should not be earlier than the exit date");
                    document.getElementById("id_last_date").value = "";
                }
            }
        }
    });
    // Code for Manager/HR screen
    $('.acceptance,.rehiremgr,.backup, .hrconcent, .hrrehire').on('click', function() {
        $(this).val(this.checked ? 'on' : '');
    });
    $('.datetimepicker').datetimepicker({
        "pickTime": false,
        "language": "en",
        "format": "YYYY-MM-DD"
    });
    $('.resignation_acceptance').on('click', function() {
        var start_date = $(this).parent().parent().find('.finaldate').attr('data-resign-date');
        var end_date = $(this).parent().parent().find('.finaldate').val();
        week_end_date = check_weekends(end_date)
        if (week_end_date == 'weekend') {
             swal("You can't select Weekends as a date")
             return false;
             }
        if (start_date > end_date) {
            swal(
                'Resignation date : ' + start_date,
                'Last date should not be earlier than the resignation date',
                'error'
            )
        } else {
            var url = window.location.href
            if (url.indexOf('exit-acceptance') !== -1) {
                manager_concent = $(this).parent().parent().find('.acceptance').val();
                mgr_feedback = $(this).parent().parent().find('.feedback').val();
                manager_rehire = $(this).parent().parent().find('.rehiremgr').val();
                mgr_backup = $(this).parent().parent().find('.backup').val();
                final_date = $(this).parent().parent().find('.finaldate').val();
                user_id = $(this).parent().parent().find('.userid').val();

                $.ajax({
                    url: "/exitapp/update-manager-value/",
                    type: "GET",
                    data: {
                        'final_date': final_date,
                        'mgr_backup': mgr_backup,
                        'id': user_id,
                        'manager_concent': manager_concent,
                        'mgr_feedback': mgr_feedback,
                        'manager_rehire': manager_rehire
                    },
                    success: function(json) {
                        if (json == 'success') {
                            swal("Completed!", "Employee data has been submitted.", "success");
                        }
                        if (json == 'failure') {
                           sweetAlert("Oops...", "Check the Dates you have Holidays or weekends", "error");
                        }
                    }
                });
            }
            var url = window.location.href
            if (url.indexOf('hr-acceptance') !== -1) {
                hr_concent = $(this).parent().parent().find('.hrconcent').val();
                hr_feedback = $(this).parent().parent().find('.feedbackhr').val();
                hr_rehire = $(this).parent().parent().find('.hrrehire').val();
                final_date = $(this).parent().parent().find('.finaldate').val();
                week_end_date = check_weekends(final_date)
                if (week_end_date == 'weekend') {
                    swal("You can't select Weekends as a date")
                    return false;
                 }
                user_id = $(this).parent().parent().find('.userid').val();
                $.ajax({
                    url: "/exitapp/update-hr-value/",
                    type: "GET",
                    data: {
                        'final_date': final_date,
                        'hr_concent': hr_concent,
                        'id': user_id,
                        'hr_feedback': hr_feedback,
                        'hr_rehire': hr_rehire
                    },
                    success: function(json) {
                        if (json == 'success') {
                            swal("Completed!", "Employee data has been submitted.", "success");
                        } if (json == 'failure') {
                           sweetAlert("Oops...", "Check the Dates you have Holidays or weekends", "error");
                        }
                    }
                });
            }
        }
    });
});