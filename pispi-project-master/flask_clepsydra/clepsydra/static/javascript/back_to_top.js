$(document).ready(function () {

    $("#back_to_top_btn").on("click", function () {
        $(this).blur();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    $(document).scroll(function () {
        if ($(window).scrollTop() === 0) {
            $("#back_to_top_btn").hide();
        } else {
            $("#back_to_top_btn").show();
        }
    });
});

