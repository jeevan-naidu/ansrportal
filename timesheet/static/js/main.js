/* Global namespace for entire application */

var app = {};

// Form control module
app.form_ctrl = (function() {
    var module = {},
        addRow = $('#addForm'),
        delRow = $('#delete-member');

    // Add
    module.add = function() {
        var table = $('.table-condensed')[1],
            lastRow = $(table).find('tr').last(),
            lastRowId = lastRow.find('td').first().find('select').attr('id'),
            newRow,
            newRowId,
            $tds,
            $curId;

        // Slice the id number from last row id
        lastRowId = app.getIdNo(lastRowId);
        lastRowId = Number(lastRowId);

        newRow = lastRow.clone();
        newRowId = lastRowId + 1;
        lastRow.after(newRow);

        $tds = newRow.find('td > :first-child');

        $tds.each(function() {
            $curId = $(this).attr('id');
            $curId = $curId.replace(app.getIdNo($curId), newRowId);

            $(this).attr('id', $curId);
            $(this).attr('name', $curId);
        });

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
            }
        });

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
})();

app.getIdNo = function(str) {
    return str.match(/\d+/)[0];
};
