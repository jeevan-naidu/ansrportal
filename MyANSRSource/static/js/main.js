/* Global namespace for entire application */
var app = app || {};
var helper = helper || {};

// Helper
helper.range = function(start, end) {
    var result = [];
    for (var i = start; i < end; i += 1) {
        result.push(i);
    }

    return result;
};

helper.forEach = function(arr, action) {
    var arrLen = arr.length,
        i;

    for (i = 0; i < arrLen; i += 1) {
        action(arr[i]);
    }
};

helper.sumOfArr = function(arr) {
    var sum = 0;

    helper.forEach(arr, function(item) {
        sum += item;
    });

    return sum.toFixed(2);
};

// argument element must be jQuery element
helper.getValOrText = function($ele) {
    var eleVal;
    if ($ele.prop('tagName') === 'SELECT' || $ele.prop('tagName') === 'INPUT') {
        eleVal = $ele.val();
    } else {
        eleVal = $ele.text();
    }
    return eleVal;
};

app.billableSetZeroList = [];

app.spaceToUnderscore = function($containerEle) {
    var items = $containerEle.find('td *'),
        item,
        itemId;

    items.each(function() {
        item = $(this);
        itemId = item.attr('id');

        if (itemId) {
            if (/\s/.test(itemId)) {
                itemId = itemId.replace(/\s+/g, '_');
                item.attr('id', itemId);
            }
        }
    });
};


app.getEffortCurRowId = function() {
    var calenderBtn = $('.date .input-group-addon');

    calenderBtn.on('click', function() {
        var item = $(this),
            prevElem = item.prev(),
            rowId = prevElem.attr('id');
        app.effortRowIdNo = Number(app.getIdNo(rowId)) + 1;
    });
};

app.calcCurRowChangeDate = function($tableEle) {
    var table = $tableEle,
        row = table.find('tr:eq(' + app.effortRowIdNo + ')'),
        starDateItem = row.find('.pro-start-date'),
        endDateItem = row.find('.pro-end-date'),
        plannedEffortItem = row.find('.pro-planned-effort'),
        plannedEffortPercentItem = row.find('.pro-planned-effort-percent'),
        plannedResult = app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem);


    plannedEffortItem.val(plannedResult.plannedEffort);
    //plannedEffortPercentItem.val(plannedResult.plannedEffortPercent);
};



app.getTaskChapter = function(selValue, currRow) {
    var total_val = currRow.find('.is_internal')
//    console.log(currRow.get(0).id)
    endDate = document.getElementsByName('enddate')[0].value;
    if (selValue) {
        $.ajax({
            url: '/myansrsource/gettask/' + selValue + '/',
            dataType: 'json',
            data: {
                endDate: endDate
            },
            success: function(data) {
                len = data.flag;

                data = data.data;

                var dataLen = data.length,
                    options = '',
                    $tasks = $('.b-task'),
                    i;

                for (i = 0; i < dataLen; i++) {
                    options += '<option value="' + data[i].id + '"' + 'data-task-type="' + data[i].taskType + '">' + data[i].name + '</option>';
                }
                for (j = 13; j > 6; j--) {
                    $(currRow[0].cells[j]).find('*').attr('disabled', false);
                    $(currRow[0].cells[j]).find("*").removeAttr("tabindex");
                }
                for (j = 13; j > 13 - len; j--) {


                    switch (j) {
                        case 13:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                        case 12:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");

                                break;
                            }
                        case 11:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                        case 10:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                        case 9:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                        case 8:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                        case 7:
                            {
                                $(currRow[0].cells[j]).find("*").attr("disabled", "disabled");
                                $(currRow[0].cells[j]).find("*").attr("tabindex", "-1");
                                break;
                            }
                    }

                }

                currRow.find(".b-task").html(options);

                app.setActive($tasks, app.timesheet.actTaskList);


            },

            error: function(data) {
                console.log('Error: ' + data);
                alert(data.responseText)
            }
        });

        $.ajax({
            url: '/myansrsource/getchapters/' + selValue + '/',
            dataType: 'json',
            success: function(data) {
                data = data.data;
                var dataLen = data.length,
                    options = '',
                    $chapters = $('.b-chapter'),
                    i;
                for (i = 0; i < dataLen; i++) {
                    options += '<option value="' + data[i].id + '">' + data[i].name + '</option>';
                }
                currRow.find(".b-chapter").html(options);

                app.setActive($chapters, app.timesheet.actChaptersList);

            },
            error: function(data) {
                console.log('Error: ' + data);
            }
        });
    } else {
        var options = '<option value>' + '-------' + '</option>';

        currRow.find(".b-task").html(options);
        currRow.find(".b-chapter").html(options);
    }
};

app.getActiveTaskChapter = function() {
    app.timesheet = {};
    var $tasks = $('.b-task'),
        $chapters = $('.b-chapter'),
        tasksLen = $tasks.length,
        task,
        chapter,
        taskVal,
        chapterVal,
        i;

    app.timesheet.actTaskList = [];
    app.timesheet.actChaptersList = [];

    for (i = 0; i < tasksLen; i += 1) {
        task = $($tasks[i]);
        chapter = $($chapters[i]);

        taskVal = task.val();
        chapterVal = chapter.val();

        app.timesheet.actTaskList.push(taskVal);
        app.timesheet.actChaptersList.push(chapterVal);
    }

    return false;
};

app.setActive = function($elements, arr) {
    var $elementsLen = $elements.length,
        $element,
        i;

    for (i = 0; i < $elementsLen; i += 1) {
        $element = $($elements[i]);
        if (arr[i]) {
            $element.find('option[value=' + arr[i] + ']').attr('selected', 'selected');
        }
    }
};//


