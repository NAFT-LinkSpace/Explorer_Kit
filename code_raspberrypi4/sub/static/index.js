const { nowInSec, SkyWayAuthToken, SkyWayContext, SkyWayRoom, SkyWayStreamFactory, uuidV4 } = skyway_room;

// トーストが利用可能かどうかを保存する変数
var isToastAvailable = false;

// トースト初期化
$(document).ready(function () {
    toastr.options.timeOut = 1000; // 3秒
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": false,
        "progressBar": false,
        "positionClass": "toast-bottom-right",
        "preventDuplicates": false,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "3000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    }
    isToastAvailable = true;
    toastr.success('click');
});

// カメラ映像を取得できるか試験
// (メモ)音を入れるとバグるかもしれない
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then()
    .catch(e => {
        console.log('getUserMedia', e.message, e.name);
    });

// SkyWay Auth Tokenの作成(JWT形式)
// (メモ)本当はサーバー側で作成する
const token = new SkyWayAuthToken({
    jti: uuidV4(),
    iat: nowInSec(),
    exp: nowInSec() + 60 * 60 * 24,
    scope: {
        app: {
            id: 'SkyWayのアプリケーションIDをここにいれる',
            turn: true,
            actions: ['read'],
            channels: [{
                id: '*',
                name: '*',
                actions: ['write'],
                members: [{
                    id: '*',
                    name: '*',
                    actions: ['write'],
                    publication: { actions: ['write'], },
                    subscription: { actions: ['write'], },
                },],
                sfuBots: [{
                    actions: ['write'],
                    forwardings: [{ actions: ['write'], },],
                },],
            },],
        },
    },
}).encode('シックレートキーをここに入れる');

// アプリに送信するデータを保存する変数
var data = { message: "First Data" };

// アプリから受信したデータを保存する変数
var received_data = "";

(async () => {
    const localVideo = document.getElementById('local-video'); // カメラ映像をテストで表示する要素
    const myId = document.getElementById('my-id'); // ユーザIDを表示する要素
    const showButton = document.getElementById('show'); // カメラ映像を表示するボタン
    const sendButton = document.getElementById('send'); // データをアプリに再送信するボタン

    // カメラ映像の取得・データ送信準備
    const video = await SkyWayStreamFactory.createCameraVideoStream(video_settings);
    const dataStream = await SkyWayStreamFactory.createDataStream();

    // 取得したトークンを使用
    const context = await SkyWayContext.Create(token);
    // 同じ名前の部屋(room)が存在しなければ作成し、存在する場合にはそのroomを取得する
    const room = await SkyWayRoom.FindOrCreate(context, {
        type: 'p2p',
        name: 'room',
    });

    // 部屋の状態に変化があった際に呼び出される
    room.onClosed.add(({ state }) => {
        console.log("ROOM状態変化!")
        if (isToastAvailable) {
            toastr.error(state, "ROOM状態変化!");
        }
    });

    // roomに入室
    console.log("try joining room")
    const me = await room.join({ name: "member_raspberry" + (new Date()).getTime() });
    myId.textContent = me.id; // ユーザIDを表示

    // 映像の公開(publish)
    if (video_isAvailable == true) {
        await me.publish(video);
    }

    // データ送信準備
    const publication = await me.publish(dataStream);

    // 送信状態に変化があった際に呼び出される
    publication.onConnectionStateChanged.add(({ state, remoteMember }) => {
        console.log("送信状態変化！" + state)
        if (isToastAvailable) {
            toastr.error(state, "送信状態変化！");
            if (String(state) == "reconnecting") {
                location.reload()
            }
        }
    });

    // 相手から Publish された Stream を Subscribe する
    const subscribe = async (publication) => {
        if (publication.publisher.id === me.id) return; // 自分自身はsubscribeしない

        // subscribe先のユーザ名を保存
        const publisher_name = String(publication.publisher.name)

        // Schrittが既にroomにいたらキックする
        if (publisher_name.includes("member_raspberry")) {
            await room.leave(publication.publisher)
            console.log("kicked raspberry")
        } else {
            // subscribeする
            const { stream, subscription } = await me.subscribe(publication.id)
            if (stream.contentType === 'data') {
                // 文字列データを取得した場合はpythonに送信準備
                stream.onData.add((data) => {
                    console.log(data)
                    postFlask(data)
                })
            }
             // 受信状態に変化があった際に呼び出される
            subscription.onConnectionStateChanged.add((state) => {
                console.log("受信状態変化！" + state)
                if (isToastAvailable) {
                    toastr.warning(state, "受信状態変化！");
                }
            });
        }
    };

    // RoomにStreamがPublishされたときに呼び出される
    room.onStreamPublished.add((e) => subscribe(e.publication));
    room.publications.forEach(subscribe);

    // アプリにデータ送信する関数
    sendButton.onclick = async () => {
        dataStream.write(data)
    }

    // カメラ映像を表示する関数
    showButton.onclick = async () => {
        localVideo.muted = true;
        localVideo.playsInline = true;
        video.attach(localVideo);
        await localVideo.play();
    };
})();
