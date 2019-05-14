function get_time_interval() {
    let intervals = rings_data["time_intervals"];
    let base = new Date(rings_data["base"]);
    let cur_custom_time = get_new_custom_time();
    let cur_custom_delta = get_delta_from_start_of_day(cur_custom_time);
    for (let i = 0; i < intervals.length; i++) {
        let start = new Date(intervals[i]["start"]).getTime() - base;
        let end = new Date(intervals[i]["end"]).getTime() - base;
        if (cur_custom_delta - start >= 0 && cur_custom_delta - start <= 8000) {
            return {"status": "ring"}
        }
        if (start <= cur_custom_delta && cur_custom_delta <= end) {
            return intervals[i];
        }
    }
}

function get_cur_real_time() {
    return new Date(new Date().getTime());
}

function get_time_delta(time_start, time_end) {
    return time_end - time_start;
}

function get_new_custom_time() {
    return new Date(custom_time.getTime() + get_time_delta(start_real_time, get_cur_real_time()));
}

function convert_time_to_string(time, chars) {
    let hh = ("0" + time.getHours()).substr(-2, 2);
    let mm = ("0" + time.getMinutes()).substr(-2, 2);
    let ss = ("0" + time.getSeconds()).substr(-2, 2);
    return [hh, mm, ss].join(chars);
}

function update_timer_ans_status() {
    let cur_status = get_time_interval();
    let status_text = "Not defined";
    let timer_text = "Not defined";

    if (cur_status["status"] === "ring") {
        timer.style.visibility = "hidden";
        status2.style.visibility = "hidden";
        update_status1("ЗВОНОК");
        status1.parentElement.classList.add("apply-shake");
        // status1.classList.remove("apply-shake");
        if (!is_goint_to_reload) {
            is_goint_to_reload = true;
            setTimeout(function () {
                reload_page()
            }, 8000);
        }
    } else {
        if (cur_status["status"] === "finished") {
            status_text = "Уроки закончились";
            status2.style.visibility = "hidden";
            timer.style.visibility = "hidden";
        } else {
            timer.style.visibility = "visible";
            status1.style.visibility = "visible";
            status2.style.visibility = "visible";
            let ms_remain = get_delta_from_start_of_day(new Date(cur_status["end"])) - get_delta_from_start_of_day(get_new_custom_time());
            let remain_str = ms_delta_to_hh_if_more_than_zero__mm__ss(ms_remain, ":");
            update_timer(remain_str);
            if (cur_status["status"] === "not_started") {
                status_text = "Уроки еще не начались";
                timer_text = "До начала 1 урока осталось";
                status2.style.visibility = "visible";
                timer.style.visibility = "visible";
            } else if (cur_status["status"] === "lesson") {
                status_text = "Идёт " + cur_status["number"] + " урок";
                timer_text = "До конца " + cur_status["number"] + " урока осталось";
                timer.style.visibility = "visible";
                status2.style.visibility = "visible";
            } else if (cur_status["status"] === "break") {
                status_text = "Идёт " + cur_status["number"] + " перемена";
                timer_text = "До начала " + (cur_status["number"] + 1) + " урока осталось";
                timer.style.visibility = "visible";
                status2.style.visibility = "visible";
            }
        }
        update_status1(status_text);
        update_status2(timer_text);
    }
}

function get_delta_from_start_of_day(time) {
    let time2 = new Date(time);
    time2.setHours(0, 0, 0, 0);
    return time - time2;
}

function ms_delta_to_hh_if_more_than_zero__mm__ss(delta, chars) {
    delta += 1000;
    let hh = Math.floor(delta % 43200000 / 3600000);
    let mm = ("00" + (Math.floor(delta % 3600000 / 60000)).toString()).substr(-2, 2);
    let ss = ("00" + (Math.floor(delta % 60000 / 1000)).toString()).substr(-2, 2);
    if (parseInt(hh, 10) > 0) {
        return [hh, mm, ss].join(chars);
    } else {
        return [mm, ss].join(chars);
    }
}

function update_timer(text) {
    timer.textContent = text;
}

function update_status1(text) {
    status1.textContent = text;
}

function update_status2(text) {
    status2.textContent = text;
}

function update_clock() {
    clock.textContent = convert_time_to_string(get_new_custom_time(), ":");
}

