var player_id;
var room_id;
var send_contents = {};
var mode;
var input_flag = true;
var game_flag = true
var clear_count = 0;
var enemy_hp;   // 敵の体力
var turn;   // 残り時間やターン数
var score;

// ウェブソケットの立ち上げ
function create_web_socket() {
    var protocol = '';
    if (window.location.protocol === 'https:') {
        protocol = 'wss:';
    } else {
        protocol = 'ws:';
    }
    console.log(player_id)
    send_contents = { "player_id": player_id, "word": [], "mode": "" }
    if ($("#game_mode").text() == "ソロモード") {
        mode = "solo"
        var chatSocket = new WebSocket(
            protocol + '//' + window.location.host +
            '/ws/solo/' + player_id + '/');
    }
    else {
        mode = "multi"
        $(".result_screen").show()
        $(".option").hide()
        $("#result").text("協力モード")
        $("#score").text("プレイヤーの参加を待ってます。")
        $(".btn").hide()
        $(".contents").css("opacity", "0.3");
        var chatSocket = new WebSocket(
            protocol + '//' + window.location.host +
            '/ws/multi/' + room_id + '/');
    }
    audioBGM()
    chatSocket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log(data)
        if (mode == "solo") {
            // ゲームオーバー
            if (data["data"]["mode"] == "end") {
                $(".option").hide()
                $(".form-inline").show()
                $(".result_screen").fadeIn(1000)
                $("#score").text(data["data"]["score"])
                $("#result").text("GAME OVER!!")
                $(".contents").css("opacity", "0.3");
                $("#next_stage_btn").hide()
            }
            // 制限時間を進める
            else if (data["data"]["mode"] == "time") {
                turn = data["data"]["term"]
                console.log(turn)
                $("#turn").text(turn)
            }
            // 初期化
            else if (data["data"]["mode"] == "init") {
                init(data);
                $("#word_input").focus()
            }
            // ゲーム進行中
            else if ((data["data"]["mode"] == "play") | (data["data"]["mode"] == "clear")) {
                // enemy_hp = data["data"]["enemy_hp"]
                damage = data["data"]["damage"]
                enemy_hp -= damage
                theme = data["data"]["theme"]
                if (data["data"]["term"].match(/回/)) {
                    if (game_flag) {
                        turn -= 1
                        $("#turn").text(turn + "回")
                    }
                }
                $("#theme").text(theme)
                if (game_flag) {
                    if (damage > 60) {
                        $("#log").append("<div class='card-text text-danger'>" + damage + "ダメージ与えた!！</div>")
                        $("#s-log").html("<div class='card-text text-danger'>" + damage + "ダメージ与えた!！</div>")
                    }
                    else if (damage > 0) {
                        $("#log").append("<div class='card-text'>" + damage + "ダメージ与えた</div>")
                        $("#s-log").html("<div class='card-text'>" + damage + "ダメージ与えた</div>")
                    }
                    else if (damage == 0) {
                        $("#log").append("<div class='card-text'>効果は無いみたいだ・・・</div>")
                        $("#s-log").html("<div class='card-text'>効果は無いみたいだ・・・</div>")
                    }
                    else {
                        $("#log").append("<div class='card-text'>" + damage + "回復させてしまった・・・</div>")
                        $("#s-log").html("<div class='card-text'>" + damage + "回復させてしまった・・・</div>")
                    }
                }
                $('#log').animate({ scrollTop: $('#log')[0].scrollHeight }, 'fast');
                $("#enemy_hp").attr({
                    "value": enemy_hp
                });
                hit_effect(80);
                if (enemy_hp <= 0 & game_flag) {
                    game_flag = false
                    send_contents["mode"] = "clear"
                    chatSocket.send(JSON.stringify(send_contents))
                }
                else if (enemy_hp > 0 & game_flag & turn <= 0) {
                    game_flag = false
                    send_contents["mode"] = "end"
                    chatSocket.send(JSON.stringify(send_contents))
                }
                if (data["data"]["mode"] == "clear") {
                    console.log(clear_count)
                    $(".form-inline").hide()
                    $(".result_screen").fadeIn(1000)
                    if (clear_count == 10) {
                        $("#result").text("ALL CLEAR!!")
                        $("#next_stage_btn").hide()
                    }
                    else {
                        $("#result").text("GAME CLEAR!!")
                    }
                    $("#score").text(data["data"]["score"])

                    $(".contents").css("opacity", "0.3");
                }
            }
        }
        else if (mode == "multi") {
            // ゲームオーバー
            if (data["data"]["mode"] == "end") {
                $(".option").hide()
                $(".form-inline").show()
                $(".result_screen").fadeIn(1000)
                if (data["data"]["my_id"] == player_id)
                    $("#score").text(data["data"]["score"])
                $("#result").text("GAME OVER!!")
                $(".contents").css("opacity", "0.3");
                $("#next_stage_btn").hide()
            }
            // 制限時間を進める
            else if (data["data"]["mode"] == "time") {
                turn = data["data"]["term"]
                console.log(turn)
                $("#turn").text(turn)
            }
            // 初期化
            else if (data["data"]["mode"] == "init") {
                $(".form-inline").show()
                $(".btn").show()
                $(".contents").css("opacity", "1.0");
                $(".result_screen").hide()
                init(data);
                $("#word_input").focus()
            }
            // ゲーム進行中
            else if ((data["data"]["mode"] == "play") | (data["data"]["mode"] == "clear")) {
                // enemy_hp = data["data"]["enemy_hp"]
                damage = data["data"]["damage"]
                enemy_hp -= damage
                theme = data["data"]["theme"][player_id.toString()]
                if (data["data"]["term"].match(/回/)) {
                    if (game_flag) {
                        turn -= 1
                        $("#turn").text(turn + "回")
                    }
                }
                $("#theme").text(theme)
                if (game_flag) {
                    if (damage > 60) {
                        $("#log").append("<div class='card-text text-danger'>" + damage + "ダメージ与えた!！</div>")
                        $("#s-log").html("<div class='card-text text-danger'>" + damage + "ダメージ与えた!！</div>")
                    }
                    else if (damage > 0) {
                        $("#log").append("<div class='card-text'>" + damage + "ダメージ与えた</div>")
                        $("#s-log").html("<div class='card-text'>" + damage + "ダメージ与えた</div>")
                    }
                    else if (damage == 0) {
                        $("#log").append("<div class='card-text'>効果は無いみたいだ・・・</div>")
                        $("#s-log").html("<div class='card-text'>効果は無いみたいだ・・・</div>")
                    }
                    else {
                        $("#log").append("<div class='card-text'>" + damage + "回復させてしまった・・・</div>")
                        $("#s-log").html("<div class='card-text'>" + damage + "回復させてしまった・・・</div>")
                    }
                }
                $('#log').animate({ scrollTop: $('#log')[0].scrollHeight }, 'fast');
                $("#enemy_hp").attr({
                    "value": enemy_hp
                });
                hit_effect(80);
                if (enemy_hp <= 0 & game_flag) {
                    game_flag = false
                    send_contents["mode"] = "clear"
                    chatSocket.send(JSON.stringify(send_contents))
                }
                else if (enemy_hp > 0 & game_flag & turn <= 0) {
                    game_flag = false
                    send_contents["mode"] = "end"
                    chatSocket.send(JSON.stringify(send_contents))
                }
                if (data["data"]["mode"] == "clear") {
                    $(".form-inline").hide()
                    $(".result_screen").fadeIn(1000)
                    if (clear_count == 10) {
                        $("#result").text("ALL CLEAR!!")
                        $("#next_stage_btn").hide()
                    }
                    else {
                        $("#result").text("GAME CLEAR!!")
                    }
                    if (data["data"]["my_id"] == player_id)
                        $("#score").text(data["data"]["score"])
                    $(".contents").css("opacity", "0.3");
                }
            }
        }
    }
    chatSocket.onclose = function (e) {
        console.error('切断されました。');
    };

    // 入力ワードの送信
    $("#word_submit").on("click", function (e) {
        e.preventDefault();
        if (input_flag) {
            input_flag = false
            setTimeout(function () {
                input_flag = true
            }, 1000)
            word = $("#word_input").val();
            theme = $("#theme").text();
            if (word == theme)
                word = ""
            send_contents["word"] = [word, theme];
            send_contents["mode"] = "play"
            chatSocket.send(JSON.stringify(send_contents));
            $("#word_input").val("");
            document.getElementById("atack_sound").currentTime = 0;
            document.getElementById("atack_sound").play();
        }
    });

    // 次のステージへ進む
    $("#next_stage_btn").on("click", function (e) {
        e.preventDefault();
        $(".contents").css("opacity", "1.0");
        $(".result_screen").fadeOut(1000)
        send_contents["mode"] = "next_stage"
        chatSocket.send(JSON.stringify(send_contents))
        $("#word_input").focus()
    })
}

