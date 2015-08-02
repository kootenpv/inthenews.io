// moment.js support; Source: http://stackoverflow.com/a/25110964/1575066
// use <time class="cw-relative-date" datetime="2014-06-09T12:32:10-00:00"></time> in html

(function () {

// Define a function that updates all relative dates defined by <time class='cw-relative-date'>
var updateAllRelativeDates = function() {
        $('time').each(function (i, e) {
            if ($(e).attr("class") == 'cw-relative-date') {

                // Initialise momentjs
                var now = moment();
                moment.locale('en', {
                    calendar : {
                        lastDay : '[Yesterday at] LT',
                        sameDay : '[Today at] LT',
                        nextDay : '[Tomorrow at] LT',
                        lastWeek : '[Last] dddd [at] LT',
                        nextWeek : 'dddd [at] LT',
                        sameElse : 'D MMM YYYY [at] LT'
                    }
                });

                // Grab the datetime for the element and compare to now                    
                var time = moment($(e).attr('datetime'));
                var diff = now.diff(time, 'days');

                // If less than one day ago/away use relative, else use calendar display
                if (diff <= 1 && diff >= -1) {
                    $(e).html('<span>' + time.from(now) + '</span>');
                } else {
                    $(e).html('<span>' + time.calendar() + '</span>');
                }
            }
        });
    };

// Register the timer to call it again every minute
setInterval(updateAllRelativeDates, 60000);

// Update all dates initially
updateAllRelativeDates();

    
})();


$("#pypi_button").click(function() {
  $( "#pypi_results" ).toggle( "fast", function() {
      // Animation complete.
  });
});

$("#twitter_button").click(function() {
  $( "#twitter_results" ).toggle( "fast", function() {
    // Animation complete.
  });
});
