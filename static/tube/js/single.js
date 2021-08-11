window.addEventListener("load" , function (){

    $("#single_video_comments_submit").on("click",function(){ comments_submit(); });
    single_video_comments_form_initialize();

    $(document).on("click",".rating_good",function(){ rate_submit(true); });
    $(document).on("click",".mylist_entry",function(){ rate_submit(false); });

    $(document).on("click",".follow",function(){ follow_user(); });
    $(document).on("click",".block",function(){ block_user(); });

    $(document).on("click","#video_delete", function() { video_delete();});
    $(document).on("click","#video_update", function() { video_update();});

    $(document).on("click",".comment_page",function(){ get_comment_page( $(this).val()); });


    //リプライのチェックボックスはリロード時にチェックを外す
    $(".reply_chk").prop("checked",false);
    //リプライ関係
    $(document).on("click",".reply_submit",function(){ comment_reply( $(this).val()); });
    //チェックボタンが有効になった時リプライのGET文を送信
    $(document).on("change",".reply_chk", function(){
        if ( $(this).prop("checked") ){
            comment_reply( $(this).attr("id").replace("reply_button_",""), true );
    }; });


    //リプライに対するリプライのチェックボックスはリロード時にチェックを外す
    $(".reply_to_reply_chk").prop("checked",false);
    //リプライ関係
    $(document).on("click",".reply_to_reply_submit",function(){ comment_reply_to_reply( $(this).val()); });
    //チェックボタンが有効になった時リプライのGET文を送信
    $(document).on("change",".reply_to_reply_chk", function(){
        if ( $(this).prop("checked") ){
            comment_reply_to_reply( $(this).attr("id").replace("reply_to_reply_button_",""), true );
    }; });

    //動画に対するコメント削除、編集。
    $(document).on("click",".v_c_delete_button", function() { video_comment_delete( $(this).val()); });
    $(document).on("click",".v_c_edit_button", function() { video_comment_edit( $(this).val() ); });

    //動画コメントのリプライの編集、削除。
    $(document).on("click",".reply_delete_button", function() { v_comment_reply_delete( $(this).val()); });
    $(document).on("click",".reply_edit_button", function() { v_comment_reply_edit( $(this).val() ); });

    //動画コメントのリプへのリプライの編集、削除。
    $(document).on("click",".r_to_reply_delete_button", function() { v_comment_r_to_reply_delete( $(this).val()); });
    $(document).on("click",".r_to_reply_edit_button", function() { v_comment_r_to_reply_edit( $(this).val() ); });




    const video   = document.querySelector("video");
    video.addEventListener("volumechange",(event) => {
        document.cookie = "volume=" + decodeURIComponent(event.target.volume) + ";Path=/single;SameSite=strict";
    });

    //video.jsを初期化させる。Cookieからの音量取得は
    video_initialize();


});


//Cookieから音量値取得して返す
function get_video_volume(){

    let cookies         = document.cookie;
    console.log(cookies);

    let cookiesArray    = cookies.split(';');
    let volume          = 0;

    for(let c of cookiesArray) {
        console.log(c);

        let cArray = c.split('=');
        if( cArray[0] === "volume"){
            volume  = Number(cArray[1]);
            console.log(volume);
            break;
        }
    }

    return volume;
}


function video_initialize(){

    //#video-jsを{}内の設定で初期化、返り値のオブジェクトをplayerとする。
    let player  = videojs( 'video-js',{
        //コントロール表示、アクセスしたら自動再生、事前ロードする(一部ブラウザではできない)
        controls: true,
        autoplay: true,
        preload: 'auto',


        fill:false,
        responsive: true,

        //再生速度の設定
        playbackRates: [ 0.25, 0.5, 1, 1.5, 2, 4, 8],

        //ローディングの表示
        LoadingSpinner:true,

        //音量は縦に表示
        controlBar: {
            volumePanel: { inline: false },
        }
    });

    //Cookieに格納されている音量の値をセットする。
    let v   = get_video_volume();
    player.volume(v);


    //生成したvideo.jsのオブジェクトに対して、イベントリスナの設定ができる。トリガーはvideoタグのものと同様
    //player.on("loadstart",function(){ console.log("start"); });
    //player.on("volumechange",function(){ console.log("音量が変わった"); });
    player.on("ended",function(){
        console.log("end");
        //alert('video is done!');
        //player.src = '次のビデオ.mp4';
        //player.play();

    });

    //video.jsのオブジェクトにはいくらかメソッドがあるので、引数に#video-jsを指定することで追加の処理を実行できる
    //例:特定キーを押したら発動するイベントリスナを定義、動画をミュートする、次のトラックに行くなど
    /*
    let test    = videojs('video-js');
    test.volume(0.4);
    */

    //カスタムスキンをクラスを指定
    player.addClass('vjs-matrix');

}

