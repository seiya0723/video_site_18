/*
$(function (){
    $(".skip").on("click", function() { skip( $(this).val()); });
});
*/
//function skip(value){

 //これでは上手くいかない。
    var video = videojs($(".single_video"));

    seek(secs) {
      let time = this.player.currentTime() + secs;

      if (time < 0) {
        time = 0;
      }

      this.player.currentTime(time);
    },

    forward() {
      this.seek(10);
    },

    rewind() {
      this.seek(-10);
    },

