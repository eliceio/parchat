$(function() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $("#send-btn").on("click", chat);
    $("#send-msg").on("keyup", function(e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code == "13")
            chat();
    })
})


function chat() {
    var metrics = [];
    $(".ui.toggle.button.active").each((i, btn) => metrics.push(btn.value))
    if (metrics.length === 0) {
        alert("최소 한 개의 metric을 골라주세요(L2 norm, Cosine similarity)");
        return;
    }

    var message = $.trim($("#send-msg").val());
    $("#send-msg").val("");
    $("#send-msg").focus();
    if (message.length > 0) {
        construct_user_message(message)
            .then(() => send_and_receive_message(message, metrics));
    }
}

function construct_user_message(message) {
    return $.ajax({
        type: "POST",
        url: "/chat/echo_user/",
        data: {
            message: message
        },
        success: (res) => $("#comments").append(res),
    });
}

function send_and_receive_message(message, metrics) {
    return $.ajax({
        type: "POST",
        url: "/chat/response/progressive/",
        data: {
            "message": message,
            "request_from": window.location.href,
            "metrics[]": metrics,
        },
        success: (res) => $("#comments").append(res),
    });
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
