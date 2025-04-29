<script lang="ts" setup>
import { Icon } from '@iconify/vue';
</script>

<template>
    <div class="flex justify-center w-full mb-14">
        <button
          class="w-full md:w-[374px] mt-10 py-3.5 p header-16 text-white flex gap-4 justify-center items-center rounded-full bg-button-v2-hover hover:bg-button-v2 border border-addition">
          <Icon icon="ic:baseline-plus" width="24" height="24" />
          <span>{{ $t('module.add_network') }}</span>
        </button>
      </div>
</template>