//var is_internal_id = 0;
app.changeProject = function() {

    app.billableSelectProject.on('change', function(e) {

       var mondayH = this.id.split('-');
    $(this).blur();
//    if(this.value != ''){
          $.ajax({
                    url: '/myansrsource/get_internal',
                    dataType: 'json',
    //                async:false,
                    data: {
                        project_id: this.value
                    },

                    success: function(data) {

                        var is_internal_id = mondayH[0]+'-'+mondayH[1]+'-is_internal';
                        $('#'+is_internal_id).val(parseInt(data.is_internal));
                        mondayH = mondayH[0]+'-'+mondayH[1]+'-mondayH';
                        is_changed =true;
                        $('#'+mondayH).trigger('change');
//                            change: primaryCb ,

//                        console.log("mon trigger");
                        is_changed =false;
                    },
                    error: function(data) {
                        console.log('Error: ' + data);
                    }
                });
//    }
        var $this = $(this),
            $row = $this.closest('tr'),
            $projectUnitsElement = $row.find('.project-unit'),
            selectedValue = Number($this.val()),
            selectedProject;
        app.getTaskChapter(selectedValue, $row);

 var tmp_id = this.id.split('-');
    var tmp_is_internal_id = tmp_id[0]+'-'+tmp_id[1]+'-is_internal';
    $('#'+tmp_is_internal_id).data('prev_value', $('#'+tmp_is_internal_id).val());



        // get current project by id
        if (selectedValue != 0) {
            selectedProject = app.getById(app.projectsList, 'project__id', selectedValue);
            app.curProjectUnitShort = selectedProject.project__projectType__code;
            app.curProjectUnit = selectedProject.project__projectType__description;
            app.norms = selectedProject.project__maxProductivityUnits;

            $projectUnitsElement.text(app.curProjectUnitShort);
        }
   e.stopImmediatePropagation();
    return false; });

};

// Get particular object from array of object
app.getById = function(arr, propName, id) {
    for (var d = 0, len = arr.length; d < len; d += 1) {
        if (arr[d][propName] === id) {
            return arr[d];
        }
    }
};

app.firstTimeTotal = function() {
    function billableIdleTotal() {
        var bTask = $('.b-task'),
            $cRow,
            cRowItemsLen,
            cRowTask,
            cRowHours,
            cRowQuestions,
            $cRowTQuestions,
            $cRowTHours,
            $cRowBTQuestionsHidden,
            $cRowBTHoursHidden,
            $cRowITQuestionsHidden,
            $cRowITHoursHidden,
            cRowHoursArr,
            cRowQuestionsArr,
            i,
            cRowItemHour,
            cRowItemQuestion,
            $totalBillableHours = $('.total-billable-hours'),
            $totalIdleHours = $('.total-idle-hours'),

            cRowHourTotal = 0,
            cRowQuestionTotal = 0,

            cRowBillableHoursTotal = 0,
            cRowBillableQuestionTotal = 0,
            cRowIdleHoursTotal = 0,
            cRowIdleQuestionTotal = 0,

            billableHoursTotal = 0,
            billableQuestionTotal = 0,

            idleHoursTotal = 0,
            idleQuestionTotal = 0;

        var nonBillableTotalItems = $('#timesheet-non-billable .r-total'),
            cRowNonBillable,
            $nonBillableItemsHour,
            nonBillableItemHour,
            $cRowNonBillableTotal,
            cRowNonBillableTotal = 0,
            nonBillableTotal = 0,
            $nonBillableTotal = $('.total-non-billable-hours'),

            grandTotal = 0,
            $grandTotal = $('.timesheet-grand-total');
        helper.forEach(bTask, function(item) {
            cRowHourTotal = 0;
            cRowQuestionTotal = 0;

            $cRow = $(item).closest('tr');
            cRowTask = $cRow.find('.b-task option:selected').data('task-type');
            cRowHours = $cRow.find('.b-hours');
            cRowQuestions = $cRow.find('.b-questions');
            cRowItemsLen = cRowHours.length;
            $cRowTQuestions = $cRow.find('.t-questions');
            $cRowTHours = $cRow.find('.t-hours');
            $cRowBTHoursHidden = $cRow.find('.r-total-billable-hours');
            $cRowITHoursHidden = $cRow.find('.r-total-idle-hours');

            for (i = 0; i < cRowItemsLen; i += 1) {
                cRowItemHour = Number($(cRowHours[i]).val());


                cRowHourTotal += cRowItemHour;

            }
            // To Dom
            $cRowTHours.text(cRowHourTotal.toFixed(2));
            $cRowTQuestions.text(cRowQuestionTotal.toFixed(2));

            if (cRowTask === 'I') {
                idleHoursTotal += cRowHourTotal;
                idleQuestionTotal += cRowQuestionTotal;

                $cRowBTHoursHidden.val(0);
                $cRowITHoursHidden.val(cRowHourTotal);

            } else {
                billableHoursTotal += cRowHourTotal;
                billableQuestionTotal += cRowQuestionTotal;

                $cRowBTHoursHidden.val(cRowHourTotal);
                $cRowITHoursHidden.val(0);
            }
        });

        helper.forEach(nonBillableTotalItems, function(item) {
            cRowNonBillableTotal = 0;
            cRowNonBillable = $(item).closest('tr');
            $nonBillableItemsHour = cRowNonBillable.find('.Mon-t, .Tue-t, .Wed-t, .Thu-t, .Fri-t, .Sat-t, .Sun-t');
            $cRowNonBillableTotal = cRowNonBillable.find('.r-total');

            helper.forEach($nonBillableItemsHour, function(item) {
                nonBillableItemHour = Number($(item).val());

                cRowNonBillableTotal += nonBillableItemHour;
            });

            // To Dom
            $cRowNonBillableTotal.val(cRowNonBillableTotal.toFixed(2));

            nonBillableTotal += cRowNonBillableTotal;
        });
        total_leave_hours =  Number($('.total-leave-hours').text() ),
        grandTotal = billableHoursTotal + idleHoursTotal + nonBillableTotal+total_leave_hours;


        // To Dom
        $totalBillableHours.text(billableHoursTotal.toFixed(2));
        $totalIdleHours.text(idleHoursTotal.toFixed(2));
        $nonBillableTotal.text(nonBillableTotal.toFixed(2));
        $grandTotal.text(grandTotal.toFixed(2));

        app.timeSheetDayTotalHours();
    }

    billableIdleTotal();
};

