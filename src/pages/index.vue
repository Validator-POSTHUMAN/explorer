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
const dashboardStore = useDashboard();

const favoriteChains = computed(() => {
  return chains.value.filter((i) => dashboardStore.favoriteMap[i.chainName]);
});
</script>
<template>
  <div
    class="flex md:!flex-row flex-col items-center justify-center mt-20 gap-2"
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

  <div class="flex justify-center mt-5">
    <div class="join">
      <input 
      type="text"
      :placeholder="$t('pages.search_placeholder')"
      class="cosmos-navbar text-base pl-4 rounded-full w-[60rem] h-12 join-item"
      />
      <button class="btn join-item cosmos-styles rounded-r-full">
        <Icon icon="mdi:magnify" class="text-2xl"/>
      </button>
    </div>
    <!-- <div class="absolute px-4 text-base hidden md:!block ml-[59rem] mt-2">
      <Icon icon="mdi:magnify" class="text-2xl text-[#686868]" />
    </div> -->
  </div>

  <div class="flex flex-wrap justify-center gap-4 mt-6">
    <ChainSummary
      v-for="(chain, index) in favoriteChains"
      :key="index"
      :name="chain.chainName"
    />
  </div>
</template>

<style scoped>
.logo path {
  fill: #242424;
}
</style>
