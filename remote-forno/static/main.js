$( function() {
    $( "#slider1" ).slider();
    $( "#slider2" ).slider();
    $( "#slider3" ).slider();
    $( "#slider4" ).slider();
    $( "#slider5" ).slider();
    $( "#slider6" ).slider();
    $( "#slider7" ).slider();
} );

$(".dropdown-menu li a").click(function(){
  var selText = $(this).text();
  console.log(selText);
  $(this).parents('.col-xs-6').find('.dropdown-toggle').html(selText+' <span class="caret"></span>');
});