function set_video_volume(){

    get_video_volume();

    const video     = document.querySelector("video");
    video.volume    = volume;
}

function comments_submit(){

    let form_elem   = "#single_video_comments_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) { 

        if (data.error){
            $("#comments_message").addClass("upload_message_error");
            $("#comments_message").removeClass("upload_message_success");
        }
        else{
            $("#comments_message").addClass("upload_message_success");
            $("#comments_message").removeClass("upload_message_error");
            single_video_comments_form_initialize();

            $("#video_comments_area").html(data.content);
        }

        $("#comments_message").text(data.message)

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}
function single_video_comments_form_initialize() {
    $("[name='content']").val("");
}



//コメントのリプライ。comment.idを再利用することでフォーム、リプライの表示箇所を一意に特定できる。
//comment_reply呼び出し時、第二引数未指定の場合、getにはfalseが入る。(リプライのGETもPOSTも返却後の処理は同じなのでajaxの送信設定だけ書き換える)
function comment_reply(pk,get=false){

    let form_elem   = "#reply_form_" + pk;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    for (let v of data.entries() ){ console.log(v); }

    if (get) {
        var ajax_conf = {
            url: url,
            type: "GET",
            dataType: 'json'
        };
    }
    else{
        var ajax_conf   = {
            url: url,
            type: method,
            data: data,
            processData: false,
            contentType: false,
            dataType: 'json'
        };
    }

    $.ajax(ajax_conf).done( function(data, status, xhr ) {

        let target  = "#reply_content_" + pk;
        $(target).html(data.content);
        single_video_comments_form_initialize();

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}


function comment_reply_to_reply(pk,get=false){

    let form_elem   = "#reply_to_reply_form_" + pk;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    for (let v of data.entries() ){ console.log(v); }

    if (get) {
        var ajax_conf = {
            url: url,
            type: "GET",
            dataType: 'json'
        };
    }
    else{
        var ajax_conf   = {
            url: url,
            type: method,
            data: data,
            processData: false,
            contentType: false,
            dataType: 'json'
        };
    }

    $.ajax(ajax_conf).done( function(data, status, xhr ) {

        let target  = "#reply_to_reply_content_" + pk;
        $(target).html(data.content);
        single_video_comments_form_initialize();

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}


//動画のコメント削除
function video_comment_delete(pk){
    let form_elem   = ".v_comment_delete_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "DELETE";

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);

        }
        else{
            console.log("削除完了");
            $("#v_c_edit_message_" + pk).addClass("upload_message_success");
            $("#v_c_edit_message_" + pk).removeClass("upload_message_error");
        }

        $("#v_c_edit_message_" + pk).text(data.message);

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}
//動画のコメント編集
function video_comment_edit(pk) {

    let form_elem   = "#v_comment_update_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "PUT";

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("編集完了");
            $("#comments_message").addClass("upload_message_success");
            $("#comments_message").removeClass("upload_message_error");

            $("#video_comments_area").html(data.content);

        }

        $("#comments_message").text(data.message)
        console.log(data);


    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}

//動画コメントに対するリプライの削除
function v_comment_reply_delete(pk){
    let form_elem   = ".reply_delete_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "DELETE";

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);

        }
        else{
            console.log("削除完了");
            $("#reply_edit_message_" + pk).addClass("upload_message_success");
            $("#reply_edit_message_" + pk).removeClass("upload_message_error");
        }

        $("#reply_edit_message_" + pk).text(data.message);

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}

//動画コメントに対するリプライの編集
function v_comment_reply_edit(pk){

    let form_elem   = "#reply_update_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "PUT";

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("編集完了");
            $("#video_comments_area").html(data.content);
            $("#comments_message").addClass("upload_message_success");
            $("#comments_message").removeClass("upload_message_error");
        }

        $("#comments_message").text(data.message)
        console.log(data);


    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}



//動画コメントのリプに対するリプライの削除
function v_comment_r_to_reply_delete(pk){
    let form_elem   = ".r_to_reply_delete_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "DELETE";

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);

        }
        else{
            console.log("削除完了");
            $("#r_to_reply_edit_message_" + pk).addClass("upload_message_success");
            $("#r_to_reply_edit_message_" + pk).removeClass("upload_message_error");
        }

        $("#r_to_reply_edit_message_" + pk).text(data.message);

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}

