$(document).ready(function(){
  $(".hide_reply").click(function(){
    $(this).closest(".single_comment_container").find(".reply_form").toggleClass("hidden_reply");
  });
});


