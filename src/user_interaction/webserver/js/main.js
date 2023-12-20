const ADDRESS = "ws://robotpi-01.enst.fr:8765/"
const STATE_OPEN = 0;
const STATE_CONNECTING = 1;
const STATE_CLOSING = 2;
const STATE_CLOSED = 3;

const NOTIFICATION_INFO = 0;
const NOTIFICATION_WARN = 1;
const NOTIFICATION_ERROR = 2;

let ws = undefined;
let joystick = new Joystick(document.getElementById("joystick"), joystick_callback);
let under_voltage = document.getElementById("under_voltage");
let search_left = document.getElementById("search_left");
let search_right = document.getElementById("search_right");
search_left.addEventListener("click", () => {
    order = {
        "type": "option",
        "option": "search_left",
        "data": {}
    }

    send_message(order);
});
search_right.addEventListener("click", () => {
    order = {
        "type": "option",
        "option": "search_right",
        "data": {}
    }

    send_message(order);
});
let dragslide_maxspeed = new DragSlide(document.getElementById("dragslide_maxspeed"));
dragslide_maxspeed.transform_value = (x) => { return Math.min(Math.max(0, 0.1*x), 100); }
dragslide_maxspeed.transform_value_inverse = (x) => { return 10*x };
dragslide_maxspeed.display = (x) => { return Math.round(x*10)/10+"%" }
dragslide_maxspeed.set_value(100);
dragslide_maxspeed.callback = (x) => {
    let v = parseFloat(x);
    if (isNaN(v)) {
        v = 0;
    }
    let order = {
        "type": "option",
        "option": "max_speed",
        "data": {
            "value": v
        }
    }
    ws.send(JSON.stringify(order));
}
let mode_switch = document.getElementById("mode_switch");

let state = -1;
let mode = "manual";
let state_dom = document.getElementById("state");
let notifications_dom = document.getElementById("notifications");

mode_switch.addEventListener("change", (e) => {
    toggle_mode_autonomous(mode_switch.checked);
})

create_websocket();

function create_websocket() {
    ws = new WebSocket(ADDRESS);

    ws.onopen = function () {
        set_state(STATE_OPEN);
        // ws.send(JSON.stringify({ type: "info", content: "Connection established" }));
    };

    ws.onmessage = function (evt) {
        var received_msg = evt.data;
        console.log(received_msg);
        if (received_msg.type == "under-voltage") {
            under_voltage.classList.add("info-active");
        }
    };

    ws.onclose = () => {
        set_state(STATE_CLOSED);
        new_notification({ header: "Connection closed", content: "Host closed the connection, or the attempt timed out", severity: NOTIFICATION_ERROR });
    }
}

function send_message(message) {
    if (ws.readyState == ws.OPEN) {
        ws.send(JSON.stringify(message));
    }
}

function close_notification(item) {
    item.style.opacity = "0%";
    setTimeout(() => {
        if (item.parentNode == notifications_dom) {
            notifications_dom.removeChild(item);
        }
    }, 400);
}

function new_notification(infos) {
    let notification = document.createElement("div");
    let severity = "notification-info";
    switch (infos.severity) {
        case NOTIFICATION_INFO:
            severity = "notification-info";
            break;
        case NOTIFICATION_WARN:
            severity = "notification-warn";
            break;
        case NOTIFICATION_ERROR:
            severity = "notification-error";
            break;
        default:
            break;
    }
    notification.classList.add("notification", severity);
    notification.innerHTML = "<div class='notification-top'><div class='notification-header'></div><button class='notification-close-button' onclick='close_notification(this.parentNode.parentNode);'>x</button></div><div class='notification-content'></div>";
    notification.children[0].firstChild.innerText = infos.header;
    notification.children[1].innerText = infos.content;
    notifications_dom.appendChild(notification);

    setTimeout(() => {
        close_notification(notification);
    }, 3000);
}

function update_state() {
    switch (ws.readyState) {
        case ws.CLOSED:
            set_state(STATE_CLOSED);
            break;
        case ws.CLOSING:
            set_state(STATE_CLOSING);
            break;
        case ws.CONNECTING:
            set_state(STATE_CONNECTING);
            break;
        case ws.OPEN:
            set_state(STATE_OPEN);
            break;
        default:
            break;
    }
}

window.onload = () => {
    update_state();
    setInterval(() => {
        update_state();
    }, 5000);
}

function clamp(x, a, b) {
    return Math.min(Math.max(x, a), b);
}

function send_order(forback_in, rotation_in) {
    let forback = forback_in;
    let rotation = rotation_in;
    if (isNaN(parseFloat(forback_in))) {
        forback = 0;
    }
    if (isNaN(parseFloat(rotation_in))) {
        rotation = 0;
    }
    let order = {
        "type": "order",
        "position": {
            "forback": forback,
            "rotation": rotation
        }
    };
    
    send_message(order);
}

function joystick_callback(x_in, y_in) {
    let x = clamp(x_in, -1, 1);
    let y = clamp(y_in, -1, 1);
    x = Math.sign(x)*Math.sqrt(Math.abs(x));

    send_order(y, x**3);
}

function toggle_mode_autonomous(b) {
    order = {
        "type": "option",
        "option": "mode",
        "data": {
            "mode": undefined
        }
    }
    if (b) {
        joystick.enabled = false;
        order["data"]["mode"] = "ia";
    } else {
        joystick.enabled = true;
        order["data"]["mode"] = "manual";
    }
    send_message(order)
}

function retry_connection() {
    if (ws.readyState == ws.OPEN) {
        return;
    }
    create_websocket();
    set_state(STATE_CONNECTING);
}

function set_state(new_state) {
    if (state == new_state) {
        return;
    }
    switch (new_state) {
        case STATE_OPEN:
            state_dom.innerText = "Connected";
            state_dom.classList = ["state-info"]
            break;
        case STATE_CONNECTING:
            state_dom.innerText = "Connecting to socket";
            state_dom.classList = ["state-warning"]
            break;
        case STATE_CLOSING:
            state_dom.innerText = "Closing connection";
            state_dom.classList = ["state-warning"]
            break;
        case STATE_CLOSED:
            state_dom.innerHTML = "No connection <button onclick='retry_connection()' class='retry_button'>Retry</button>";
            state_dom.classList = ["state-error"]
            break;
    }
    state = new_state;
}