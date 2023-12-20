class DragSlide {
    constructor(dom) {
        this.root_dom = dom;
        this.label_dom = dom.children[0];
        this.dragging_dom = dom.children[1];
        this.value_dom = dom.children[1].children[0];

        this.drag_begin = {x: 0, y: 0};
        this.value = 0;
        this.background_value = 0;
        this.background_value_begin = 0;
        this.dragging = false;
        this.value_dom.innerText = this.value;
        this.dragging_id = undefined;
        this.callback = ()=>{};

        this.enabled = true;

        this.dragging_dom.addEventListener("pointerdown", this.pointerdown.bind(this), true);
        document.addEventListener("pointermove", this.pointermove.bind(this), true);
        document.addEventListener("pointerup", this.pointerup.bind(this), true);
    }

    pointerdown(e) {
        this.dragging_dom.setPointerCapture(e.pointerId);
        this.drag_begin.x = e.x;
        this.drag_begin.y = e.y;
        this.background_value_begin = this.background_value;
        this.dragging = true;
        this.dragging_id = e.pointerId;
    }
    
    pointermove(e) {
        if (e.pointerId != this.dragging_id) {
            return;
        }
        if (this.dragging && this.enabled) {
            this.set_background_value(-(e.x - this.drag_begin.x));
            this.dragging_dom.style.backgroundPosition = -this.background_value + "px 0px";
            this.value_dom.innerText = this.display(this.value);
        }
    }

    display(value) {
        return Math.round(value*10)/10
    }

    pointerup(e) {
        if (e.pointerId != this.dragging_id) {
            return;
        }
        this.dragging = false;
        this.dragging_dom.releasePointerCapture(e.pointerId);
        this.callback(this.value);
    }

    transform_value(value) {
        return 0.01*value;
    }

    transform_value_inverse(value) {
        return 100*value;
    }

    set_value(value) {
        this.set_background_value(this.transform_value_inverse(value));
    }

    set_background_value(value) {
        this.background_value = this.background_value_begin + value;
        this.value = this.transform_value(this.background_value);
        this.background_value = this.transform_value_inverse(this.value);
        this.dragging_dom.style.backgroundPosition = -this.background_value + "px 0px";
        this.value_dom.innerText = this.display(this.value);
    }
}


document.ontouchmove = (e) => {
    e.preventDefault();
}