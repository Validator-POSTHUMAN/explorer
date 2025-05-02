<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue';

const router = useRouter()

function goBack() {
  router.back()
}
</script>

<template>
    <!-- hover:shadow-[0_0_5px_2px_rgba(255,255,255,0.3)] -->
    <button
      @click="goBack"
      class="self-start border border-addition hover:bg-menu-button-hover active:bg-menu-button-active rounded-full header-16-medium py-1.5 pl-3 pr-5 text-white flex gap-1">
      <Icon icon="mdi-light:chevron-left" width="24" height="24" />
      <span>{{$t('pages.back')}}</span>
    </button>
</template>