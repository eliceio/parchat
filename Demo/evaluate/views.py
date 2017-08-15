from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from chat.views import get_progressive_response, get_conservative_response, get_all_response, get_all_meta_response


def evaluate(request):
    return render(request, "evaluate.html")


@ensure_csrf_cookie
def evaluate_models(request):
    message = request.POST["message"]
    # response_types = request.POST["models[]"]
    response_types = [
        "Progressive Congressman",
        "Conservative Congressman",
        "Congressman",
        "Congressman+",
    ]
    metrics = request.POST.getlist("metrics[]")

    response_progressive = get_progressive_response(message)
    response_conservative = get_conservative_response(message)
    response_all = get_all_response(message)
    response_all_meta = get_progressive_response(message)

    content_progressive = res2html(response_progressive, metrics)
    content_conservative = res2html(response_conservative, metrics)
    content_all = res2html(response_all, metrics)
    content_all_meta = res2html(response_all_meta, metrics)

    contents = [
        content_progressive,
        content_conservative,
        content_all,
        content_all_meta,
    ]

    args = {
        "lst": zip(response_types, contents)
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