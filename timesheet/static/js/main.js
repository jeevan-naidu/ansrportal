/* Global namespace for entire application */
var app = {};

// Main
(function() {
    $(document).ready(function() {
        $('#createProject').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true});
        $('#timesheet-billable').dynamicForm({add: '#timesheet-billable-add-btn', del: '#timesheet-billable-del-btn', billableTotal: true});
        $('#timesheet-non-billable').dynamicForm({add: '#timesheet-non-billable-add-btn', del: '#timesheet-non-billable-del-btn', daysTotal: true});




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
                lastRowId = lastRow.find('td').first().find('select').attr('id'),
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
                //$curId = $curId.replace(app.getIdNo($curId), newRowId);

                //$element.attr('id', $curId);
                //$element.attr('name', $curId);

                if(index === 1 || index === 2) {
                    $element.val('');
                }

                if($($element).hasClass('input-field')) {
                    $element.val(0);
                }

                if(options.calendar) {
                    if(index === 3) {
                        $curIdSel = $('#' + $curId);
                        $curChildEle = $element.find('div:nth-child(1n)');
                        $curChildEleInput = $curIdSel.find('input');

                        console.log($curChildEleInput);
                        $curChildEle.attr('id', $curId);
                        $curChildEle.attr('name', $curId);
                        $curChildEleInput.attr('id', $curId);
                        $curChildEleInput.attr('name', $curId);

                        $curIdSel.datetimepicker({"pickTime": false, "language": "en-us", "format": "YYYY-MM-DD"});
                    }
                }
            });

            rowCount += 1;

            $(rowCountElement).attr('value', rowCount);

            daysTotalFun();
            billableTotalFun();
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
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label">Hours</label> <input class="form-control small-input hours-input" type="number" value="0"></div>';

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
                        curRowQuestionsLen      = $curRowQuestions.length,
                        $curQuestionsView       = $(this).find('.b-questions'),
                        $curHoursView           = $curDayBtn.find('.b-hours'),
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
                    };

                    var inputToView = function() {
                        $curQuestionsView.text($curQuestionsInput.val());
                        $curHoursView.text($curHoursInput.val());

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

        daysTotalFun();
        billableTotalFun();


        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };


        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));