function updater() {
    update_clock();
    update_timer_ans_status();
}

function reload_page() {
    let new_date = get_cur_date();
    let new_lesson_num = get_new_lesson_num();
    let new_url = window.location.href.substr(0, window.location.href.indexOf("/") + 1) + "desk?";
    new_url += "number=" + new_lesson_num + "&" + "date=" + new_date;
    window.location = new_url;
}

function get_cur_date() {
    let date = new Date();
    return date.getFullYear() + ("0" + (date.getMonth() + 1)).substr(-2, 2) + ("0" + date.getDate()).substr(-2, 2)
}

function get_new_lesson_num() {
    let interval = get_time_interval();
    if (interval["status"] === "not_started" || interval["status"] === "break") {
        return interval["number"] + 1
    } else {
        return interval["number"]
    }
}

var rings_data = {
    "custom_time": "2019-05-01T09:25:00.000+03:00",
    "base": "2019-01-01T00:00:00.000+03:00",
    "time_intervals": [
        {
            "start": "2019-01-01T00:00:00.000+03:00",
            "end": "2019-01-01T08:30:00.000+03:00",
            "status": "not_started",
            "number": 0
        },
        {
            "start": "2019-01-01T08:30:00.000+03:00",
            "end": "2019-01-01T09:15:00.000+03:00",
            "status": "lesson",
            "number": 1
        },
        {
            "start": "2019-01-01T09:15:00.000+03:00",
            "end": "2019-01-01T09:25:00.000+03:00",
            "status": "break",
            "number": 1
        },
        {
            "start": "2019-01-01T09:25:00.000+03:00",
            "end": "2019-01-01T10:10:00.000+03:00",
            "status": "lesson",
            "number": 2
        },
        {
            "start": "2019-01-01T10:10:00.000+03:00",
            "end": "2019-01-01T10:30:00.000+03:00",
            "status": "break",
            "number": 2
        },
        {
            "start": "2019-01-01T10:30:00.000+03:00",
            "end": "2019-01-01T11:15:00.000+03:00",
            "status": "lesson",
            "number": 3
        },
        {
            "start": "2019-01-01T11:15:00.000+03:00",
            "end": "2019-01-01T11:35:00.000+03:00",
            "status": "break",
            "number": 3
        },
        {
            "start": "2019-01-01T11:35:00.000+03:00",
            "end": "2019-01-01T12:20:00.000+03:00",
            "status": "lesson",
            "number": 4
        },
        {
            "start": "2019-01-01T12:20:00.000+03:00",
            "end": "2019-01-01T12:30:00.000+03:00",
            "status": "break",
            "number": 4
        },
        {
            "start": "2019-01-01T12:30:00.000+03:00",
            "end": "2019-01-01T13:15:00.000+03:00",
            "status": "lesson",
            "number": 5
        },
        {
            "start": "2019-01-01T13:15:00.000+03:00",
            "end": "2019-01-01T13:35:00.000+03:00",
            "status": "break",
            "number": 5
        },
        {
            "start": "2019-01-01T13:35:00.000+03:00",
            "end": "2019-01-01T14:20:00.000+03:00",
            "status": "lesson",
            "number": 6
        },
        {
            "start": "2019-01-01T14:20:00.000+03:00",
            "end": "2019-01-01T14:40:00.000+03:00",
            "status": "break",
            "number": 6
        },
        {
            "start": "2019-01-01T14:40:00.000+03:00",
            "end": "2019-01-01T15:25:00.000+03:00",
            "status": "lesson",
            "number": 7
        },
        {
            "start": "2019-01-01T15:25:00.000+03:00",
            "end": "2019-01-01T23:59:59.999+03:00",
            "status": "finished",
            "number": 8
        }
    ]
};


if (!(window.location.toString().includes("date") && window.location.toString().includes("number"))) {
    setTimeout(function () {
                reload_page()
            }, 500);
}

var is_goint_to_reload = false;
var custom_time = new Date(get_cur_real_time().getTime() + get_delta_from_start_of_day(new Date("2019-05-14T00:00:00.000+03:00")));
var start_real_time = get_cur_real_time();
var clock = document.getElementById("clock");
var status1 = document.getElementById("status1");
var status2 = document.getElementById("status2");
var timer = document.getElementById("timer");

updater();
setInterval(updater, 10);