// 初期化（敵画像、ターン数、体力のセット）
function init(data) {
    game_flag = true
    clear_count += 1
    $(".option").show()
    $(".form-inline").show()
    enemy_img_path = "/media/" + data["data"]["enemy_img"]
    enemy_hp = data["data"]["enemy_hp"]
    turn = data["data"]["turn"]
    theme = data["data"]["theme"]
    back = "/media/" + data["data"]["back"]
    if (mode == "multi") {
        theme = data["data"]["theme"][player_id.toString()]
    }
    $("body").attr("background", back)
    $(".enemy_info").hide()
    $(".enemy_info").fadeIn(3000)
    $("#enemy_img").attr("src", enemy_img_path)
    $("#theme").text(theme)
    $("#turn").text(turn)
    $("#enemy_hp").attr({
        "max": enemy_hp,
        "value": enemy_hp,
        "high": enemy_hp / 5 * 2,
        "low": enemy_hp / 5,
        "optimum": enemy_hp,
    });
    // ターン数
    if (data["data"]["term"].match(/回/)) {
        $(".term").text("残りターン数")
        turn = Number(data["data"]["term"].split("回")[0])
        $("#turn").text(turn + "回")
    }
    // 制限時間
    else {
        $(".term").text("制限時間")
        turn = data["data"]["term"]
        $("#turn").text(turn)
    }
    $("#word_input").focus()
}

