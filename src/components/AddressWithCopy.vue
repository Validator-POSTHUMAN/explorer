<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { ref, computed } from 'vue';

defineProps({
    address: { type: String },
    href: { type: String },
    icon: { type: Boolean },
    styles: { type: String },
    size: {
        type: Number,
        default: 24
    },
    hasIconOutline: { type: Boolean },
    hasQr: { type: Boolean },
    isShort: { type: Boolean },
});

let showCopyToast = ref(0);
async function copyAdress(address: string | undefined) {
    if (!address) return;
    try {
        await navigator.clipboard.writeText(address);
        showCopyToast.value = 1;
        setTimeout(() => {
            showCopyToast.value = 0;
        }, 1000);
    } catch (err) {
        showCopyToast.value = 2;
        setTimeout(() => {
            showCopyToast.value = 0;
        }, 1000);
    }
}
const tipMsg = computed(() => {
    return showCopyToast.value === 2
        ? { class: 'error', msg: 'Copy Error!' }
        : { class: 'success', msg: 'Copy Success!' };
});
</script>

<template>
    <div class="hidden md:flex header-20-medium text-white tracking-wide gap-3 truncate" :class="styles">
        <RouterLink v-if="address && href" class="no-underline max-w-[566px] truncate" :to="href"
            @click="!icon || !href && copyAdress(address)">
            <span class="max-w-[566px] truncate">{{
                !address ? 'Not Connected' : isShort ? `${address.slice(0, 12)}...${address.slice(-6)}` : address
                }}</span>
        </RouterLink>
        <span v-if="address && !href" class="max-w-[566px] truncate">{{
            `${address.slice(0, 12)}...${address.slice(-6)}` || 'Not Connected'
            }}</span>

        <div v-if="icon" @click="copyAdress(address)" class="cursor-pointer flex justify-center items-center gap-2"
            :class="{ 'before:z-[1] before:absolute before:rounded-full before:bg-button-v2-hover before:hover:bg-button-v2 before:w-9 before:h-9': hasIconOutline }">
            <Icon class="relative z-10" icon="bx:copy" :width="size" :height="size" />
        </div>
        <div v-if="hasQr" @click="copyAdress(address)" class="cursor-pointer flex justify-center items-center gap-2"
            :class="{ 'before:z-[1] before:absolute before:rounded-full before:bg-button-v2-hover before:hover:bg-button-v2 before:w-9 before:h-9': hasIconOutline }">
            <Icon class="relative z-10" icon="tabler:qrcode" :width="size" :height="size" />
        </div>
    </div>

    <div class="toast" v-show="showCopyToast === 1">
        <div class="alert alert-success">
            <div class="text-xs md:!text-sm">
                <span>{{ tipMsg.msg }}</span>
            </div>
        </div>
    </div>
    <div class="toast" v-show="showCopyToast === 2">
        <div class="alert alert-error">
            <div class="text-xs md:!text-sm">
                <span>{{ tipMsg.msg }}</span>
            </div>
        </div>
    </div>
</template>