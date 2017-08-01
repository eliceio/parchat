from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def progressive(request):
    return render(request, "chat.html")


@ensure_csrf_cookie
def conservative(request):
    return render(request, "chat.html")


@ensure_csrf_cookie
def echo(request):
    print(request.path)
    response_type = grab_response_type(request.POST["request_from"])
    args = {
        "user_type": response_type,
        "content": request.POST["message"]
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def echo_user(request):
    response_type = "user"
    args = {
        "user_type": response_type,
        "content": request.POST["message"]
    }
    return render(request, "message.html", args)


def grab_response_type(string):
    response_types = [
        "progressive",
        "conservative"
    ]
    for type in response_types:
        if type in string:
            return type
