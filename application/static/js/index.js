let skipScrollUpdate = false;

$(document).ready(function() {

    // Countdown to registration opening
    var makeathonDate = new Date("Jan 30, 2020 23:59:99").getTime();
    setInterval(function() {
        var now = new Date().getTime();
        var remaining = makeathonDate - now;
        var days = Math.floor(remaining / (1000 * 60 * 60 * 24));
        var hours = Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((remaining % (1000 * 60)) / 1000);
        $('#countdown-days').html(days);
        $('#countdown-hours').html(hours);
        $('#countdown-minutes').html(minutes);
        $('#countdown-seconds').html(seconds);
        $('#countdown').html(days + 'D ' + hours + 'H ' + minutes + 'M ' + seconds + 'S');
    }, 1000);


    $('#top-bar li').click(function() {
        $('.title-bar').foundation('toggleMenu');
    });

    $(document).scroll(function() {
        if($(window).scrollTop() > 50) {
            $(".top-bar").addClass("top-bar-active");
        } else {
            //remove the background property so it comes transparent again (defined in your css)
           $(".top-bar").removeClass("top-bar-active");
        }
        if (skipScrollUpdate) {
            skipScrollUpdate = false;
        }
    });

	// Form submission
    $('.mailing-list').submit(function(e) {
        e.preventDefault();
        const form = $(this);
        const email = form.find('input[name="email"]').val();
        const data = {'email': email};
        $.post('mailinglist', data, function(result) {
            console.log(result);
            try {
                if (result['success']) {
                    alert(result['message']);
                } else {
                    alert(result['error']);
                }
            } catch (e) {
                alert('Error: ' + e.message);
            }
        });
    });
});