//動画コメントのリプに対するリプライの編集
function v_comment_r_to_reply_edit(pk){

    let form_elem   = "#r_to_reply_update_form_" + pk ;

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "PUT";

    for (let v of data.entries() ){ console.log(v); }

    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        contentType: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("編集完了");
            $("#video_comments_area").html(data.content);
            $("#comments_message").addClass("upload_message_success");
            $("#comments_message").removeClass("upload_message_error");
        }

        $("#comments_message").text(data.message)
        console.log(data);


    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}




function rate_submit(rate){

    console.log(rate);


    let form_elem   = ".single_video_rating_content";

    let data    = JSON.stringify({ "flag":rate });
    let url     = $(form_elem).prop("action");
    let method  = "PATCH";

    $.ajax({
        url: url,
        type: method,
        contentType : 'application/json; charset=utf-8',
        enctype     : "multipart/form-data",
        data: data,
    }).done( function(data, status, xhr ) { 

        if (data.error){
            console.log(data.error);
            $("#mylist_message").addClass("upload_message_error");
            $("#mylist_message").removeClass("upload_message_success");
        }

        else{
            console.log("登録完了");
            $("#mylist_message").addClass("upload_message_success");
            $("#mylist_message").removeClass("upload_message_error");
            $("#single_video_rating_area").html(data.content);
        }
        $("#mylist_message").text(data.message);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}


//動画を削除する
function video_delete(){

    //#video_delete_formを指定、フォーム内のデータ、送信先URL、メソッドを抜き取る
    //TIPS:PUT、DELETE、PATCHはpropで参照しようとしてもGETに変換されてしまうので、直入力
    let form_elem   = "#video_delete_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "DELETE";

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    //Ajaxを送信する
    //http://semooh.jp/jquery/api/ajax/jQuery.ajax/options/
    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false, // dataをクエリ文字列に指定しない trueにするとcontentTypeの値はデフォルトで"application/x-www-form-urlencoded"になる
        contentType: false, //content-typeヘッダの値。processDataでfalseを指定したので、これは無くても動く
        dataType: 'json' //サーバーから返却されるデータはjson形式を指定
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
            $("#delete_message").addClass("upload_message_error");
            $("#delete_message").removeClass("upload_message_success");
        }
        else{
            console.log("削除完了");
            $("#delete_message").addClass("upload_message_success");
            $("#delete_message").removeClass("upload_message_error");
        }

        $("#delete_message").text(data.message)

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}


//動画を編集する
function video_update(){

    //#video_update_formを指定、フォーム内のデータ、送信先URL、メソッドを抜き取る
    //TIPS:PUT、DELETE、PATCHはpropで参照しようとしてもGETに変換されてしまうので、直入力
    let form_elem   = "#video_update_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = "PUT";

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    //Ajaxを送信する
    //http://semooh.jp/jquery/api/ajax/jQuery.ajax/options/
    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false, // dataをクエリ文字列に指定しない trueにするとcontentTypeの値はデフォルトで"application/x-www-form-urlencoded"になる
        contentType: false, //content-typeヘッダの値。processDataでfalseを指定したので、これは無くても動く
        dataType: 'json' //サーバーから返却されるデータはjson形式を指定
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("編集完了");
            //更新
            location.reload();
        }

        $("#delete_message").text(data.message)

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}


//コメントのページ移動
function get_comment_page(page){

    if (!(page)){ return false; }

    let form_elem   = "#comment_pagination_area";

    let url     = $(form_elem).prop("action") + "?page=" + page;
    let method  = $(form_elem).prop("method");

    console.log(url);

    $.ajax({
        url: url,
        type: "GET",     //getの代わりにmethodでもいい。
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log("error");
        }
        else{
            $("#video_comments_area").html(data.content);
            $(".single_video_comments").animate({scrollTop:0},100);
        }

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });


}



// フォロー処理
function follow_user(){
    let form_elem   = "#follow_user_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    //Ajaxを送信する
    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("フォロー処理完了");
        }

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}



// ブロック処理
function block_user(){
    let form_elem   = "#block_user_form";

    let data    = new FormData( $(form_elem).get(0) );
    let url     = $(form_elem).prop("action");
    let method  = $(form_elem).prop("method");

    //フォーム内のデータを確認できる
    for (let v of data.entries() ){ console.log(v); }

    //Ajaxを送信する
    $.ajax({
        url: url,
        type: method,
        data: data,
        processData: false,
        dataType: 'json'
    }).done( function(data, status, xhr ) {

        if (data.error){
            console.log(data.error);
        }
        else{
            console.log("ブロック処理完了");
        }

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}
