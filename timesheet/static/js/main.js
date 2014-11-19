/* Global namespace for entire application */
var app = {};

// Main
(function() {
    $(document).ready(function() {
        $('#add-team-members').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true, calendarPos: 3});
        $('#timesheet-billable').dynamicForm({add: '#timesheet-billable-add-btn', del: '#timesheet-billable-del-btn', billableTotal: true});
        $('#timesheet-non-billable').dynamicForm({add: '#timesheet-non-billable-add-btn', del: '#timesheet-non-billable-del-btn', daysTotal: true});
        $('#financial-milestones').dynamicForm({add: '#add-milestone-btn', del: '#del-milestone-btn', calendar: true, calendarPos: 0, financialTotal: true});

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

            rowCountElement = $table.find('input[type="hidden"]:nth-of-type(1)'),
            rowCount = Number(rowCountElement.val());

        var add = function() {
            var lastRow = $($table).find('tr').last(),
                lastRowId = lastRow.find('td:first').children(':first').attr('id'),
                newRow,
                newRowId,
                $tds,
                $element,
                $curId,
                $curIdSel,
                $curChildEle,
                curChildId,
                $curChildEleInput,

            // Slice the id number from last row id
            lastRowId = getIdNo(lastRowId);
            lastRowId = Number(lastRowId);

            newRow = lastRow.clone();
            newRowId = lastRowId + 1;

            lastRow.after(newRow);

            $tds = newRow.find('td > :first-child');

            $tds.each(function(index) {
                $element = $(this);
                $curId = $element.attr('id');

                if($curId) {
                    $curId = $curId.replace(app.getIdNo($curId), newRowId);
                    $element.attr('id', $curId);
                    $element.attr('name', $curId);
                }

                if(index === 1 || index === 2) {
                    $element.val('');
                }

                if($($element).hasClass('input-field')) {
                    $element.val(0);
                }

                if(options.calendar) {
                    if(index === options.calendarPos) {
                        $curIdSel = $('#' + $curId);
                        $curChildEle = $element.find('div:nth-child(1n)');
                        $curChildEleInput = $curIdSel.find('input');

                        $curChildEle.attr('id', $curId);
                        $curChildEle.attr('name', $curId);
                        $curChildEleInput.attr('id', $curId);
                        $curChildEleInput.attr('name', $curId);

                        $curIdSel.datetimepicker({"pickTime": false, "language": "en-us", "format": "YYYY-MM-DD"});
                    }
                }
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
                    dItemsLen                   = dItems.length,
                    curDItem,
                    curDItemId,
                    i;


                for(i = 0; i < dItemsLen; i += 1) {
                    curDItem = dItems[i];
                    curDItemId = $(curDItem).attr('id');
                    curDItemId = curDItemId.replace(app.getIdNo(curDItemId), newRowId);

                    $(curDItem).attr('id', curDItemId);
                }

                newRowBQuestions.text('0');
                newRowBHours.text('0');
                newRowBQuestionsHidden.val('0');
                newRowBHoursHidden.val('0');
                newRowTotalQuestions.text('0');
                newRowTotalHours.text('0');
                newRowTotalQuestionsHidden.val('0');
                newRowTotalHoursHidden.val('0');
            }

            rowCount += 1;

            $(rowCountElement).attr('value', rowCount);

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

        var billableTotalFun = function() {
            if(options.billableTotal) {
                var $dayPopoverBtn = $table.find('.day-popover-button');
                var $bTask = $table.find('.b-task');

                var popoverCon = '<div class="mar-bot-5"><label class="sm-fw-label">Question</label> <input class="form-control small-input question-input" type="number" value="0"></div>';
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label">Hours</label> <input class="form-control small-input hours-input" type="number" value="0" max="24"></div>';

                $dayPopoverBtn.popover({
                    html: true,
                    placement: 'bottom',
                    content: popoverCon
                });

                $dayPopoverBtn.popover('hide');

                var primaryCb = function() {
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
            }
        };

        var financialTotalFun = function() {
            if(options.financialTotal) {
                $deliverables = $table.find('.milestone-item-deliverable');
                $amounts = $table.find('.milestone-item-amount');

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

                var amountTotal = function () {
                    var $amountsLen = $amounts.length,
                        $amountTotal = $table.parent().find('.milestone-total-amount'),
                        i,
                        $curItem,
                        temp = 0;

                    for (i = 0; i < $amountsLen; i += 1) {
                        $curItem = Number($($amounts[i]).val());
                        temp += $curItem;
                    }

                    $amountTotal.text(temp);
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

        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };

        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));




