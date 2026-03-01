$(document).ready(function () {
    const navigationBarLinks = $(".navigation-bar").find(".col a");
    const progressBar = $(".progress-bar");

    const surveyStartButton = $("#survey-start-button");

    surveyStartButton.removeAttr("disabled");

    surveyStartButton.on("click", () => {
        $(".survey-start").hide();
        $(".image-class").first().show();
        $(".question-class").first().show();

        navigationBarLinks.first().removeClass("disabled");
    });

    $(document).on("click", "#next-button", function () {
        const parentQuestion = $(this).closest(".question-class");
        const nextQuestion = parentQuestion.nextAll(".question-class").eq(0);

        // get correct image for category change
        if (parentQuestion.next(".image-class").length !== 0) {
            parentQuestion.prevAll(".image-class").first().hide();
            parentQuestion.next(".image-class").show();

            const visibleImage = $(".image-class:visible");
            navigationBarLinks.filter("[data-category-order=" + visibleImage.attr("data-category-order") + "]").removeClass("disabled");

            progressBar.width((33.33 * visibleImage.attr("data-category-order")) + "%");
        }
        parentQuestion.hide();
        nextQuestion.show();
    });

    $(document).on("click", "#back-button", function () {
        const parentQuestion = $(this).closest(".question-class");
        const prevQuestion = parentQuestion.prevAll(".question-class").eq(0);

        // get correct image for category change
        if (parentQuestion.prev(".image-class").length !== 0) {
            parentQuestion.prev(".image-class").hide();
            parentQuestion.prevAll(".image-class").eq(1).show();

            progressBar.width((33.33 * $(".image-class:visible").attr("data-category-order")) + "%");
        }
        parentQuestion.hide();
        prevQuestion.show();
    });

    $(document).on("click", "#finish-button", function () {
        let answers = [];

        $(".question-class").each((qIndex, question) => {
            let $form = $(question).find(".form-container");

            if ($form.attr("data-type-of-question") === "radiogroup") {
                let radioButtons = $form.find('input');
                answers.push(radioButtons.index(radioButtons.filter(':checked')));

            } else if ($form.attr("data-type-of-question") === "checkbox") {
                let values = [];

                $form.find('input').each((chIndex, choice) => {
                    if ($(choice).is(':checked')) values.push(chIndex);
                });

                if (values.length === 0) answers.push(-1);
                else answers.push(values);
            } else if ($form.attr("data-type-of-question") === "dropdown") {
                let values = [];

                $form.find('option').each((chIndex, choice) => {
                    if ($(choice).is(':selected')) values.push(parseInt($(choice).val()));
                });
                answers.push(values);
            }

        });
        console.log(answers);

        // AJAX
        $.ajax({
            type: "POST",
            url: "/survey",
            dataType: "json",
            data: JSON.stringify({answers: answers}),
            contentType: "application/json",
            success: function (response) {
                console.log(response);
                window.location = "/user_profile";
            },
            error: function (error) {
                console.log(error);
                window.location = "/user_profile";
            }
        });

        $(this).attr("disabled", true);
    });

    // enable next button after first radio button press
    $(document).on("change", ".form-container", function () {
        $(this).parent().find(".btn.btn-primary").removeAttr("disabled");
    });

    navigationBarLinks.on("click", function (event) {
        event.preventDefault();

        // if pressed link category not equal to current survey category
        if ($(this).attr("data-category") != $(".question-class:visible").attr("data-category")) {
            $(".question-class:visible").hide();
            $(".image-class:visible").hide();

            $(".question-class[data-category='" + $(this).attr("data-category") + "'][data-question='0']").show();
            $(".image-class[data-category='" + $(this).attr("data-category") + "']").show();

            // change progress bar
            progressBar.width((33.33 * $(".image-class:visible").attr("data-category-order")) + "%");
        }
    });
});

// $(window).bind("beforeunload", () => {
//     return "Your answers will not be saved if you leave now";
// });
