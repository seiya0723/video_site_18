window.addEventListener("load" , function (){
    $(document).on("click",".report_submit",function(){ report( $(this).val() ); });

});


function report(pk){

    let form_elem   =  "#report_form_" + pk;

    let target = $("#report_target_" + pk).text();

    console.log(target);

    let target_id = pk;

    let data    = new FormData( $(form_elem).get(0) );
    data.append("target_id", pk);
    data.append("target",target);

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
            console.log(data.error);
        }
        else{
            console.log("通報完了");
        }

        alert(data.message);

        console.log(data);

    }).fail( function(xhr, status, error) {
        console.log(status + ":" + error );
    });

}