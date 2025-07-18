<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import {
  useDashboard,
  LoadingStatus,
  type ChainConfig,
} from '@/stores/useDashboard';
import ChainSummary from '@/components/ChainSummary.vue';

import { computed, ref } from 'vue';
import { useBlockchain } from '@/stores';

const dashboard = useDashboard();

const keywords = ref('');
const chains = computed(() => {
  if (keywords.value) {
    const lowercaseKeywords = keywords.value.toLowerCase();

    return Object.values(dashboard.chains).filter(
      (x: ChainConfig) =>
        x.chainName.toLowerCase().indexOf(lowercaseKeywords) > -1 ||
        x.prettyName.toLowerCase().indexOf(lowercaseKeywords) > -1
    );
  } else {
    return Object.values(dashboard.chains);
  }
});

const chainStore = useBlockchain();
</script>
<template>
  <div class="">
    <div
      class="flex md:!flex-row flex-col items-center justify-center mb-6 mt-14 gap-2"
    >
      <img class="w-453 h-153" src="../assets/logo-big.svg" />
      <!-- <h1 class="text-3xl md:!text-6xl w-453 h-153 rajdhani-regular">
        {{ $t('pages.title') }}
      </h1> -->
    </div>
    <div class="text-center text-[#FFFFFF]">
      <p class="mb-1">
        {{ $t('pages.slogan') }}
      </p>
    </div>
    <div
      v-if="dashboard.status !== LoadingStatus.Loaded"
      class="flex justify-center"
    >
      <progress class="progress progress-info w-80 h-1"></progress>
    </div>

    <!-- <div class="text-center text-base mt-6">
      <h2 class="mb-6">{{ $t('pages.description') }}</h2>
    </div> -->

    <div class="flex items-center rounded-full bg-[#171718] mt-10">
      <input
        :placeholder="$t('pages.search_placeholder')"
        class="px-4 h-10 bg-transparent flex-1 outline-none text-base"
        v-model="keywords"
      />
      <div class="px-4 text-base hidden md:!block">
        <Icon icon="mdi:magnify" class="text-2xl text-[#686868] ml-3" />
      </div>
    </div>

    <div
      class="grid grid-cols-1 gap-4 mt-6 md:!grid-cols-3 lg:!grid-cols-4 2xl:!grid-cols-5"
    >
      <ChainSummary
        v-for="(chain, index) in chains"
        :key="index"
        :name="chain.chainName"
      />
    </div>
  </div>
</template>

<style scoped>
.logo path {
  fill: #242424;
}
</style>
