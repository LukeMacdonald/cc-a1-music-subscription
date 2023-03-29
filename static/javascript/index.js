$("#togglePassword").click(function () {
    const element = $('#password');
    element.attr('type', (element.attr('type') === 'password' ? 'text' : 'password'));
    $(this).toggleClass('fa-eye');
    }

);
$('#register').hover(function() {
    $('.music').toggleClass('elements');

})