// Main: IIEF for local scope
(function($) {
    function getTastChaptersEachProject() {
        var billableSelectProject = $('.billable-select-project'),
            billableSelectProjectLen = billableSelectProject.length,
            $item,
            selValue,
            $task,
            $chapter,
            $row,
            i;

        for (i = 0; i < billableSelectProjectLen; i += 1) {
            $item = $(billableSelectProject[i]);
            selValue = $item.val();
            $row = $item.closest('tr');

            app.getTaskChapter(selValue, $row);
        }
    };




    app.timeSheetGrandTotal = function() {
        var billableTotal = Number($('.total-billable-hours').text()),
            idleTotal = Number($('.total-idle-hours').text()),
            notBillableTotal = Number($('.total-non-billable-hours').text()),
            total_leave_hours =  Number($('.total-leave-hours').text() ),
            $total = $('.timesheet-grand-total'),
            total = billableTotal + idleTotal + notBillableTotal + total_leave_hours ;


        $total.text((total).toFixed(2));
//        console.log("total_leave_hours"+total_leave_hours+"total"+total);
        return total;
    };


    app.timeSheetDayTotalHours = function() {
        var $mon = $('.Mon-t'),
            $tue = $('.Tue-t'),
            $wed = $('.Wed-t'),
            $thu = $('.Thu-t'),
            $fri = $('.Fri-t'),
            $sat = $('.Sat-t'),
            $sun = $('.Sun-t'),
            $monTotal = $('.ts-mon-total-hr'),
            $tueTotal = $('.ts-tue-total-hr'),
            $wedTotal = $('.ts-wed-total-hr'),
            $thuTotal = $('.ts-thu-total-hr'),
            $friTotal = $('.ts-fri-total-hr'),
            $satTotal = $('.ts-sat-total-hr'),
            $sunTotal = $('.ts-sun-total-hr');

        function total($arr, $output) {
            var tempArr = [],
                tempTotal = 0;

            helper.forEach($arr, function(item) {
                var curVal = helper.getValOrText($(item));
                tempArr.push(Number(curVal));
            });

            tempTotal = helper.sumOfArr(tempArr);

            $output.text(tempTotal);
        }

        total($mon, $monTotal);
        total($tue, $tueTotal);
        total($wed, $wedTotal);
        total($thu, $thuTotal);
        total($fri, $friTotal);
        total($sat, $satTotal);
        total($sun, $sunTotal);


    };

    app.tsInputIsValid = function($elem, str) {
        if (!str) {
            console.log('Please enter the valid number');
            $elem.addClass('alert-danger');
            return false;
        } else {
            // check for decimal
            str = Number(str);
            if (str < 0) {
                console.log('Please enter the positive number');
                $elem.addClass('alert-danger');
                return false;
            }
            if (/\./.test(str)) {
                if (!(/\b\.\d\d?\b/.test(str))) {
                    console.log('Only two decimal is allowed');
                    $elem.addClass('alert-danger');
                    return false;
                }
            }

            $elem.removeClass('alert-danger');
            return true;
        }
    };


    app.init = function() {
        app.getActiveTaskChapter();
        getTastChaptersEachProject();

    };

    $(document).ajaxStop(function() {
        app.firstTimeTotal();
    });

    $(document).ready(function() {
        app.init();
        var $popover = $('.popover');
        app.norms = '0.0 / Day';
        // Manage project
        var $changeTeamMembers = $('#change-team-members');
        if ($changeTeamMembers.length > 0) {
            app.spaceToUnderscore($changeTeamMembers);

            $changeTeamMembers.dynamicForm({
                add: '#addForm',
                del: '#delete-member',
                calendar: true,
                plannedEffortCalc: true,
                changeTeamMember: true,
                setEditableAll: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: [23],
                    setEmptyList: null
                },
                setEnableList: [24]
            });
        }

        var $manageMilestone = $('#manage-milestones');
        if ($manageMilestone.length > 0) {
            app.spaceToUnderscore($manageMilestone);

            $manageMilestone.dynamicForm({
                add: '#add-milestone-btn',
                del: '#delete-member',
                calendar: true,
                changeMilestone: true,
                isAmountTotal: true,
                setEditableAll: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: [6, 9],
                    setEmptyList: [5]
                },
                setEnableList: [0, 1, 4, 5, 6, 7, 8, 10]
            });
        }

        // Project
        var addTeamMembers = $('#add-team-members');
        if (addTeamMembers.length > 0) {
            app.spaceToUnderscore(addTeamMembers);
            addTeamMembers.dynamicForm({
                add: '#addForm',
                del: '#delete-member',
                calendar: true,
                calendarPosList: [11, 16],
                addTeamMember: true,
                plannedEffortCalc: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: null,
                    setEmptyList: null
                }
            });


            var $addTeamRows = addTeamMembers.find('tr'),
                item,
                starDateItem,
                endDateItem,
                plannedEffortItem,
                plannedEffortPercentItem,
                row,
                holiday,
                holidayDay,
                totalHolidayLen = window.holidays.data.length;
            app.holidaysList = [];


            app.proPlannedEffortPercentItems = $('.pro-planned-effort-percent, .pro-planned-effort');

            helper.clearArray(app.holidaysList);

            for (var i = 0; i < totalHolidayLen; i += 1) {
                holiday = new Date(window.holidays.data[i].date);
                holidayDay = holiday.getDay();

                if (holidayDay !== 0 && holidayDay !== 6) {
                    app.holidaysList.push(holiday);
                }
            }

            // Calculate effort for each row
            $addTeamRows.each(function(index) {
                if (index > 0) {
                    item = $(this);
                    starDateItem = item.find('.pro-start-date');
                    endDateItem = item.find('.pro-end-date');
                    plannedEffortItem = item.find('.pro-planned-effort'),
                        plannedEffortPercentItem = item.find('.pro-planned-effort-percent');

                    plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
                }
            });

            // Calculate PlannedEffort when change effort
            app.calcPlannedEffortCurRow = function(e) {
                item = $(this);
                row = item.closest('tr');
                starDateItem = row.find('.pro-start-date');
                endDateItem = row.find('.pro-end-date');
                plannedEffortItem = row.find('.pro-planned-effort');
                plannedEffortPercentItem = row.find('.pro-planned-effort-percent');

                if (item.hasClass('pro-planned-effort-percent')) {
                    plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
                }

                if (item.hasClass('pro-planned-effort')) {
                    plannedEffortPercentItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem, 'percent').plannedEffortPercent);
                }
            };

            app.proPlannedEffortPercentItems.on({
                'keyup': app.calcPlannedEffortCurRow,
                'click': app.calcPlannedEffortCurRow
            });

            app.getEffortCurRowId();

            $('.date').on('change', app.calcCurRowChangeDate);

        }

        var financialMilestones = $('#financial-milestones');
        if (financialMilestones.length > 0) {
            app.spaceToUnderscore(financialMilestones);
            financialMilestones.dynamicForm({
                add: '#add-milestone-btn',
                del: '#del-milestone-btn',
                calendar: true,
                calendarPosList: [0],
                isAmountTotal: true,
                isFinancialMilestone: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: [6, 9],
                    setEmptyList: [5]
                },
                setEnableList: [0, 1, 4, 5, 6, 7, 8, 10]
            });
        }

        // TimeSheet
        var timesheetBillable = $('#timesheet-billable');
        try {
            var strtDate = document.getElementsByName('startdate')[0].value;
        } catch (error) {

        }
        if (timesheetBillable.length > 0) {
            timesheetBillable.dynamicForm({
                add: '#timesheet-billable-add-btn',
                del: '#timesheet-billable-del-btn',
                billableTotal: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: app.billableSetZeroList,
                    setEmptyList: null
                }
            });
            $.ajax({
                url: '/myansrsource/getprojecttype',
                dataType: 'json',
                data: {
                    strtDate: strtDate
                },
                success: function(data) {
                    app.projectsList = data.data;
                },
                error: function(data) {
                    console.log('Error: ' + data);
                }
            });

            app.billableSelectProject = $('.billable-select-project');
            app.changeProject();
        }

        var timesheetNonBillable = $('#timesheet-non-billable');
        if (timesheetNonBillable.length > 0) {
            timesheetNonBillable.dynamicForm({
                add: '#timesheet-non-billable-add-btn',
                del: '#timesheet-non-billable-del-btn',
                daysTotal: true,
                nonBillable: true,
                defaultValues: { // When add row, set the elements default values
                    setZeroList: [0, 2, 3, 4, 5, 6, 7, 8, 9],
                    setEmptyList: null
                }
            });
        }

        var contigencyEffortEle = $('.contigency-effort-input');

        if (contigencyEffortEle.length > 0) {
            localStorage.contigencyEffort = contigencyEffortEle.val();
        }

        contigencyEffortEle.on('keyup', function() {
            localStorage.contigencyEffort = $(this).val();
        });
    });
})(jQuery);



