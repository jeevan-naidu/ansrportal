/* Global namespace for entire application */
var app = {};

// Main
(function() {
    $(document).ready(function() {
        $('#createProject').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true});
        $('#timesheet-billable').dynamicForm({add: '#timesheet-billable-add-btn', del: '#timesheet-billable-del-btn', daysTotal: true});
        $('#timesheet-non-billable').dynamicForm({add: '#timesheet-non-billable-add-btn', del: '#timesheet-non-billable-del-btn', daysTotal: true});

        var popoverCon = '<div class="mar-bot-5"><label class="sm-fw-label">Question</label> <input class="form-control small-input question-input" type="text" value="3"></div>';
            popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label">Hours</label> <input class="form-control small-input hours-input" type="text" value="7"></div>';

        $('.days').popover({
                html: true,
                placement: 'bottom',
                content: popoverCon
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
                $curId = $curId.replace(app.getIdNo($curId), newRowId);

                $element.attr('id', $curId);
                $element.attr('name', $curId);

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

        daysTotalFun();



        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };


        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));




