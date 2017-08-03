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
    var message = $.trim($("#send-msg").val());
    $("#send-msg").val("");
    $("#send-msg").focus();
    if (message.length > 0) {
        construct_user_message(message)
            .then(() => send_and_receive_message(message));
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

function send_and_receive_message(message) {
    return $.ajax({
        type: "POST",
        url: "/chat/answer/gm/",
        data: {
            message: message,
            request_from: window.location.href,
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
