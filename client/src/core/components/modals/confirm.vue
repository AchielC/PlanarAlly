<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import Modal from "@/core/components/modals/modal.vue";

@Component({
    components: {
        Modal,
    },
})
export default class ConfirmDialog extends Vue {
    $refs!: {
        confirm: HTMLButtonElement;
        deny: HTMLButtonElement;
    };

    visible = false;
    yes = "Yes";
    no = "No";
    title = "";
    body = "";
    focus: "confirm" | "deny" = "deny";

    resolve: (ok: boolean) => void = (_ok: boolean) => {};
    reject: () => void = () => {};

    confirm(): void {
        this.resolve(true);
        this.close();
    }
    deny(): void {
        this.resolve(false);
        this.close();
    }
    close(): void {
        this.reject();
        this.visible = false;
    }
    open(title: string, yes = "yes", no = "no", focus: "confirm" | "deny" = "deny"): Promise<boolean> {
        this.focus = focus;
        this.yes = yes;
        this.no = no;
        this.title = title;

        this.visible = true;
        this.$nextTick(() => {
            if (focus === "confirm") this.$refs.confirm.focus();
            else this.$refs.deny.focus();
        });

        return new Promise((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
        });
    }
}
</script>

<template>
    <modal :visible="visible" @close="close">
        <div
            class="modal-header"
            slot="header"
            slot-scope="m"
            draggable="true"
            @dragstart="m.dragStart"
            @dragend="m.dragEnd"
        >
            {{ title }}
        </div>
        <div class="modal-body">
            <slot></slot>
            <div class="buttons">
                <button @click="confirm" ref="confirm" :class="{ focus: focus === 'confirm' }">{{ yes }}</button>
                <button @click="deny" v-if="!!no" ref="deny" :class="{ focus: focus === 'deny' }">{{ no }}</button>
            </div>
        </div>
    </modal>
</template>

<style scoped>
.modal-header {
    background-color: #ff7052;
    padding: 10px;
    font-size: 20px;
    font-weight: bold;
    cursor: move;
}

.modal-body {
    padding: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.buttons {
    align-self: flex-end;
}

button:first-of-type {
    margin-right: 10px;
}

.focus {
    color: #7c253e;
    font-weight: bold;
}
</style>
