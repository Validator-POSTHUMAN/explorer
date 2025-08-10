<script lang="ts" setup>
defineProps({
    value: { type: Number },
    size: {
        type: Number || String,
        default: 90,
    }
});
</script>

<template>
    <div>
        <div class="relative rounded overflow-hidden flex items-center justify-center text-[#3FB6A8]">
            <div class="absolute top-0 left-0 bottom-0 right-0 bg-almost-black rounded-full m-2"></div>

            <div class="radial-progress
              before:bg-[#17171C] before:outline before:outline-addition-1"
                :style="`--value:${value ? +value : 0}; --size:${size}px;`" :ariaValuenow="value ? +value : 0"
                role="progressbar">
                <slot />
            </div>
            <div :style="{ margin: `${size / 10}px` }"
                class="absolute top-0 left-0 bottom-0 right-0 border border-addition-1 rounded-full shadow-[0_0_2px_2px_rgba(0,0,0,0.6)]">
            </div>
        </div>
    </div>
</template>