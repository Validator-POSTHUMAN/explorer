<script lang="ts" setup>
defineProps({
    value: { type: Number },
});
</script>

<template>
    <span>
        <div class="relative rounded overflow-hidden flex items-center justify-center mr-2 text-[#3FB6A8]">
            <div class="absolute top-0 left-0 bottom-0 right-0 bg-almost-black rounded-full m-2"></div>

            <div class="radial-progress
              before:bg-[#17171C] before:outline before:outline-addition-1" :style="`--value:${value}; --size:90px;`"
                :ariaValuenow="value" role="progressbar">
                <slot />
            </div>
            <div
                class="absolute top-0 left-0 bottom-0 right-0 border border-addition-1 rounded-full m-[9px] shadow-[0_0_2px_2px_rgba(0,0,0,0.6)]">
            </div>
        </div>
    </span>
</template>