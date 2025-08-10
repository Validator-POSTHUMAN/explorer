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
    openQR: { type: Function },
    isShort: { type: Boolean },
    isCopyHref: { type: Boolean },
});
let showCopyToast = ref(0);
async function copyAdress(address: string | undefined, isCopyHref?: boolean, href?: string) {
    if (!address) return;
    const host = window.location.origin;
    const newUrl = `${host}${href}`;
    try {
        await navigator.clipboard.writeText(isCopyHref ? newUrl : address);
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

        <div v-if="icon" @click="copyAdress(address, isCopyHref, href)"
            class="cursor-pointer flex justify-center items-center gap-2"
            :class="{ 'before:z-[1] before:absolute before:rounded-full before:bg-button-v2-hover before:hover:bg-button-v2 before:w-9 before:h-9': hasIconOutline }">
            <Icon class="relative z-10" icon="bx:copy" :width="size" :height="size" />
        </div>

        <div v-if="openQR" class="cursor-pointer flex justify-center items-center gap-2"  @click="openQR(true)"
            :class="{ 'before:z-[1] before:absolute before:rounded-full before:bg-button-v2-hover before:hover:bg-button-v2 before:w-9 before:h-9': hasIconOutline }">
            <Icon class="relative z-10" icon="tabler:qrcode" :width="size" :height="size" />
        </div>
    </div>

    <div class="toast" v-show="showCopyToast === 1">
        <div
            class="relative bg-almost-black flex items-center gap-4 p-4 border border-button-text rounded text-green-text">
            <Icon @click="showCopyToast = 0" class="absolute top-0 right-0 text-addition cursor-pointer"
                icon="codex:cross" width="16" height="16" />
            <div
                class="flex justify-center items-center gap-2 before:z-[1] before:absolute before:rounded-full before:bg-[#0A2B0C] before:w-9 before:h-9">
                <Icon class="relative z-10 " icon="material-symbols:check-rounded" width="34" height="34" />
            </div>
            <div class="header-20 tracking-wide">
                <span>{{ tipMsg.msg }}</span>
            </div>
        </div>
    </div>
    <div class="toast" v-show="showCopyToast === 2">
        <div
            class="relative bg-almost-black flex items-center gap-4 p-4 border border-button-text rounded text-red-text">
            <Icon @click="showCopyToast = 0" class="absolute top-0 right-0 text-addition cursor-pointer"
                icon="codex:cross" width="16" height="16" />
            <div
                class="flex justify-center items-center gap-2 before:z-[1] before:absolute before:rounded-full before:bg-[#480D0D] before:w-9 before:h-9">
                <Icon class="relative z-10 " icon="codex:cross" width="34" height="34" />
            </div>
            <div class="header-20 tracking-wide">
                <span>{{ tipMsg.msg }}</span>
            </div>
        </div>
    </div>
</template>