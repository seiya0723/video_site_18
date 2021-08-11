$(function () {
    $("#l_sidebar_closer").on("click",function() {
            $("#l_sidebar").prop("checked",false);
    });
});

$(function () {
    $("#edit_menu_closer").on("click",function() {
        $(".comment_edit_menu_button").prop("value",false);
    });
});

$(function () {
    $("#reply_menu_closer").on("click",function() {
        $(".reply_edit_menu_button").prop("value",false);
    });
});

$(function () {
    $("#r_to_reply_menu_closer").on("click",function() {
        $(".r_to_reply_edit_menu_button").prop("value",false);
    });
});