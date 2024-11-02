postFlask("SkyWayProgressId0")

// データをアプリからpythonに送る関数
function postFlask(data) {
    let fd = new FormData();
    fd.append('received_data', data);
    fetch('{{ url_for('execute') }}', {
        method: 'POST',
        body: fd,
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (myjson) {
            console.log("PythonにPOSTします。")
            console.log(myjson)
        });
}

// データをpythonからアプリに送る関数
function getFlask() {
    fetch('{{ url_for('execute') }}', {
        method: 'GET',
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (myjson) {
            console.log("PythonからGETします。")
            console.log(myjson)
            data = myjson;
            document.getElementById('send').click();
            getFlask();
        });

}
getFlask();