app.getIdNo = function(str) {
    return str.match(/\d+/)[0];
};

// For elements sum of values to output (jQuery based)
app.getSum = function($elements, $outputElement) {
    var elementsLen = $elements.length,
        $item,
        itemVal,
        total = 0,
        i;

    for (i = 0; i < elementsLen; i += 1) {
        $item = $($elements[i]);
        itemVal = $item.val();
        total += itemVal;
    }

    $outputElement.text(total);
};

// Form control plugin
;
(function() {
    $.fn.dynamicForm = function(options) {
        var $table = $(this),
            $addBtn = $(options.add),
            $delBtn = $(options.del),
            $rows = $table.find('tr'),

            rowCountElement = $table.find('input[type="hidden"]:first'),
            rowCount = Number(rowCountElement.val());

        if (options.addTeamMember || options.changeTeamMember) {
            rowCountElement = $table.parent().parent().find('input[type="hidden"]:nth-of-type(3), input[type="hidden"]:nth-of-type(4)');
            rowCount = Number(rowCountElement.val());
        }

        if (options.isFinancialMilestone) {
            rowCountElement = $table.parent().parent().parent().find('input[type="hidden"]:nth-of-type(3)');
            rowCount = Number(rowCountElement.val());
        }

        if (options.changeMilestone) {
            rowCountElement = $table.parent().parent().parent().find('input[type="hidden"]:nth-of-type(3)');
            rowCount = Number(rowCountElement.val());
        }



        var add = function() {
            var lastRow = $($table).find('tr').last(),
                lastRowId = lastRow.find('td:first').children(':first').attr('id'),
                newRow,
                newRowId,
                $formFields,
                formFieldsLen,
                $element,
                curId,
                curName,
                $curIdSel,
                $popover = $('.popover');

            if ($popover.length > 0) {
                $popover.hide();
            }


            // Slice the id number from last row id
            lastRowId = app.getIdNo(lastRowId);
            lastRowId = Number(lastRowId);

            newRow = lastRow.clone();
            newRowId = lastRowId + 1;

            lastRow.after(newRow);

            $formFields = newRow.find('select, input, div, span');
            formFieldsLen = $formFields.length;
            rowCount += 1;

            if (options.billableTotal || options.nonBillable) {
                var disableElms = newRow.find('.ansr-disabled'),
                    disableElms2 = newRow.find('.disabled');

                if (disableElms.length > 0) {
                    disableElms.removeClass('ansr-disabled');
                }

                if (disableElms2.length > 0) {
                    disableElms2.removeClass('disabled');
                }
            }

            $(rowCountElement).attr('value', rowCount);

            // Increment the id and name value
            $formFields.each(function(index) {
                $element = $(this);
                curId = $element.attr('id');
                curName = $element.attr('name');

                if (curId) {
                    curId = curId.replace(app.getIdNo(curId), newRowId);
                    $element.attr('id', curId);
                }

                if (curName) {
                    curName = curName.replace(app.getIdNo(curName), newRowId);
                    $element.attr('name', curName);
                }

                if (options.billableTotal || options.nonBillable) {
                    var rowCountInitialElement = $table.find('input[type="hidden"]:eq(1)');
                    $(rowCountInitialElement).attr('value', rowCount);
                }

                if (options.defaultValues.setZeroList) {
                    if (options.defaultValues.setZeroList.indexOf(index) !== -1) {
                        // For project unit not set zero
                        if (!$element.hasClass('project-unit')) {
                            if ($element.prop('tagName') === 'INPUT' || $element.prop('tagName') === 'SELECT') {
                                $element.val('0');
                            } else {
                                $element.text('0');
                           }
                        }

                    }

                    //console.log(index + ': set zero');
                }

                if (options.defaultValues.setEmptyList) {
                    if (options.defaultValues.setEmptyList.indexOf(index) !== -1) {
                        $element.val('');
                        //console.log(index + ': set empty');
                    }
                }

                if (options.setEnableList) {
                    if (options.setEnableList.indexOf(index) !== -1) {
                        $element.prop('disabled', false);
                        //console.log(index + ': setEnableList');
                    }
                }

                if (options.setEditable) {
                    if (options.setEditable.indexOf(index) !== -1) {
                        $element.prop('readonly', false);
                        //console.log(index + ': setEditable');
                    }
                }

                if (options.setEditableAll) {
                    $element.removeAttr('readonly');
                }

                if (options.calendar) {
                    if (curId) {
                        if (curId.match('Date_pickers')) {
                            $curIdSel = $('#' + curId);
                            $curIdSel.datetimepicker({
                                "pickTime": false,
                                "language": "en-us",
                                "format": "YYYY-MM-DD"
                            }).on('change', function() {
                                app.calcCurRowChangeDate($table);
                            });
                        }
                    }
                }

                if (options.addTeamMember || options.changeTeamMember) {
                    if ((formFieldsLen - 1) === index) {
                        $element.prop('disabled', false);
                    }
                    // For team member autocomplete
                    if ($element.hasClass('autocomplete-light-widget') && $element.attr('data-widget-bootstrap') == 'normal') {
                        var $remove = $element.find('.remove');
                        if ($remove.css('display') === 'none') {
                            $element.yourlabsWidget().input.bind('selectChoice', function(e, choice, autocomplete) {
                                var $this = $(this);
                                $this.getMemberHolidayList();
                            });
                        } else {
                            $element.yourlabsWidget().input.bind('selectChoice', function(e, choice, autocomplete) {
                                var $this = $(this);
                                $this.getMemberHolidayList();
                            });
                            $remove.trigger('click');
                        }

                    }
                }


                if (options.plannedEffortCalc) {
                    if ($element.hasClass('pro-planned-effort-percent')) {
                        $element.val(100);
                    }
                }

                if (options.billableTotal) {
                    app.rowChapter = $('#id_form-' + newRowId + '-chapter');
                    if ($element.hasClass('billable-select-project')) {
                        app.rowProject = $element;
                    }
                }



                if ($element.hasClass('set-empty')) {
                    var elementType = $element.prop('tagName');
                    if (elementType === 'SELECT' || elementType === 'INPUT') {
                        $element.val('');
                    } else {
                        $element.text('');
                    }
                }

                if ($element.hasClass('set-zero')) {
                    var elementType2 = $element.prop('tagName');
                    if (elementType2 === 'SELECT' ){
                        $element.attr('value', 0);
                    }
                    else if( elementType2 === 'INPUT') {
                            if(!$element.hasClass('is_internal'))
                                $($element).val(0);
                            else  {
                                $($element).val(1);
                                $($element).data('prev_value',1);
                            }
                    }
                    else {
                        $element.text('0');
                    }
                }

                if ($element.hasClass('remove-sel-options')) {
                    var elementType3 = $element.prop('tagName');
                    if (elementType3 === 'SELECT') {
                        $element.find('option')
                            .remove()
                            .end()
                            .append('<option value>-----</option>');
//                        console.log('index: ' + index + ' - ' + curId); // Check the index value of the elements
                    }
                }

                if ($element.hasClass('set-q')) {
                    var elementType4 = $element.prop('tagName');
                    if (elementType4 === 'SELECT' || elementType4 === 'INPUT') {
                        $element.attr('value', 'Q');
                    } else {
                        $element.text('Q');
                    }
                }


//                console.log('index: ' + index + ' - ' + curId); // Check the index value of the elements

            });


            daysTotalFun();
            billableTotalFun();
            amountTotalFun();

            if (options.plannedEffortCalc) {
                app.proPlannedEffortPercentItems = $('.pro-planned-effort-percent, .pro-planned-effort');

                app.proPlannedEffortPercentItems.on({
                    'keyup': app.calcPlannedEffortCurRow,
                    'click': app.calcPlannedEffortCurRow
                });

                app.getEffortCurRowId();

                // Calculate effort for new row
                var item = $($table).find('tr').last(),
                    starDateItem = item.find('.pro-start-date'),
                    endDateItem = item.find('.pro-end-date'),
                    plannedEffortItem = item.find('.pro-planned-effort'),
                    plannedEffortPercentItem = item.find('.pro-planned-effort-percent');

                plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
            }

            if (options.billableTotal) {
                app.billableSelectProject = $('.billable-select-project');
                app.changeProject();
                app.autoFillInit(app.rowProject, app.rowChapter);
            }
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

                if (isDelete) {
                    curRowCheckbox.closest('tr').remove();

                    rowCount -= 1;
                }
            });

            $(rowCountElement).attr('value', rowCount);

        };

        var daysTotalFun = function() {
            if (options.daysTotal) {
                var $days = $table.find('.days');

                var totalDays = function() {
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
                        for (i = 0; i < totalListLen; i += 1) {
                            curTotalNonBillable = Number($($totalList[i]).val());

                            tempTotalNonBillable += curTotalNonBillable;
                        }

                        totalNonBillable = tempTotalNonBillable.toFixed(2);

                        $totalNonBillableHours.text(totalNonBillable);
                    };

                    temp = temp.toFixed(2);
                    $curTotal.val(temp);

                    nonBillableTotalFun();
                    app.timeSheetGrandTotal();
                    app.timeSheetDayTotalHours();
                };

                $days.on({
                    keyup: totalDays,
                    click: totalDays
                });
            }
        };

        var billableTotalFun = function() {
//        console.log("billableTotalFun");
            if (options.billableTotal) {
                var $totalBillableHours = $('.total-billable-hours'),
                    $totalIdleHours = $('.total-idle-hours');


                var $dayPopoverBtn = $table.find('.day-popover-button');
                var $bTask = $table.find('.b-task'),
                    $rowTotalView = $('.row-total-view');

                var popoverCon = '<div class="mar-bot-5" style="display: none;><label class="sm-fw-label project-type-popup">Questions</label> <input class="form-control small-input question-input" type="number" value="0" min="0" step="0.01"></div>';
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label hours"></label> <input style="position: absolute;top: -44px;left: -39px;width: 82px;    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.25) inset;" class="form-control small-input hours-input" type="number" value="0" max="24" min="0" step="0.01"></div>';
                popoverCon += '<div class="mar-bot-5" style="display: none;><label class="sm-fw-label hours">Norm</label> <label class="small-input norm-input"></label></div>';

                $dayPopoverBtn.popover({
                    trigger: 'click',
                    html: true,
                    placement: 'bottom',
                    content: popoverCon
                });

                var primaryCb = function(e) {
                    e.preventDefault();
                    e.stopImmediatePropagation();

                    var $curDayBtn = $(this),
                        $curRow = $curDayBtn.closest('tr'),
                        $curRowQuestions = $curRow.find('.b-questions'),
                        $curRowHours = $curRow.find('.b-hours'),
                        $totalQuestions = $curRow.find('.t-questions'),
                        $totalHours = $curRow.find('.t-hours'),
                        $is_internal = $curRow.find('.is_internal'),
                        $totalQuestionsHidden = $curRow.find('.t-questions-hidden'),
                        $totalHoursHidden = $curRow.find('.t-hours-hidden'),
                        curRowQuestionsLen = $curRowHours.length,
                        $curQuestionsView = $curDayBtn.find('.b-questions'),
                        $curHoursView = $curDayBtn.find('.b-hours'),
                        $curQuestionsHidden = $curDayBtn.find('.b-questions-hidden'),
                        $curHoursHidden = $curDayBtn.find('.b-hours-hidden'),
                        $curQuestionsInput = $curDayBtn.next().find('.question-input'),
                        $curHoursInput = $curDayBtn.next().find('.hours-input'),
                        $curProjectUnit = $curDayBtn.find('.project-unit'),
                        $curProjectPopupUnit = $curDayBtn.next().find('.project-type-popup'),
                        $curProjectPopupNorm = $curDayBtn.next().find('.norm-input'),
                        curQuestionsViewText = $curQuestionsView.text(),
                        curHoursViewText = $curHoursView.text(),
                        curProjectUnit = $curProjectUnit.text(),
                        $curSelectProject = $curRow.find('.billable-select-project'),
                        selectedValue = Number($curSelectProject.val()),
                        selectedProject;
                    var viewToInput = function() {
                        $($curQuestionsInput).val(curQuestionsViewText);
                        $($curHoursInput).val(curHoursViewText);
                    };

                    var projectUnitViewToPopUp = function() {
                        // get current project by id
                        if (selectedValue != 0) {
                            selectedProject = app.getById(app.projectsList, 'project__id', selectedValue);

                            app.curProjectUnitShort = selectedProject.project__projectType__code;
                            app.curProjectUnit = selectedProject.project__projectType__description;
                            app.norms = selectedProject.project__maxProductivityUnits;

                            $curProjectPopupUnit.text(app.curProjectUnit);
                        } else {
                            app.norms = 0.0;
                        }

                        // Get project norms
                        if (app.norms > 0 && app.norms != undefined) {
                            $curProjectPopupNorm.text(app.norms + '  ' + app.curProjectUnitShort + '/DAY');
                        } else {
                            $curProjectPopupNorm.text('  ');
                        }
                    };

                    projectUnitViewToPopUp();

                    viewToInput();
                    var calculateTotal = function() {
                        var questionsTemp = 0,
                            hoursTemp = 0,
                            curQuestions,
                            curHours,
                            i,
                            curTaskType = $curRow.find('.b-task option:selected').data('task-type'),
                            curTotalIdleHours = 0,
                            curTotalBillableHours = 0,
                            $curTotalIdleHoursHidden = $curRow.find('.r-total-idle-hours'),
                            $curTotalBillableHoursHidden = $curRow.find('.r-total-billable-hours');


                        if (curTaskType === 'I') {
                            $curRow.removeClass('billable-row').addClass('idle-row');
                        } else {
                            $curRow.removeClass('idle-row').addClass('billable-row');
                        }
                        for (i = 0; i < curRowQuestionsLen; i += 1) {
                            curQuestions = Number($($curRowQuestions[i]).text());
                            curHours = Number($($curRowHours[i]).val());

                            questionsTemp += curQuestions;
                            hoursTemp += curHours;

                            if (curTaskType === 'I') {
                                curTotalIdleHours += curHours;
                            } else {
                                curTotalBillableHours += curHours;
                            }
                        }
                        var cur_$totalHours = parseFloat($totalHours.text());
                        var prev_value_is_internal = parseInt($($is_internal).data('prev_value'));
                        var cur_value_is_internal = parseInt($($is_internal).val());
//                        console.log("prev_value_is_internal"+prev_value_is_internal+'cur_value_is_internal'+cur_value_is_internal);
                        var calculated_total = parseFloat(hoursTemp);
                        var diff = Math.abs( parseFloat($totalHours.text())-(parseFloat(hoursTemp)))
                        diff = parseFloat(diff).toFixed(2);
                        var internal_total = parseFloat($('.total-internal-hours').text());
                        var external_total = parseFloat( $('.total-external-hours').text() );
                        if(is_changed === true) {
                            if (prev_value_is_internal > cur_value_is_internal) {
                            //console.log("1->0");
//                                console.log("internal_total  "+internal_total+"calculated_total  "+calculated_total+"  external_total  "+external_total+"  $totalHours  "+cur_$totalHours);
//                                console.log("total"+external_total+calculated_total);
                                    $('.total-internal-hours').text((internal_total-cur_$totalHours).toFixed(2));


                                $('.total-external-hours').text((parseFloat(external_total+calculated_total)).toFixed(2));
                            }
                            //external - > internal
                            else if (cur_value_is_internal > prev_value_is_internal) {
//                            console.log("0->1");
                                    $('.total-internal-hours').text(parseFloat(internal_total+calculated_total).toFixed(2));
                                    $('.total-external-hours').text(parseFloat(external_total-cur_$totalHours).toFixed(2));
                            }
                        }
                        else {
                            if(cur_value_is_internal ) {
//                                 console.log("1-1-1");
                                if(calculated_total > cur_$totalHours ) {
                                    var total_sum = parseFloat(internal_total)+ parseFloat(diff);
                                    $('.total-internal-hours').text(total_sum.toFixed(2))

                                }
                                else if (calculated_total < cur_$totalHours )  {
                                     var total_sum = parseFloat(internal_total) - parseFloat(diff);
                                     $('.total-internal-hours').text(total_sum.toFixed(2))
                                }

                            }

                            else if(!(cur_value_is_internal )) {
//                            console.log("0-0-0");
                                if(calculated_total > cur_$totalHours ) {
                                    var total_sum = parseFloat(external_total)+ parseFloat(diff);
                                    $('.total-external-hours').text(total_sum.toFixed(2))

                                }
                                else if (calculated_total < cur_$totalHours )  {
                                     var total_sum = parseFloat(external_total) - parseFloat(diff);
                                     $('.total-external-hours').text(total_sum.toFixed(2))
                                }

                            }
                        }
                        $totalQuestions.text(questionsTemp.toFixed(2));
                         $totalHours.text(hoursTemp.toFixed(2));
                        $totalQuestionsHidden.val(questionsTemp.toFixed(2));
                        $totalHoursHidden.val(hoursTemp.toFixed(2));

                        // Idle and billable hours
                        $curTotalIdleHoursHidden.val(curTotalIdleHours.toFixed(2));
                        $curTotalBillableHoursHidden.val(curTotalBillableHours.toFixed(2));

                        var totalIdleAndBillableHours = function() {
                            var $rTotalIdleHoursList = $table.find('.r-total-idle-hours'),
                                $rTotalBillableHoursList = $table.find('.r-total-billable-hours'),
                                rTotalIdleHoursListLen = $rTotalIdleHoursList.length,
                                rTotalBillableHoursListLen = $rTotalBillableHoursList.length,
                                tempIdleTotal = $rTotalIdleHoursList.text(),
                                tempBillableTotal = $rTotalBillableHoursList.text(),
                                curIdleTotal,
                                curBillableTotal,
                                idleTotalHours,
                                billableTotalHours;

                            // type cast
                            tempIdleTotal = Number(tempIdleTotal);
                            tempBillableTotal = Number(tempBillableTotal);

                            for (i = 0; i < rTotalIdleHoursListLen; i += 1) {
                                curIdleTotal = Number($($rTotalIdleHoursList[i]).val());
                                tempIdleTotal += curIdleTotal;
                            }

                            for (i = 0; i < rTotalBillableHoursListLen; i += 1) {
                                curBillableTotal = Number($($rTotalBillableHoursList[i]).val());
                                tempBillableTotal += curBillableTotal;
                            }

                            idleTotalHours = tempIdleTotal;
                            billableTotalHours = tempBillableTotal;

                            // To Dom
                            $totalBillableHours.text((billableTotalHours).toFixed(2));
                            $totalIdleHours.text((idleTotalHours).toFixed(2));

                            app.timeSheetGrandTotal();
                            app.timeSheetDayTotalHours();
                        };

                        totalIdleAndBillableHours();




                    };

                    calculateTotal();

                    var inputToView = function() {
                        var curInput = $curHoursInput.val();
                        var tsInput = app.tsInputIsValid($curHoursInput, $curHoursInput.val());
                        if (tsInput) {
                            $curQuestionsView.text($curQuestionsInput.val());
                            $curHoursView.text($curHoursInput.val());

                            $curQuestionsHidden.val($curQuestionsInput.val());
                            $curHoursHidden.val($curHoursInput.val());

                            calculateTotal();
                        }
                    };

//                    $curQuestionsInput.on({
//                        keyup: inputToView,
//                        click: inputToView
//                    }, calculateTotal);

                    $curHoursInput.on({
                        change : inputToView,
                        keyup: inputToView,
                        click: inputToView,
                    });

                };



                $bTask.on({
                    change: primaryCb
                });
                $('.b-hours').on({
                    change: primaryCb ,
                });


            }
        };

        var amountTotalFun = function() {
            if (options.isAmountTotal) {
                var $datePickers = $('.date-picker');

                if ($($datePickers[0]).prop('readonly') == true) {
                    $table.hide();

                    $links.each(function() {
                        $(this).attr('role', 'button');
                        $(this).attr('disabled', true);
                    });
                }

                var $deliverables = $table.find('.milestone-item-deliverable'),
                    $amounts = $table.find('.milestone-item-amount'),
                    $amountTotal = $('.milestone-total-amount'),
                    $links = $('#add-milestone-btn, #del-milestone-btn'),
                    $projectTotalValueHidden = $('.project-total-value-hidden'),
                    projectTotalValueHidden = Number($projectTotalValueHidden.val());

                // amount validation
                var amountValidatoinFun = function() {
                    if (projectTotalValueHidden !== Number($amountTotal.text())) {
                        if (!($amountTotal.hasClass('t-danger'))) {
                            $amountTotal.addClass('t-danger');
                        }
                    } else {
                        if ($amountTotal.hasClass('t-danger')) {
                            $amountTotal.removeClass('t-danger');
                        }
                    }
                };

                var amountTotal = function() {
                    var $amountsLen = $amounts.length,
                        i,
                        $curItem,
                        temp = 0;

                    for (i = 0; i < $amountsLen; i += 1) {
                        $curItem = Number($($amounts[i]).val());
                        temp += $curItem;
                    }
                    temp = temp.toFixed(2);
                    $amountTotal.text(temp);

                    amountValidatoinFun();
                };

                amountTotal();

                $amounts.on({
                    keyup: amountTotal,
                    click: amountTotal
                });
            }
        };

        daysTotalFun();
        billableTotalFun();
        amountTotalFun();

        if (options.plannedEffortCalc) {
            app.plannedEfforInit($table);
        }

        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));


