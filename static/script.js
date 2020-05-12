$(function () {
    $(window).on('scroll', function () {
        if ( $(window).scrollTop() > 10 ) {
            $('.navbar').addClass('active');
        } else {
            $('.navbar').removeClass('active');
        }
    });
});

function search_click() {
    window.location = "/search";  
}

function home_click() {
    window.location = "/";  
}

function about_click() {
    window.location = "/about";  
}

function parse_search_args() {
    var is_swear = document.getElementById('is_swear').checked ? 1 : 0;
    var contains_thread = document.getElementById('contains_thread').checked ? 1 : 0;
    var contains_img = document.getElementById('contains_img').checked ? 1 : 0;
    var popularity = document.getElementById('popularity').value
    var amount = document.getElementById('amount').value
    
    var result = '/search_result/'
    if (amount != '') {
        result += 'amount=' + amount + '&'
    }
    if (popularity != '') {
        result += 'popularity=' + popularity + '&'
    }
    result += 'swears=' + is_swear + '&'
    result += 'contains_img=' + contains_img + '&'
    result += 'thread=' + contains_thread
    console.log(result)
    window.location = result
}