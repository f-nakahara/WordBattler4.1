var player_id;
var room_id;
var send_contents = {};
var mode;
var p1_id;
var p2_id;
var enemy_hp;
var turn;
var game_flag = true;
var score = 0
var init_flag = true;
var effect;
var term;
var stage_id;

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
    $(".result_screen").show()
    $(".option").hide()
    $("#result").text("協力モード")
    $("#score").text("プレイヤーの参加を待ってます。")
    $(".btn").hide()
    $(".contents").css("opacity", "0.3");
    var chatSocket = new WebSocket(
        protocol + '//' + window.location.host +
        '/ws/view/' + room_id + '/');

    audioBGM()
    chatSocket.onmessage = function (e) {
        var data = JSON.parse(e.data);
        console.log(data)

        // ゲームオーバー
        if (data["data"]["mode"] == "end") {
            turn = data["data"]["term"]
            $(".result_screen").fadeIn(1000)
            get_score()
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
            init_flag = false

        }
        // ゲーム進行中
        else if ((data["data"]["mode"] == "play") | (data["data"]["mode"] == "clear")) {
            damage = data["data"]["damage"]
            effect = "/media/" + data["data"]["effect"]
            if (game_flag)
                score += damage
            if (init_flag) {
                init_flag = false
                init(data)
            }
            enemy_hp -= damage
            p1_theme = data["data"]["theme"][p1_id.toString()]
            p2_theme = data["data"]["theme"][p2_id.toString()]
            write_id = data["data"]["write_id"]
            input_word = data["data"]["input_word"]
            before_theme = data["data"]["before_theme"]
            $("#theme1").text(p1_theme)
            $("#theme2").text(p2_theme)
            if (term.match(/回/)) {
                turn -= 1
                $("#turn").text(turn + "回")
            }
            var log = "#log"
            if (p1_id == write_id)
                log += "1"
            else
                log += "2"
            console.log(log)
            if (game_flag) {
                $("#effect").attr("src", effect)
                if (damage > 60)
                    $(log).append("<div class='card-text'>●お題：" + before_theme + "<br>　入力：" + input_word + "<br>" + "<span class='text-danger'>　" + damage + "ダメージ与えた!！</span></div>").trigger("create")
                else if (damage > 0)
                    $(log).append("<div class='card-text'>●お題：" + before_theme + "<br>　入力：" + input_word + "<br>" + "　" + damage + "ダメージ与えた</div>")
                else if (damage == 0)
                    $(log).append("<div class='card-text'>●お題：" + before_theme + "<br>　入力：" + input_word + "<br>" + "　効果は無いみたいだ・・・</div>")
                else
                    $(log).append("<div class='card-text'>●お題：" + before_theme + "<br>　入力：" + input_word + "<br>" + "　" + damage + "回復させてしまった・・・</div>")
            }
            $(log).animate({ scrollTop: $(log)[0].scrollHeight }, 'fast');
            $("#enemy_hp").attr({
                "value": enemy_hp
            });
            hit_effect(80);
            if (enemy_hp <= 0) {
                game_flag = false
            }
            if (data["data"]["mode"] == "clear") {
                init_flag = true
                $(".form-inline").hide()
                $(".result_screen").fadeIn(1000)
                get_score()
                $("#result").text("GAME CLEAR!!")
                $(".contents").css("opacity", "0.3");
            }
        }
    }
    chatSocket.onclose = function (e) {
        console.error('切断されました。');
    };
}

// 初期化（敵画像、ターン数、体力のセット）
function init(data) {
    $(".form-inline").show()
    $(".btn").show()
    $(".contents").css("opacity", "1.0");
    $(".result_screen").hide()
    effect = "/media/" + data["data"]["effect"]
    stage_id = data["data"]["stage_id"]
    game_flag = true
    p1_id = data["data"]["p1_id"]
    p2_id = data["data"]["p2_id"]
    get_player_name()
    console.log(p1_id, p2_id)
    $(".option").show()
    enemy_img_path = "/media/" + data["data"]["enemy_img"]
    enemy_hp = data["data"]["enemy_hp"]
    turn = data["data"]["turn"]
    back = "/media/" + data["data"]["back"]
    p1_theme = data["data"]["theme"][p1_id.toString()]
    p2_theme = data["data"]["theme"][p2_id.toString()]
    $("body").attr("background", back)
    $(".enemy_info").hide()
    $(".enemy_info").fadeIn(3000)
    $("#enemy_img").attr("src", enemy_img_path)
    $("#stage_id").text(stage_id)
    $("#effect").attr("src", effect)
    $("#theme1").text(p1_theme)
    $("#theme2").text(p2_theme)
    $("#turn").text(turn)
    $("#enemy_hp").attr({
        "max": enemy_hp,
        "value": enemy_hp,
        "high": enemy_hp / 5 * 2,
        "low": enemy_hp / 5,
        "optimum": enemy_hp,
    });
    term = data["data"]["term"]
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

function get_score() {
    $.ajax({
        url: "/ajax/get_score",
        type: "post",
        data: {
            "p1_id": p1_id,
            "p2_id": p2_id
        }
    })
        .done(function (data) {
            $("#score").text(data)
        });
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

function get_player_name() {
    $.ajax({
        url: "/ajax/get_player_name",
        type: "post",
        async: false,
        data: {
            "p1_id": p1_id,
            "p2_id": p2_id
        }
    })
        .done(function (a) {
            data = JSON.parse(a)
            console.log(data)
            $("#p1_name").text(data["p1_name"])
            $("#p2_name").text(data["p2_name"])
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
$(function () {
    $(".result_screen").hide()
    $(".enemy_info").hide()
    player_id = Number($("#player_id").text())
    room_id = Number($("#room_id").text());
    console.log(room_id)
    create_web_socket();
    player_logout()
});