app.workingDaysBetweenDates = function(startDate, endDate) {
    var newDate,
        holidayCount = 0,
        holidaysListLen = app.holidaysList.length;

    // Validate input
    if (endDate < startDate)
        return 0;

    // Calculate days between dates
    var millisecondsPerDay = 86400 * 1000; // Day in milliseconds
    startDate.setHours(0, 0, 0, 1); // Start just after midnight
    endDate.setHours(23, 59, 59, 999); // End just before midnight
    var diff = endDate - startDate; // Milliseconds between datetime objects
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

    // Remove holidays
    var startDateFormat,
        startGetDay;

    for (var i = 0; i < holidaysListLen; i += 1) {
        if (app.holidaysList[i] >= startDate && app.holidaysList[i] <= endDate) {
            holidayCount += 1;
        }
    }

//    console.log('holidayCount:' + holidayCount);

    return days - holidayCount;
};

app.getPlannedEffort = function($startDate, $endDate, $plannedEffort, $plannedPercent, percent) {
    // get value and formatting
    var startDateVal = $startDate.val();
    var startDate = startDateVal.split('-');
    var startDateLen = startDate.length;

    var endDateVal = $endDate.val();
    var endDate = endDateVal.split('-');
    var endDateLen = endDate.length;

    var plannedPercentVal = $plannedPercent.val();
    var plannedEffortVal = $plannedEffort.val();


    plannedPercentVal = Number(plannedPercentVal);
    plannedEffortVal = Number(plannedEffortVal);


    // Type cast
    for (var i = 0; i < startDateLen; i += 1) {
        startDate[i] = Number(startDate[i]);
    }

    for (i = 0; i < endDateLen; i += 1) {
        endDate[i] = Number(endDate[i]);
    }

    startDate = startDate.join();
    endDate = endDate.join();

    // Create Date Object
    startDate = new Date(startDate);
    endDate = new Date(endDate);

    // Calculate planned effort
    var totalPlannedEffort = app.workingDaysBetweenDates(startDate, endDate) * 8;

    if (percent) {
        var plannedEffortPercent = (plannedEffortVal / totalPlannedEffort) * 100; // Calculate effort percentage
        plannedEffortPercent = Math.round(plannedEffortPercent);
        plannedEffortPercent = Number(plannedEffortPercent);


        return {
            plannedEffortPercent: plannedEffortPercent
        };
    } else {
        var plannedEffort = totalPlannedEffort * (plannedPercentVal / 100);
        plannedEffort = plannedEffort.toFixed(2);
        //plannedEffort = Math.round(plannedEffort);

        return {
            plannedEffort: plannedEffort
        };
    }
};


