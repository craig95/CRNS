/**
 * Created by Craig on 2017/03/17.
 */
$( document ).ready(function() {
    (function () {
        setInterval(function(){
        var xhr = new XMLHttpRequest();
        xhr.open("GET", 'time?zone=' + $('#city_name').text(), true);
        xhr.onload = function (e) {
            var serverResponse = xhr.responseText;
            $('#time').html(serverResponse);
        };
        xhr.onerror = function (e) {
            console.error(xhr.statusText);
        };
        xhr.send(null);
        }, 1000);
    })();

});