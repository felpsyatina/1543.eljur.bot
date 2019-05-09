function move_carusel(step = 1) {
    if (total_slides > step) {
        show_slide((cur_slide + step) % total_slides)
    }
    cur_slide = (cur_slide + step) % total_slides;
}

function show_slide(new_slide) {
    slides[cur_slide].classList.replace("active", "not_active");
    slides[new_slide].classList.replace("not_active", "active");
}

function set_up() {
    if (total_slides >= 1) {
        cur_slide = 0;
        slides[0].classList.add("active");
        for (let i = 1; i < total_slides; i++) {
            slides[i].classList.add("not_active")
        }
    }
}

var cur_slide = 0;
var slides = document.getElementsByClassName("news");
var total_slides = slides.length;

set_up();

setInterval(function () {
    move_carusel()
}, 10000);