app.plannedEfforInit = function($table) {
    var $tableRows = $table.find('tr'),
        item,
        starDateItem,
        endDateItem,
        plannedEffortItem,
        plannedEffortPercentItem,
        row,
        holiday,
        holidayDay,
        totalHolidayLen = window.holidays.data.length;
    app.holidaysList = [];


    app.proPlannedEffortPercentItems = $('.pro-planned-effort-percent, .pro-planned-effort');

    for (var i = 0; i < totalHolidayLen; i += 1) {
        holiday = new Date(window.holidays.data[i].date);
        holidayDay = holiday.getDay();

        if (holidayDay !== 0 && holidayDay !== 6) {
            app.holidaysList.push(holiday);
        }
    }

    // Calculate effort for each row
    $tableRows.each(function(index) {
        if (index > 0) {
            item = $(this);
            starDateItem = item.find('.pro-start-date');
            endDateItem = item.find('.pro-end-date');
            plannedEffortItem = item.find('.pro-planned-effort'),
                plannedEffortPercentItem = item.find('.pro-planned-effort-percent');

            plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
        }
    });



    // Calculate PlannedEffort when change effort
    app.calcPlannedEffortCurRow = function(e) {
        item = $(this);
        row = item.closest('tr');
        starDateItem = row.find('.pro-start-date');
        endDateItem = row.find('.pro-end-date');
        plannedEffortItem = row.find('.pro-planned-effort');
        plannedEffortPercentItem = row.find('.pro-planned-effort-percent');

        if (item.hasClass('pro-planned-effort-percent')) {
            plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
        }

        if (item.hasClass('pro-planned-effort')) {
            plannedEffortPercentItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem, 'percent').plannedEffortPercent);
        }
    };


    app.proPlannedEffortPercentItems.on({
        'keyup': app.calcPlannedEffortCurRow,
        'click': app.calcPlannedEffortCurRow
    });

    app.getEffortCurRowId();

    $('.date').on('change', function() {
        app.calcCurRowChangeDate($table);
    });
};



