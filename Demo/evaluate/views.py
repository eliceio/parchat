from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from chat.views import grab_model_args, get_response


@ensure_csrf_cookie
def evaluate(request):
    return render(request, "evaluate.html")


@ensure_csrf_cookie
def evaluate_models(request):
    message = request.POST["message"]
    model_names = request.POST.getlist("models[]")
    metrics = request.POST.getlist("metrics[]")

    contents = []
    for model_name in model_names:
        model_name, model_args = grab_model_args(model_name)
        response = get_response(message, **model_args)
        response_html = res2html(response, metrics)
        contents.append(response_html)

    args = {
        "lst": zip(model_names, contents)
    }
    return render(request, "messages.html", args)


def res2html(response, metrics):
    model_score = response["modelScore"]
    if len(metrics) == 1:
        metric = metrics[0]
        score = response["result"][metric]["score"]
        answer = response["result"][metric]["sentence"]

        sentence = """
            <strong>Sentence Score</strong>: %f<br>
            %s<br>
        """ % (score, answer)
    else:
        l2_score = response["result"]["l2"]["score"]
        l2_answer = response["result"]["l2"]["sentence"]
        cosine_score = response["result"]["cosine"]["score"]
        cosine_answer = response["result"]["cosine"]["sentence"]

        sentence = '''
            <strong>[L2 norm]</strong><br>
            &ensp;&ensp;<strong>Sentence Score</strong>: %f<br>
            &ensp;&ensp;%s<br>
            <strong>[Cosine distance]</strong><br>
            &ensp;&ensp;<strong>Sentence Score</strong>: %f<br>
            &ensp;&ensp;%s<br>
        ''' % (l2_score, l2_answer, cosine_score, cosine_answer)

    html = """
        <strong>Model Score</strong>: %f<br>
        %s
    """ % (model_score, sentence)

    return html