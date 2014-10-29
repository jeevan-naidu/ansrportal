/* Global namespace for entire application */

var app = {};

// Form control module
app.form_ctrl = (function() {
    var module = {},
        addRow = $('#addForm'),
        delRow = $('#delete-member'),
        rowCountElement = $('#createProject').find('input[type="hidden"]:nth-of-type(3)'),
        rowCount = Number(rowCountElement.val());

        console.log(rowCount);

    // Add
    module.add = function() {
        var table = $('.table-condensed')[1],
            lastRow = $(table).find('tr').last(),
            lastRowId = lastRow.find('td').first().find('select').attr('id'),
            newRow,
            newRowId,
            $tds,
            $element,
            $curId,
            $curChildEle,
            curChildId;
        // Slice the id number from last row id
        lastRowId = app.getIdNo(lastRowId);
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

            if(index === 3) {
                $curChildEle = $element.find('div:nth-child(1n)');
                $curChildEle.attr('id', $curId);
                $curChildEle.attr('name', $curId);

                $('#' + $curId).datetimepicker({"pickTime": false, "language": "en-us", "format": "YYYY-MM-DD"});
            }

        });

        rowCount += 1;

        $(rowCountElement).attr('value', rowCount);
    };

    module.del = function() {
        var form = $('#createProject'),
            rows = form.find('tr'),
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




    // DOM Events
    addRow.on('click', function() {
        module.add();
    });

    delRow.on('click', function() {
        module.del();
    });

    // Export module
    return module;
})//();

app.getIdNo = function(str) {
    return str.match(/\d+/)[0];
};

// Form control plugin
(function() {
    $.fn.dynamicForm = function(options) {
        var $form = $(this),
            $addBtn = $(options.add),
            $delBtn = $(options.del),

            rowCountElement = $form.find('input[type="hidden"]:nth-of-type(3)'),
            rowCount = Number(rowCountElement.val());



        var add = function() {
            var lastRow = $($form).find('tr').last(),
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
        };

        var del = function() {
            var rows = $form.find('tr'),
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

        var getIdNo = function(str) {
            return str.match(/\d+/)[0];
        };


        // Dom events
        $addBtn.on('click', add);
        $delBtn.on('click', del);
    };
}(jQuery));

$('#createProject').dynamicForm({add: '#addForm', del: '#delete-member', calendar: true});