app.autoFillInit = function($currentElement, $currentChapter) {
    function fireEvent(element, event) {
        if (document.createEventObject) {
            // dispatch for IE
            var evt = document.createEventObject();
            return element.fireEvent('on' + event, evt)
        } else {
            // dispatch for firefox + others
            var evt = document.createEvent("HTMLEvents");
            evt.initEvent(event, true, true); // event type,bubbling,cancelable
            return !element.dispatchEvent(evt);
        }
    }

    function dismissRelatedLookupPopup(win, chosenId) {
        var name = windowname_to_id(win.name);
        var elem = document.getElementById(name);
        if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
            elem.value += ',' + chosenId;
        } else {
            elem.value = chosenId;
        }
        fireEvent(elem, 'change');
        win.close();
    }

    if (typeof(dismissAddAnotherPopup) !== 'undefined') {
        var oldDismissAddAnotherPopup = dismissAddAnotherPopup;
        dismissAddAnotherPopup = function(win, newId, newRepr) {
            oldDismissAddAnotherPopup(win, newId, newRepr);
            if (windowname_to_id(win.name) == $curElement.attr('id')) {
                $curElement.change();
            }
        }
    }
};

// Get holiday list when change member
$.fn.getMemberHolidayList = function(options) {
    var o = $(this),
        $select = o.parent().find('.value-select'),
        selectedVal = $select.val();

    $.ajax({
        url: '/myansrsource/getholidays/' + selectedVal + '/',
        dataType: 'json',
        success: function(data) {
            data = data.data;

            helper.clearArray(app.holidaysList);

            var holiday,
                holidayDay,
                totalHolidayLen = data.length;

            for (var i = 0; i < totalHolidayLen; i += 1) {
                holiday = new Date(data[i].date);
                holidayDay = holiday.getDay();

                if (holidayDay !== 0 && holidayDay !== 6) {
                    app.holidaysList.push(holiday);
                }
            }

//            console.log(app.holidaysList);
        },
        error: function(data) {
            console.log("ERROR:  " + data);
        }
    });

    console.log('Selected Val: ' + selectedVal);
};

helper.clearArray = function(arr) {
    while (arr.length) {
        arr.pop();
    }
};
//  sending csrf token for ajax post submission don't try to modify unless there's a change suggested in django docs

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$("[name$='project']").on('focus', function(){
    var tmp_id = this.id.split('-');
    var tmp_is_internal_id = tmp_id[0]+'-'+tmp_id[1]+'-is_internal';
    $('#'+tmp_is_internal_id).data('prev_value', $('#'+tmp_is_internal_id).val());
});
is_changed =false;
//$("[name$='project']").on('change', function(){
//    var tmp_id = this.id.split('-');
//    var tmp_is_internal_id = tmp_id[0]+'-'+tmp_id[1]+'-is_internal';
//    $('#'+tmp_is_internal_id).data('prev_value', $('#'+tmp_is_internal_id).val());
//});