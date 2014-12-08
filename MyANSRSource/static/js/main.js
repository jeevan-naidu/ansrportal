/* Global namespace for entire application */
var app = app || {};

// Main
(function() {
    $(document).ready(function() {
        // Project
        $('#add-team-members').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true, calendarPos: 3, calendarPos2: 8, addTeamMember: true});

        $('#financial-milestones').dynamicForm({add: '#add-milestone-btn', del: '#del-milestone-btn', calendar: true, calendarPos: 0, financialTotal: true});

        // TimeSheet
        $('#timesheet-billable').dynamicForm({add: '#timesheet-billable-add-btn', del: '#timesheet-billable-del-btn', billableTotal: true});
        $('#timesheet-non-billable').dynamicForm({add: '#timesheet-non-billable-add-btn', del: '#timesheet-non-billable-del-btn', daysTotal: true, nonBillable: true});

        var contigencyEffortEle = $('.contigency-effort-input');

        if(contigencyEffortEle.length > 0) {
            localStorage.contigencyEffort = contigencyEffortEle.val();
        }

        contigencyEffortEle.on('keyup', function() {
            localStorage.contigencyEffort = $(this).val();
        });

    });
}());



app.getIdNo = function(str) {
    return str.match(/\d+/)[0];
};

// Form control plugin
(function() {
    $.fn.dynamicForm = function(options) {
        var $table = $(this),
            $addBtn = $(options.add),
            $delBtn = $(options.del),
            $rows   = $table.find('tr'),

            rowCountElement = $table.find('input[type="hidden"]:first'),
            rowCount = Number(rowCountElement.val());

            if(options.addTeamMember || options.financialTotal) {
                rowCountElement = $table.parent().find('input[type="hidden"]:nth-of-type(3)');
                rowCount = Number(rowCountElement.val());
            }

        var add = function() {
            var lastRow = $($table).find('tr').last(),
                lastRowId = lastRow.find('td:first').children(':first').attr('id'),
                newRow,
                newRowId,
                $formFields,
                $element,
                curId,
                curName,
                $curIdSel,

            // Slice the id number from last row id
            lastRowId = getIdNo(lastRowId);
            lastRowId = Number(lastRowId);

	    newRow = lastRow.clone();
            newRowId = lastRowId + 1;

	    screenName = newRow.find('td:first').children(':first').attr('id');
	    if (screenName.search("Milestones") >= 0) {
		    if (newRow.find('td:first').children(':first').children(':first').attr('readonly')) {
			newRow.find('td:nth-child(1)').children(':first').children(':first').attr('readonly',false)
			newRow.find('td:nth-child(2)').children(':first').attr('readonly',false)
			newRow.find('td:nth-child(3)').children(':first').attr('readonly',false)
			newRow.find('td:nth-child(4)').children(':first').attr('readonly',false)
		    }
	    }
	    else {
		    if (newRow.find('td:first').children(':first').attr('readonly')) {
			newRow.find('td:nth-child(1)').children(':first').attr('readonly',false)
			newRow.find('td:nth-child(2)').children(':first').attr('readonly',false)
			newRow.find('td:nth-child(3)').children(':first').children(':first').attr('readonly', false)
			newRow.find('td:nth-child(4)').children(':first').children(':first').attr('readonly', false)
			newRow.find('td:nth-child(5)').children(':first').attr('readonly',false)
		    }
	    }

	    newRow.find('input[type="hidden"]:last').val(0)
            
	    lastRow.after(newRow);

            $formFields = newRow.find('select, input, div, span');

            rowCount += 1;

            $(rowCountElement).attr('value', rowCount);

            // Increment the id and name value
            $formFields.each(function(index) {
                $element = $(this);
                curId = $element.attr('id');
                curName = $element.attr('name');

                if(curId) {
                    curId = curId.replace(app.getIdNo(curId), newRowId);
                    $element.attr('id', curId);
                }

                if(curName) {
                    curName = curName.replace(app.getIdNo(curName), newRowId);
                    $element.attr('name', curName);
                }

                if(!options.billableTotal || !options.nonBillable) {
                    if(index === 1 || index === 2) {
                        $element.val('');
                    }


                }

                if(options.billableTotal || options.nonBillable) {
                    if(index === 0) {
                        $element.val('0');
                    }


                    var rowCountInitialElement      = $table.find('input[type="hidden"]:eq(1)');
                    $(rowCountInitialElement).attr('value', rowCount);

                }

                if(options.calendar) {
                    if(index === options.calendarPos || index === options.calendarPos2) {
			if (curId.indexOf("id_Change Team Members-") >= 0) {
				curId = curId.replace(/\s+/g, '_') + '_pickers';
			}
			$curIdSel = $('#' + curId);
                        $curIdSel.datetimepicker({"pickTime": false, "language": "en-us", "format": "YYYY-MM-DD"});
                    }
                }



                console.log('index: ' + index + ' - ' + curId);  // Check the index value of the elements
            });

            if(options.billableTotal) {
                var newRowBQuestions            = newRow.find('.b-questions'),
                    newRowBHours                = newRow.find('.b-hours'),
                    newRowBQuestionsHidden      = newRow.find('.b-questions-hidden'),
                    newRowBHoursHidden          = newRow.find('.b-hours-hidden'),
                    newRowTotalQuestions        = newRow.find('.t-questions'),
                    newRowTotalHours            = newRow.find('.t-hours'),
                    newRowTotalQuestionsHidden  = newRow.find('.t-questions-hidden'),
                    newRowTotalHoursHidden      = newRow.find('.t-hours-hidden'),
                    dItems                      = newRow.find('.d-item'),
                    dItemsLen                   = dItems.length;

                newRowBQuestions.text('0');
                newRowBHours.text('0');
                newRowBQuestionsHidden.val('0');
                newRowBHoursHidden.val('0');
                newRowTotalQuestions.text('0');
                newRowTotalHours.text('0');
                newRowTotalQuestionsHidden.val('0');
                newRowTotalHoursHidden.val('0');
            }

            daysTotalFun();
            billableTotalFun();
            financialTotalFun();
        };

        var del = function() {
            var rows = $table.find('tr'),
                curRowCheckbox,
                isDelete,
                curr;

            rows.each(function() {
                curr = $(this);
                curRowCheckbox = curr.find('td:last-child > :first-child');

                isDelete = curRowCheckbox.is(':checked');

                if(isDelete) {
                    curRowCheckbox.closest('tr').remove();

                    rowCount -= 1;
                }
            });

            $(rowCountElement).attr('value', rowCount);

        };

        var daysTotalFun = function() {
            if(options.daysTotal) {
                var $days = $table.find('.days');

                var totalDays = function () {
                    var $curEle = $(this),
                        $curRow = $curEle.closest('tr'),
                        $curDays = $curRow.find('.days'),
                        $curDaysLen = $curDays.length,
                        $curTotal = $curRow.find('.total'),
                        $curEleVal = $curEle.val(),
                        $curEleVal = Number($curEleVal),
                        $totalNonBillableHours = $('.total-non-billable-hours'),
                        i,
                        $curDay,
                        temp = 0,
                        $rows = $table.find('tr'),
                        $totalList = $rows.find('.r-total'),
                        totalListLen = $totalList.length,
                        curTotalNonBillable,
                        tempTotalNonBillable = 0,
                        totalNonBillable;

                    for (i = 0; i < $curDaysLen; i += 1) {
                        $curDay = Number($($curDays[i]).val());
                        temp += $curDay;
                    }

                    var nonBillableTotalFun = function() {
                        for(i = 0; i < totalListLen; i += 1) {
                            curTotalNonBillable = Number($($totalList[i]).val());

                            tempTotalNonBillable +=  curTotalNonBillable;
                        }

                        totalNonBillable = tempTotalNonBillable;

                        $totalNonBillableHours.text(totalNonBillable);
                    };



                    $curTotal.val(temp);

                    nonBillableTotalFun();
                };

                $days.on({
                    keyup: totalDays,
                    click: totalDays
                });
            }
        };

        var plannedEffortFun = function() {
            if(options.plannedEffortCalc) {
                // variables
                var rowsLen = $rows.length,
                    item,
                    starDateItem,
                    endDateItem,
                    plannedEffortItem,
                    $plannedEffortItems = $('.pro-planned-effort'),
                    $plannedEffortItemsLen = $plannedEffortItems.length;


                var calcEffort = function($startDate, $endDate, $plannedEffort) {
                    // get value and formatting
                    var startDateVal = $startDate.val();
                    var startDate = startDateVal.split('-');
                    var startDateLen = startDate.length;

                    var endDateVal = $endDate.val();
                    var endDate = endDateVal.split('-');
                    var endDateLen = endDate.length;

                    // Type cast
                    for(i = 0; i < startDateLen; i += 1) {
                        startDate[i] = Number(startDate[i]);
                    }

                    for(i = 0; i < endDateLen; i += 1) {
                        endDate[i] = Number(endDate[i]);
                    }

                    startDate = startDate.join();
                    endDate = endDate.join();

                    // Create Date Object
                    startDate = new Date(startDate);
                    endDate = new Date(endDate);

                    // Calculate planned effort
                    var plannedEffort = app.workingDaysBetweenDates(startDate, endDate);

                    var totalEffort = plannedEffort * 8 * (plannedEffort / 100);

                    $plannedEffort.val(plannedEffort);

                    return true;
                };



                // Calculation for each row
                $rows.each(function(index) {

                    if(index > 0) {
                        item = $(this);
                        starDateItem = item.find('.pro-start-date');
                        endDateItem = item.find('.pro-end-date');
                        plannedEffortItem = item.find('.pro-planned-effort');

                        calcEffort(starDateItem, endDateItem, plannedEffortItem);
                    }
                });

                
            }
        };

        var billableTotalFun = function() {
            if(options.billableTotal) {
                var $dayPopoverBtn = $table.find('.day-popover-button');
                var $bTask = $table.find('.b-task'),
                    $rowTotalView = $('.row-total-view');

                var popoverCon = '<div class="mar-bot-5"><label class="sm-fw-label">Question</label> <input class="form-control small-input question-input" type="number" value="0"></div>';
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label">Hours</label> <input class="form-control small-input hours-input" type="number" value="0" max="24"></div>';

                $dayPopoverBtn.popover({
                    trigger: 'click',
                    html: true,
                    placement: 'bottom',
                    content: popoverCon
                });


               var primaryCb = function(e) {
                   e.preventDefault();
                   e.stopPropagation();

                    var $curDayBtn              = $(this),
                        $curRow                 = $curDayBtn.closest('tr'),
                        $curRowQuestions        = $curRow.find('.b-questions'),
                        $curRowHours            = $curRow.find('.b-hours'),
                        $totalQuestions         = $curRow.find('.t-questions'),
                        $totalHours             = $curRow.find('.t-hours'),
                        $totalQuestionsHidden   = $curRow.find('.t-questions-hidden'),
                        $totalHoursHidden       = $curRow.find('.t-hours-hidden'),
                        curRowQuestionsLen      = $curRowQuestions.length,
                        $curQuestionsView       = $curDayBtn.find('.b-questions'),
                        $curHoursView           = $curDayBtn.find('.b-hours'),
                        $curQuestionsHidden     = $curDayBtn.find('.b-questions-hidden'),
                        $curHoursHidden         = $curDayBtn.find('.b-hours-hidden'),
                        $curQuestionsInput      = $curDayBtn.next().find('.question-input'),
                        $curHoursInput          = $curDayBtn.next().find('.hours-input'),
                        curQuestionsViewText    = $curQuestionsView.text(),
                        curHoursViewText        = $curHoursView.text(),
                        $totalBillableHours     = $('.total-billable-hours'),
                        $totalIdleHours         = $('.total-idle-hours');


                    var viewToInput = function() {
                        $($curQuestionsInput).val(curQuestionsViewText);
                        $($curHoursInput).val(curHoursViewText);
                    };

                    viewToInput();

                    var calculateTotal = function() {
                        var questionsTemp = 0,
                            hoursTemp = 0,
                            curQuestions,
                            curHours,
                            i,
                            curTaskVal = $curRow.find('.b-task option:selected').val(),
                            curTotalIdleHours          = 0,
                            curTotalBillableHours      = 0,
                            $curTotalIdleHoursHidden    = $curRow.find('.r-total-idle-hours'),
                            $curTotalBillableHoursHidden    = $curRow.find('.r-total-billable-hours');


                        if(curTaskVal === 'I') {
                            $curRow.removeClass('billable-row').addClass('idle-row');
                        } else {
                            $curRow.removeClass('idle-row').addClass('billable-row');
                        }

                        for(i = 0; i < curRowQuestionsLen; i += 1) {
                            curQuestions = Number($($curRowQuestions[i]).text());
                            curHours     = Number($($curRowHours[i]).text());

                            questionsTemp += curQuestions;
                            hoursTemp += curHours;

                            if(curTaskVal === 'I') {
                                curTotalIdleHours += curHours;
                            } else {
                                curTotalBillableHours += curHours;
                            }
                        }

                        $totalQuestions.text(questionsTemp);
                        $totalHours.text(hoursTemp);

                        $totalQuestionsHidden.val(questionsTemp);
                        $totalHoursHidden.val(hoursTemp);

                        // Idle and billable hours
                        $curTotalIdleHoursHidden.val(curTotalIdleHours);
                        $curTotalBillableHoursHidden.val(curTotalBillableHours);

                        var totalIdleAndBillableHours = function() {
                            var $rTotalIdleHoursList = $table.find('.r-total-idle-hours'),
                                $rTotalBillableHoursList = $table.find('.r-total-billable-hours'),
                                rTotalIdleHoursListLen = $rTotalIdleHoursList.length,
                                tempIdleTotal = 0,
                                tempBillableTotal = 0,
                                curIdleTotal,
                                curBillableTotal,
                                idleTotalHours,
                                billableTotalHours;


                            for(i = 0; i < rTotalIdleHoursListLen; i += 1) {
                                curIdleTotal = Number($($rTotalIdleHoursList[i]).val());
                                curBillableTotal = Number($($rTotalBillableHoursList[i]).val());

                                tempIdleTotal += curIdleTotal;
                                tempBillableTotal += curBillableTotal;
                            }

                            idleTotalHours = tempIdleTotal;
                            billableTotalHours = tempBillableTotal;

                            // To Dom
                            $totalBillableHours.text(billableTotalHours);
                            $totalIdleHours.text(idleTotalHours);
                        };

                        totalIdleAndBillableHours();
                    };

                    calculateTotal();

                    var inputToView = function() {
                        $curQuestionsView.text($curQuestionsInput.val());
                        $curHoursView.text($curHoursInput.val());

                        $curQuestionsHidden.val($curQuestionsInput.val());
                        $curHoursHidden.val($curHoursInput.val());

                        calculateTotal();
                    };

                    $curQuestionsInput.on({
                        keyup: inputToView,
                        click: inputToView
                    }, calculateTotal);

                    $curHoursInput.on({
                        keyup: inputToView,
                        click: inputToView
                    }, calculateTotal);
                };

                $dayPopoverBtn.on('shown.bs.popover', primaryCb);

                $bTask.on({
                    change: primaryCb
                });

                $dayPopoverBtn.on('show.bs.popover', function() {
                    var $popover = $('.popover');
                    $popover.popover('hide');
                });


                $dayPopoverBtn.on('keyup', function(e) {
                    if(e.keyCode === 9) {
                        $(this).trigger('click');
                    }
                });

                $rowTotalView.on('focus', function() {
                    console.log('rTotalView trigged');
                    var $popover = $('.popover');
                    $popover.popover('hide');
                });

            }
        };

        var financialTotalFun = function() {
            if(options.financialTotal) {
                var $deliverables = $table.find('.milestone-item-deliverable'),
                    $amounts = $table.find('.milestone-item-amount'),
                    $amountTotal = $table.parent().find('.milestone-total-amount'),
                    $datePickers = $('.date-picker'),
                    $links = $('#add-milestone-btn, #del-milestone-btn');

                    if($($datePickers[0]).prop('readonly') == true) {
                        $table.hide();

                        $links.each(function() {
                            $(this).attr('role', 'button');
                            $(this).attr('disabled', true);
                        });
                    }


                    var deliverableTotal = function () {
                    var $deliverablesLen = $deliverables.length,
                        $deliverableTotal = $table.parent().find('.milestone-total-deliverable'),
                        i,
                        $curItem,
                        temp = 0;

                    for (i = 0; i < $deliverablesLen; i += 1) {
                        $curItem = Number($($deliverables[i]).val());
                        temp += $curItem;
                    }

                    $deliverableTotal.text(temp);
                };

                // amount validation
                var amountValidatoinFun = function() {
                    if(Number(localStorage.contigencyEffort) > Number($amountTotal.text()) || Number(localStorage.contigencyEffort) < Number($amountTotal.text())) {
                        if(!($amountTotal.hasClass('t-danger'))) {
                            $amountTotal.addClass('t-danger');
                        }
                    } else {
                        if($amountTotal.hasClass('t-danger')) {
                            $amountTotal.removeClass('t-danger');
                        }
                    }
                };

                amountValidatoinFun();

                var amountTotal = function () {
                    var $amountsLen = $amounts.length,
                        i,
                        $curItem,
                        temp = 0;

                    for (i = 0; i < $amountsLen; i += 1) {
                        $curItem = Number($($amounts[i]).val());
                        temp += $curItem;
                    }

                    $amountTotal.text(temp);

                    amountValidatoinFun();
                };

                $deliverables.on({
                    keyup: deliverableTotal,
                    click: deliverableTotal
                });

                $amounts.on({
                    keyup: amountTotal,
                    click: amountTotal
                });
            }
        };

        daysTotalFun();
        billableTotalFun();
        financialTotalFun();
        plannedEffortFun();

        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };

        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));


app.workingDaysBetweenDates = function (startDate, endDate) {

    // Validate input
    if (endDate < startDate)
        return 0;

    // Calculate days between dates
    var millisecondsPerDay = 86400 * 1000; // Day in milliseconds
    startDate.setHours(0,0,0,1);  // Start just after midnight
    endDate.setHours(23,59,59,999);  // End just before midnight
    var diff = endDate - startDate;  // Milliseconds between datetime objects
    var days = Math.ceil(diff / millisecondsPerDay);

    // Subtract two weekend days for every week in between
    var weeks = Math.floor(days / 7);
    var days = days - (weeks * 2);

    // Handle special cases
    var startDay = startDate.getDay();
    var endDay = endDate.getDay();

    // Remove weekend not previously removed.
    if (startDay - endDay > 1)
        days = days - 2;

    // Remove start day if span starts on Sunday but ends before Saturday
    if (startDay == 0 && endDay != 6)
        days = days - 1

    // Remove end day if span ends on Saturday but starts after Sunday
    if (endDay == 6 && startDay != 0)
        days = days - 1

    return days;
};















