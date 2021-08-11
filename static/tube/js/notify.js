window.addEventListener("load" , function (){

    //全開、全閉
    $("#notify_all_close").on("click",function(){ $(".notify_content_chk").prop("checked",false) });
    $("#notify_all_open").on("click",function(){
        $(".notify_content_chk").prop("checked",true);

        let notifies    = $(".notify_content_chk");
        for (let n of notifies){
            if ( (n.value) && (n.checked) ){
                notify_read( n.value, n.id );
            }
        }
    });

    //既読処理
    $(".notify_content_chk").on("change", function(){ 
        if ( ($(this).val()) && ($(this).prop("checked")) ){
            notify_read( $(this).val(), $(this).prop("id") );
        }
    });

});


function notify_read(pk,id){

    //ここに既読化のAjaxを。フォームクラスで作るわけじゃないので、シリアライザ必要。

    let data    = JSON.stringify({ "notify":pk }); 
    let url     = "";
    let method  = "PATCH";

    $.ajax({
        url: url,
        type: method,
        contentType : 'application/json; charset=utf-8',
        enctype     : "multipart/form-data",
        data: data,
    }).done( function(data, status, xhr ) { 

        if (!data.error){
            $("#"+ id).val("");
            $("#"+ id + "~ label > i").remove();
        }

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    }); 
}


