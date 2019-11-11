// ソロプレイヤーの登録
function login_player() {
    $("#solo_login").on("click", function (e) {
        e.preventDefault();
        var player_name = $("#solo_player_name_input").val();
        if (player_name == "")
            player_name = "unknown"
        $.ajax({
            url: "/ajax/login_player",
            type: "post",
            data: {
                "player_name": player_name,
                "mode": "solo"
            }
        })
            .done(function () {
                window.location.href = "mode/solo"
            });
    });
    $("#multi_login").on("click", function (e) {
        e.preventDefault();
        var player_name = $("#multi_player_name_input").val();
        var room_name = $("#room_name").val();
        if (player_name == "")
            player_name = "unknown"
        $.ajax({
            url: "/ajax/login_player",
            type: "post",
            data: {
                "player_name": player_name,
                "mode": "multi",
                "room_name": room_name
            }
        })
            .done(function (data) {
                if (data == "true")
                    window.location.href = "mode/multi"
                else {
                    $("#multi_footer").text("既に他のプレイヤーがプレイ中！")
                }
            });
    })
}


function ranking() {
    $("#ranking_btn").on("click", function () {
        window.location.href = "ranking"
    });
}

function view() {
    $("#view_login").on("click", function (e) {
        e.preventDefault()
        var room_name = $("#view_name").val()
        $.ajax({
            url: "/ajax/view_login",
            type: "POST",
            data: {
                "room_name": room_name
            }
        })
            .done(function (data) {
                // alert("OK")
                window.location.href = "view"
            });
    });
}

$(function () {
    login_player();
    ranking();
    view();
});