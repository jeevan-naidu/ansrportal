(function($) {
    // datepicker, timepicker init
    grappelli.initDateAndTimePicker = function() {
        
        // HACK: get rid of text after DateField (hardcoded in django.admin)
        $('p.datetime').each(function() {
            var text = $(this).html();
            text = text.replace(/^\w*: /, "");
            text = text.replace(/<br>.*: /, "<br>");
            $(this).html(text);
        });
        
        var options = {
            // --------------------------------------------------
            // DEFINE YOUR CUSTOM DATEPICKER OPTIONS HERE
            // http://jqueryui.com/datepicker/
            // --------------------------------------------------

            beforeShow: function(year, month, inst) {
                grappelli.datepicker_instance = this;
            },
	    altFormat: "dd-mm-yy"
        };
        var dateFields = $("input[class*='vDateField']:not([id*='__prefix__'])");
        dateFields.datepicker(options);
        
        if (typeof IS_POPUP != "undefined" && IS_POPUP) {
            dateFields.datepicker('disable');
        }
        
        // HACK: adds an event listener to the today button of datepicker
        // if clicked today gets selected and datepicker hides.
        // use live() because couldn't find hook after datepicker generates it's complete dom.
        //$(".ui-datepicker-current").live('click', function() {
        //    $.datepicker._selectDate(grappelli.datepicker_instance);
        //    grappelli.datepicker_instance = null;
        //});
        
        // init timepicker
        $("input[class*='vTimeField']:not([id*='__prefix__'])").grp_timepicker();
        
    };
})(grp.jQuery);
