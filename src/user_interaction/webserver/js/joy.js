class Joystick {
    constructor(dom_element, callback) {
        this.container = dom_element;
        this.knob = dom_element.children[0];
        this.x = 0;
        this.y = 0;
        this.max_distance = 100;
        this.min_distance = 30;
        this.dragging = false;
        this.enabled = true;
        this.dragging_id = undefined;
        this.callback = callback;

        document.addEventListener("pointermove", this.pointeremove.bind(this), false);
        this.container.addEventListener("pointerdown", this.pointerdown.bind(this), false);
        document.addEventListener("pointerup", this.pointerup.bind(this), false);
    }

    pointerdown(e) {
        this.dragging = true;
        this.dragging_id = e.pointerId;
    }

    pointeremove(e) {
        if (e.pointerId != this.dragging_id) {
            return;
        }
        e.preventDefault();
        if (this.dragging && this.enabled) {
            let container_rect = this.container.getBoundingClientRect();
            // let knob_rect = this.knob.getBoundingClientRect();

            let center_x = container_rect.x + container_rect.width/2;
            let center_y = container_rect.y + container_rect.height/2;

            let dx = e.x-center_x;
            let dy = e.y-center_y;
            let norm = Math.sqrt(dx*dx+dy*dy);
            let new_norm = Math.min(norm, this.max_distance);
            if (norm < this.min_distance) {
                new_norm = 0;
            }
            if (norm > 0) {
                dx = dx*new_norm/norm;
                dy = dy*new_norm/norm;
            }
            this.knob.style.transform = "translate("+dx+"%, "+dy+"%)"
            this.x = dx/this.max_distance;
            this.y = -dy/this.max_distance;
            this.callback(this.x, this.y);
        }
    }

    go_to_zero() {
        if(!this.dragging) {
            let container_rect = this.container.getBoundingClientRect();
            let knob_rect = this.knob.getBoundingClientRect();

            let center_x = container_rect.x + container_rect.width/2;
            let center_y = container_rect.y + container_rect.height/2;

            let dx = knob_rect.x+knob_rect.width/2-center_x;
            let dy = knob_rect.y+knob_rect.height/2-center_y;
            let norm = Math.sqrt(dx*dx+dy*dy);
            let new_norm = norm*0.9;
            if (norm<=this.min_distance) {
                new_norm = 0;
            }
            if (norm>0) {
                dx = dx*new_norm/norm;
                dy = dy*new_norm/norm;
                this.knob.style.transform = "translate("+dx+"%, "+dy+"%)";
                this.x = dx/this.max_distance;
                this.y = -dy/this.max_distance;
                this.callback(this.x, this.y);
                window.requestAnimationFrame(this.go_to_zero.bind(this));
            }
        }
    }

    pointerup(e) {
        if (e.pointerId != this.dragging_id) {
            return;
        }
        this.dragging = false;
        window.requestAnimationFrame(this.go_to_zero.bind(this));
    }
}

function quasi_zero(x, epsilon) {
    if (Math.abs(x)>epsilon) {
        return x;
    }
    return 0;
}


document.ontouchmove = (e) => {
    e.preventDefault();
}