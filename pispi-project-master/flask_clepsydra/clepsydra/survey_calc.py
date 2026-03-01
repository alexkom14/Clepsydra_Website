import os
import json


def calc_survey_results(answers):
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, "static/survey", "survey.json")
    with open(json_url, 'r', encoding='utf8') as survey_file:
        data = json.load(survey_file)

        answers = answers["answers"]
        answers_index = 0
        cat_score = [0.0, 0.0, 0.0, 0.0]
        factor = 1

        for cat_index, category in enumerate(data["categories"]):
            # print("category", category["categoryName"])
            for question in category["questions"]:
                # print("answer", answers[answers_index])

                # if factor exists and is True
                if "factor" in question and question["factor"]:
                    factor = question["answers"][answers[answers_index]]
                else:
                    if question["type"] == "radiogroup":
                        if answers[answers_index] == -1:
                            pass
                        else:
                            cat_score[cat_index] += question["answers"][answers[answers_index]] * factor
                            # print(cat_score[cat_index])

                    elif question["type"] == "checkbox":
                        if answers[answers_index] == -1:
                            pass
                        else:
                            for checkboxAnswer in answers[answers_index]:
                                cat_score[cat_index] += question["answers"][checkboxAnswer] * factor
                                # print(cat_score[cat_index])

                    elif question["type"] == "dropdown":
                        if answers[answers_index] == -1:
                            pass
                        else:
                            for dropDownIndex, dropDownAnswer in enumerate(answers[answers_index]):
                                cat_score[cat_index] += dropDownAnswer * question["answers"][dropDownIndex] * factor
                                # print(cat_score[cat_index])

                    factor = 1  # set factor back to one after calculation

                # if constant exists
                if "constant" in question:
                    cat_score[cat_index] += question["constant"]

                answers_index += 1

    return cat_score
