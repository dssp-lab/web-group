document.addEventListener("DOMContentLoaded", function () {
    // Modal Image Gallery
    window.onClick = function (element) {
        document.getElementById("img01").src = element.src;
        document.getElementById("modal01").style.display = "block";
        var captionText = document.getElementById("caption");
        captionText.innerHTML = element.alt;
    };

    // Sidebar toggle
    var mySidebar = document.getElementById("mySidebar");

    if (mySidebar) {
        window.w3_open = function () {
            mySidebar.style.display = (mySidebar.style.display === 'block') ? 'none' : 'block';
        };

        window.w3_close = function () {
            mySidebar.style.display = "none";
        };
    }
});