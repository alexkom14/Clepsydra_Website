$(document).ready(function () {
    $(".navbar-toggler").on("click", function () {
        $(this).blur();
        if ($(".navbar-toggler").hasClass("collapsed")) {
            $("#main-nav").removeClass("color");
        } else {
            $("#main-nav").addClass("color");
        }
    });
});
