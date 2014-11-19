/* Global namespace for entire application */
var app = app || {};



// Main
(function() {
    $(document).ready(function() {
        $('#add-team-members').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true, calendarPos: 3});
        $('#timesheet-billable').dynamicForm({add: '#timesheet-billable-add-btn', del: '#timesheet-billable-del-btn', billableTotal: true});
        $('#timesheet-non-billable').dynamicForm({add: '#timesheet-non-billable-add-btn', del: '#timesheet-non-billable-del-btn', daysTotal: true});
        $('#financial-milestones').dynamicForm({add: '#add-milestone-btn', del: '#del-milestone-btn', calendar: true, calendarPos: 0, financialTotal: true});


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
                $curChildEleInput;

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
                        i,
                        $curDay,
                        temp = 0;

                    for (i = 0; i < $curDaysLen; i += 1) {
                        $curDay = Number($($curDays[i]).val());
                        temp += $curDay;
                    }

                    $curTotal.val(temp);
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
                        curHoursViewText        = $curHoursView.text();

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
                            i;

                        for(i = 0; i < curRowQuestionsLen; i += 1) {
                            curQuestions = Number($($curRowQuestions[i]).text());
                            curHours     = Number($($curRowHours[i]).text());

                            questionsTemp += curQuestions;
                            hoursTemp += curHours;
                        }

                        $totalQuestions.text(questionsTemp);
                        $totalHours.text(hoursTemp);

                        $totalQuestionsHidden.val(questionsTemp);
                        $totalHoursHidden.val(hoursTemp);
                    };

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

            }
        };

        var financialTotalFun = function() {
            if(options.financialTotal) {
                var $deliverables = $table.find('.milestone-item-deliverable'),
                    $amounts = $table.find('.milestone-item-amount'),
                    $amountTotal = $table.parent().find('.milestone-total-amount');

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

        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };


        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));