// 終了ボタン
function player_logout() {
    $(".end_btn").on("click", function (e) {
        e.preventDefault();
        $.ajax({
            url: "/ajax/logout_player",
            type: "post",
            async: false,
            data: {
                "player_id": player_id
            }
        })
            .done(function () {
                window.location.href = "/"
            });
    });
}

// ヒットエフェクト
function hit_effect(speed) {
    $("#enemy_img").fadeOut(speed);
    $("#enemy_img").fadeIn(speed);
    $("#enemy_img").fadeOut(speed);
    $("#enemy_img").fadeIn(speed);
}

// BGMを流す
async function audioBGM() {
    document.getElementById("battle_bgm").currentTime = 0;
    document.getElementById("battle_bgm").loop = true;
    document.getElementById("battle_bgm").play();
}
window.onload = function () {
    $('audio').prop('volume', 0.5);
    this.audioBGM()
}
$(window).on("beforeunload", function () {
    if (mode == "multi") {
        $.ajax({
            url: "/ajax/exit_room",
            type: "post",
            async: false
        })
    }
});
$(function () {
    $(".result_screen").hide()
    $(".enemy_info").hide()
    player_id = Number($("#player_id").text())
    room_id = Number($("#room_id").text());
    console.log(room_id)
    create_web_socket();
    player_logout()
});