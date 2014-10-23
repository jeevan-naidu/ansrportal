/* Global namespace for entire application */

var app = {};

// Form control module
app.form_ctrl = (function() {
    var module = {},
        addRow = $('#addForm');

    // Add
    module.add = function() {
        var table = $('.table-condensed')[1],
            lastRow = $(table).find('tr').last(),
            lastRowId = lastRow.find('td').first().find('select').attr('id'),
            newRow,
            newRowId,
            newRowIds = [],
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

    // Events
    addRow.on('click', function() {
        module.add();
    });

    return module;
})();

app.getIdNo = function(str) {
    return str.match(/\d+/)[0];
};
