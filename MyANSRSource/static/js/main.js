/* Global namespace for entire application */
var app = app || {};
var helper = helper || {};

// Helper
helper.range = function(start, end) {
    var result = [];
    for(var i = start; i < end; i += 1) {
        result.push(i);
    }

    return result;
};

app.billableSetZeroList = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 
                           16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 
                           28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 
                           40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52, 
                           53, 54];

app.spaceToUnderscore = function($containerEle) {
    var items = $containerEle.find('td *'),
        item,
        itemId;

        items.each(function() {
        item = $(this);
        itemId = item.attr('id');

        if(itemId) {
            if(/\s/.test(itemId)) {
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


app.changeProject = function() {
    app.billableSelectProject.on('change', function() {
        var $this = $(this),
            $rows = $this.closest('tr'),
            $projectUnitsElement = $rows.find('.project-unit'),
            selectedValue = Number($this.val()),
            selectedProject;
            $.ajax({
                url: '/myansrsource/gettask/' + selectedValue + '/',
                dataType: 'json',
                success: function(data) {
                    var data = data.data,
                        dataLen = data.length,
                        options = '',
                        i;
                    for (i = 0; i < dataLen; i++) {
                        options += '<option value="' + data[i].id + '">' + data[i].name + '</option>';
                    }
                    $rows.find(".b-task").html(options);
                },
                error: function(data) {
                    console.log('Error: ' + data);
                }
            });
            $.ajax({
                url: '/myansrsource/getchapters/' + selectedValue + '/',
                dataType: 'json',
                success: function(data) {
                    var data = data.data,
                        dataLen = data.length,
                        options = '',
                        i;
                    for (i = 0; i < dataLen; i++) {
                        options += '<option value="' + data[i].id + '">' + data[i].name + '</option>';
                    }
                    $rows.find(".b-chapter").html(options);
                },
                error: function(data) {
                    console.log('Error: ' + data);
                }
            });


        // get current project by id
        if(selectedValue != 0) {
            selectedProject = app.getById(app.projectsList, 'project__id', selectedValue);

            //console.log(selectedProject);

            app.curProjectUnitShort = selectedProject.project__projectType__code;
            app.curProjectUnit = selectedProject.project__projectType__description;
            app.norms = selectedProject.project__maxProductivityUnits;

            $projectUnitsElement.text(app.curProjectUnitShort);
        }
    });
};

// Get particular object from array of object
app.getById = function(arr, propName, id) {
    for (var d = 0, len = arr.length; d < len; d += 1) {
        if (arr[d][propName] === id) {
            return arr[d];
        }
    }
};

// Main
(function() {
    $(document).ready(function() {
        var $popover = $('.popover');
        app.norms = '0.0 / Day';
        // Manage project
        var $changeTeamMembers = $('#change-team-members');
        if($changeTeamMembers.length > 0) {
            app.spaceToUnderscore($changeTeamMembers);

            $changeTeamMembers.dynamicForm({
                add: '#addForm',
                del: '#delete-member',
                calendar: true,
                plannedEffortCalc: true,
                changeTeamMember: true,
                setEditableAll: true,
                defaultValues: {  // When add row, set the elements default values
                    setZeroList: [23],
                    setEmptyList: null
                },
                setEnableList: [24]
            });
        }

        var $changeMilestone = $('#change-milestones');
        if($changeMilestone.length > 0) {
            app.spaceToUnderscore($changeMilestone);

            $changeMilestone.dynamicForm({
                add: '#add-milestone-btn',
                del: '#delete-member',
                calendar: true,
                changeMilestone: true,
                isAmountTotal: true,
                setEditableAll: true,
                defaultValues: {  // When add row, set the elements default values
                    setZeroList: [8, 6],
                    setEmptyList: [5]
                },
                setEnableList: [7, 9]
            });
        }

        // Project
        var addTeamMembers = $('#add-team-members');
        if(addTeamMembers.length > 0) {
            app.spaceToUnderscore(addTeamMembers);
            addTeamMembers.dynamicForm({
                add: '#addForm',
                del: '#delete-member',
                calendar: true,
                calendarPosList: [11, 16],
                addTeamMember: true,
                plannedEffortCalc: true,
                defaultValues: {  // When add row, set the elements default values
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

            for(var i = 0; i < totalHolidayLen; i += 1) {
                holiday = new Date(window.holidays.data[i].date);
                holidayDay = holiday.getDay();

                if(holidayDay !== 0 && holidayDay !== 6) {
                    app.holidaysList.push(holiday);
                }
            }

            // Calculate effort for each row
            $addTeamRows.each(function(index) {
                if(index > 0) {
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

                if(item.hasClass('pro-planned-effort-percent')) {
                    plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
                }

                if(item.hasClass('pro-planned-effort')) {
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
        if(financialMilestones.length > 0) {
            financialMilestones.dynamicForm({
                add: '#add-milestone-btn',
                del: '#del-milestone-btn',
                calendar: true,
                calendarPosList: [0],
                isAmountTotal: true,
                isFinancialMilestone: true,
                defaultValues: {  // When add row, set the elements default values
                    setZeroList: null,
                    setEmptyList: null
                },
                setEnableList: [8]
            });
        }

        // TimeSheet
        var timesheetBillable = $('#timesheet-billable');

        if(timesheetBillable.length > 0) {
            timesheetBillable.dynamicForm({
                add: '#timesheet-billable-add-btn',
                del: '#timesheet-billable-del-btn',
                billableTotal: true,
                defaultValues: {  // When add row, set the elements default values
                    setZeroList: app.billableSetZeroList,
                    setEmptyList: null
                }
            });

            $.ajax({
                url: '/myansrsource/getprojecttype',
                dataType: 'json',
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
        if(timesheetNonBillable.length > 0) {
            timesheetNonBillable.dynamicForm({
                add: '#timesheet-non-billable-add-btn',
                del: '#timesheet-non-billable-del-btn',
                daysTotal: true,
                nonBillable: true,
                defaultValues: {  // When add row, set the elements default values
                    setZeroList: [0, 2, 3, 4, 5, 6, 7, 8, 9],
                    setEmptyList: null
                }
            });
        }

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

        if(options.addTeamMember || options.changeTeamMember) {
            rowCountElement = $table.parent().parent().find('input[type="hidden"]:nth-of-type(3), input[type="hidden"]:nth-of-type(4)');
            rowCount = Number(rowCountElement.val());
        }

        if(options.isFinancialMilestone) {
            rowCountElement = $table.parent().parent().parent().find('input[type="hidden"]:nth-of-type(3)');
            rowCount = Number(rowCountElement.val());
        }
        
	if(options.changeMilestone) {
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
                $curIdSel;

        // Slice the id number from last row id
        lastRowId = app.getIdNo(lastRowId);
        lastRowId = Number(lastRowId);

	    newRow = lastRow.clone();
        newRowId = lastRowId + 1;

        /*screenName = newRow.find('td:first').children(':first').attr('id');
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
	    }*/

	    //newRow.find('input[type="hidden"]:last').val(0)
            
	    lastRow.after(newRow);

            $formFields = newRow.find('select, input, div, span');
            formFieldsLen = $formFields.length;
            rowCount += 1;

            if(options.billableTotal || options.nonBillable) {
                var disableElms = newRow.find('.ansr-disabled'),
                    disableElms2 = newRow.find('.disabled');

                if(disableElms.length > 0) {
                    disableElms.removeClass('ansr-disabled');
                }

                if(disableElms2.length > 0) {
                    disableElms2.removeClass('disabled');
                }
            }

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

                if(options.billableTotal || options.nonBillable) {
                    var rowCountInitialElement = $table.find('input[type="hidden"]:eq(1)');
                    $(rowCountInitialElement).attr('value', rowCount);
                }

                if(options.defaultValues.setZeroList) {
                    if(options.defaultValues.setZeroList.indexOf(index) !== -1) {
                        // For project unit not set zero
                        if(!$element.hasClass('project-unit')) {
                            if ($element.prop('tagName') === 'INPUT' || $element.prop('tagName') === 'SELECT') {
                                $element.val('0');
                                //console.log('input');
                            } else {
                                $element.text('0');
                                //console.log('not input');
                            }
                        }

                    }

                    //console.log(index + ': set zero');
                }

                if(options.defaultValues.setEmptyList) {
                    if(options.defaultValues.setEmptyList.indexOf(index) !== -1) {
                        $element.val('');
                        //console.log(index + ': set empty');
                    }
                }

                if(options.setEnableList) {
                    if(options.setEnableList.indexOf(index) !== -1) {
                        $element.prop('disabled', false);
                        //console.log(index + ': setEnableList');
                    }
                }

                if(options.setEditable) {
                    if(options.setEditable.indexOf(index) !== -1) {
                        $element.prop('readonly', false);
                        //console.log(index + ': setEditable');
                    }
                }

                if(options.setEditableAll) {
                    $element.removeAttr('readonly');
                }

                if(options.calendar) {
                    if(curId) {
                        if (curId.match('Date_pickers')) {
                            $curIdSel = $('#' + curId);
                            $curIdSel.datetimepicker({"pickTime": false, "language": "en-us", "format": "YYYY-MM-DD"}).on('change', function() {
                                app.calcCurRowChangeDate($table);
                            });
                        }
                    }
                }

                if(options.addTeamMember || options.changeTeamMember) {
                    if((formFieldsLen - 1) === index) {
                        $element.prop('disabled', false);
                    }
                    // For team member autocomplete
                    if($element.hasClass('autocomplete-light-widget') && $element.attr('data-widget-bootstrap') == 'normal') {
                        var $remove = $element.find('.remove');
                        if($remove.css('display') === 'none') {
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


                if(options.plannedEffortCalc) {
                    if($element.hasClass('pro-planned-effort-percent')) {
                        $element.val(100);
                    }
                }

                if(options.billableTotal) {
                    app.rowChapter = $('#id_form-' + newRowId + '-chapter');
                    if($element.hasClass('billable-select-project')) {
                        app.rowProject = $element;
                    }
                }



                if($element.hasClass('set-empty')) {
                    var elementType = $element.prop('tagName');
                    if(elementType === 'SELECT' || elementType === 'INPUT') {
                        $element.val('');
                    } else {
                        $element.text('');
                    }
                }

                if($element.hasClass('set-zero')) {
                    var elementType2 = $element.prop('tagName');
                    if(elementType2 === 'SELECT' || elementType2 === 'INPUT') {
                        $element.attr('value', 0);
                        console.log('index: ' + index + ' - ' + curId);  // Check the index value of the elements
                    } else {
                        $element.text('0');
                    }
                }
            console.log('index: ' + index + ' - ' + curId);  // Check the index value of the elements

            });


            daysTotalFun();
            billableTotalFun();
            amountTotalFun();

            if(options.plannedEffortCalc) {
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

            if(options.billableTotal) {
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
                var $totalBillableHours     = $('.total-billable-hours'),
                    $totalIdleHours         = $('.total-idle-hours');


                var $dayPopoverBtn = $table.find('.day-popover-button');
                var $bTask = $table.find('.b-task'),
                    $rowTotalView = $('.row-total-view');

                var popoverCon = '<div class="mar-bot-5"><label class="sm-fw-label project-type-popup">Questions</label> <input class="form-control small-input question-input" type="number" value="0"></div>';
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label hours">Hours</label> <input class="form-control small-input hours-input" type="number" value="0" max="24"></div>';
                popoverCon += '<div class="mar-bot-5"><label class="sm-fw-label hours">Norm</label> <label class="small-input norm-input">0.0 / DAY</label></div>';

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
                        $curProjectUnit         = $curDayBtn.find('.project-unit'),
                        $curProjectPopupUnit    = $curDayBtn.next().find('.project-type-popup'),
                        $curProjectPopupNorm    = $curDayBtn.next().find('.norm-input'),
                        curQuestionsViewText    = $curQuestionsView.text(),
                        curHoursViewText        = $curHoursView.text(),
                        curProjectUnit          = $curProjectUnit.text(),
                        $curSelectProject       = $curRow.find('.billable-select-project'),
                        selectedValue   = Number($curSelectProject.val()),
                        selectedProject;

                    var viewToInput = function() {
                        $($curQuestionsInput).val(curQuestionsViewText);
                        $($curHoursInput).val(curHoursViewText);
                    };

                    var projectUnitViewToPopUp = function() {
                        $curProjectPopupUnit.text(app.curProjectUnit);

                        // get current project by id
                        if(selectedValue != 0) {
                            selectedProject = app.getById(app.projectsList, 'project__id', selectedValue);

                            //console.log(selectedProject);
                            app.curProjectUnitShort = selectedProject.project__projectType__code;
                            app.curProjectUnit      = selectedProject.project__projectType__description;
                            app.norms               = selectedProject.project__maxProductivityUnits;
                        } else {
                            app.norms = 0.0;
                        }

                        // Get project norms
                        $curProjectPopupNorm.text(app.norms + '/DAY');
                    };

                    projectUnitViewToPopUp();

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

			questionsTemp = questionsTemp.toFixed(2);
			hoursTemp = hoursTemp.toFixed(2)
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

                            for(i = 0; i < rTotalIdleHoursListLen; i += 1) {
                                curIdleTotal = Number($($rTotalIdleHoursList[i]).val());
                                tempIdleTotal += curIdleTotal;
                            }

                            for(i = 0; i < rTotalBillableHoursListLen; i += 1) {
                                curBillableTotal = Number($($rTotalBillableHoursList[i]).val());
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

                $(document).on('keyup', function(e) {
                    if(e.keyCode === 27) {
                        var $popover = $('.popover');
                        $popover.popover('hide');
                    }
                });

                $rowTotalView.on('focus', function() {
                    console.log('rTotalView trigged');
                    var $popover = $('.popover');
                    $popover.popover('hide');
                });

            }
        };

        var amountTotalFun = function() {
            if(options.isAmountTotal) {
                var $datePickers = $('.date-picker');

                if($($datePickers[0]).prop('readonly') == true) {
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
                    if(projectTotalValueHidden !== Number($amountTotal.text())) {
                        if(!($amountTotal.hasClass('t-danger'))) {
                            $amountTotal.addClass('t-danger');
                        }
                    } else {
                        if($amountTotal.hasClass('t-danger')) {
                            $amountTotal.removeClass('t-danger');
                        }
                    }
                };

                var amountTotal = function () {
                    var $amountsLen = $amounts.length,
                        i,
                        $curItem,
                        temp = 0;

                    for (i = 0; i < $amountsLen; i += 1) {
                        $curItem = Number($($amounts[i]).val());
                        temp += $curItem;
                    }
		    temp = temp.toFixed(2)
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

        if(options.plannedEffortCalc) {
            app.plannedEfforInit($table);
        }

        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));


app.workingDaysBetweenDates = function (startDate, endDate) {
    var newDate,
        holidayCount = 0,
        holidaysListLen = app.holidaysList.length;

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

    // Remove holidays
    var startDateFormat,
        startGetDay;

    for(var i = 0; i < holidaysListLen; i += 1) {
        if(app.holidaysList[i] >= startDate && app.holidaysList[i] <= endDate) {
            holidayCount += 1;
        }
    }

    console.log('holidayCount:' + holidayCount);

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
    for(var i = 0; i < startDateLen; i += 1) {
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
    var totalPlannedEffort = app.workingDaysBetweenDates(startDate, endDate) * 8;

    if(percent) {
        var plannedEffortPercent = (plannedEffortVal/totalPlannedEffort) * 100;  // Calculate effort percentage
        plannedEffortPercent = Math.round(plannedEffortPercent);
        plannedEffortPercent = Number(plannedEffortPercent);

        return {
            plannedEffortPercent: plannedEffortPercent
        };
    } else {
        var plannedEffort = totalPlannedEffort * (plannedPercentVal / 100);
        plannedEffort = Math.round(plannedEffort);

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

    for(var i = 0; i < totalHolidayLen; i += 1) {
        holiday = new Date(window.holidays.data[i].date);
        holidayDay = holiday.getDay();

        if(holidayDay !== 0 && holidayDay !== 6) {
            app.holidaysList.push(holiday);
        }
    }

    // Calculate effort for each row
    $tableRows.each(function(index) {
        if(index > 0) {
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

        if(item.hasClass('pro-planned-effort-percent')) {
            plannedEffortItem.val(app.getPlannedEffort(starDateItem, endDateItem, plannedEffortItem, plannedEffortPercentItem).plannedEffort);
        }

        if(item.hasClass('pro-planned-effort')) {
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
    function fireEvent(element,event){
        if (document.createEventObject){
            // dispatch for IE
            var evt = document.createEventObject();
            return element.fireEvent('on'+event,evt)
        }
        else{
            // dispatch for firefox + others
            var evt = document.createEvent("HTMLEvents");
            evt.initEvent(event, true, true ); // event type,bubbling,cancelable
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

    app.autoFillField($currentElement, $currentChapter);

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


app.autoFillField = function($curElement, $chapter){
    function fill_field(val, init_value){
        /*if (!val || val==''){
            options = '<option value="">---------<'+'/option>';
            $curElement.html(options);
            $($curElement[0].options[0]).attr('selected', 'selected');
            $curElement.trigger('change');
            return;
        }*/

        //var $chapter = $('#id_form-2-chapter');

        $.getJSON("/chaining/filter/MyANSRSource/Chapter/project/"+val+"/", function(j){
            var options = '<option value="">---------<'+'/option>';
            for (var i = 0; i < j.length; i++) {
                options += '<option value="' + j[i].value + '">' + j[i].display + '<'+'/option>';
            }
            var width = $chapter.outerWidth();
            $($chapter[0]).html(options);
            if (navigator.appVersion.indexOf("MSIE") != -1)
                $curElement.width(width + 'px');
            //$($chapter[0].options[0]).attr('selected', 'selected');

            var auto_choose = true;
            if(val){
                $($chapter[0].options[1]).attr('selected', 'selected');
            }
            /*if(auto_choose && j.length == 1){
                $($chapter[0].options[value="'+ j[0].value +'"]).attr('selected', 'selected');
            }*/
            //$chapter.trigger('change');
        })
    }

    if(!$curElement.hasClass("chained")){
        var val = $curElement.val();
        fill_field(val, "None");
    }

    $curElement.change(function(){
        var start_value = $chapter.val();
        var val = $(this).val();
        fill_field(val, start_value);
    });

};


// Get holiday list when change member
$.fn.getMemberHolidayList = function(options) {
    var o = $(this),
        $select = o.parent().find('.value-select'),
        selectedVal = $select.val();

    $.ajax({
        url: '/myansrsource/getholidays/' + selectedVal + '/' ,
        dataType: 'json',
        success: function( data ) {
            data = data.data;

            helper.clearArray(app.holidaysList);

            var holiday,
                holidayDay,
                totalHolidayLen = data.length;

            for(var i = 0; i < totalHolidayLen; i += 1) {
                holiday = new Date(data[i].date);
                holidayDay = holiday.getDay();

                if(holidayDay !== 0 && holidayDay !== 6) {
                    app.holidaysList.push(holiday);
                }
            }

            console.log(app.holidaysList);
        },
        error: function( data ) {
            console.log( "ERROR:  " + data );
        }
    });

    console.log('Selected Val: ' + selectedVal);
};

helper.clearArray = function(arr) {
    while (arr.length) {
        arr.pop();
    }
};


























