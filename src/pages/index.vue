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
    <div class="flex md:!flex-row flex-col items-center justify-center mt-12 md:mt-32 gap-2">
      <img class="w-453 h-153" src="../assets/logo-big.svg" />
      <!-- <h1 class="text-3xl md:!text-6xl w-453 h-153 rajdhani-regular">
        {{ $t('pages.title') }}
      </h1> -->
    </div>
    <div class="text-center text-white header-20 tracking-wide">
      <p class="mb-1">
        {{ $t('pages.slogan') }}
      </p>
    </div>
    <div v-if="dashboard.status !== LoadingStatus.Loaded" class="flex justify-center">
      <progress class="progress progress-info w-80 h-1"></progress>
    </div>

    <!-- <div class="text-center text-base mt-6">
      <h2 class="mb-6">{{ $t('pages.description') }}</h2>
    </div> -->

    <div class="flex w-full justify-center">
      <div
        class="flex w-full md:w-1/2 items-center rounded-[26px] bg-transparent mt-10 border border-addition text-addition py-2 px-2">
        <input :placeholder="$t('pages.search_placeholder')"
          class="md:px-4 min-h-6 md:h-10 bg-transparent flex-1 outline-none text-xs md:text-xl placeholder:text-addition focus:text-white " v-model="keywords" />
        <div class="md:px-4 pr-2 md:!block order-first md:order-last">
          <Icon icon="icon-park-outline:search" width="20" height="20" class="ml-3" />
        </div>
      </div>
    </div>

    <div class="flex justify-center">
      <div class="w-full md:w-auto grid grid-cols-2 gap-5 mt-12 pt-0.5"
        :class="{
          'md:!grid-cols-1 lg:!grid-cols-1 2xl:!grid-cols-1': chains.length === 1,
          'md:!grid-cols-2 lg:!grid-cols-2 2xl:!grid-cols-2': chains.length === 2,
          'md:!grid-cols-3 lg:!grid-cols-3 2xl:!grid-cols-3': chains.length === 3,
          'md:!grid-cols-4 lg:!grid-cols-4 2xl:!grid-cols-4': chains.length === 4,
          'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-5': chains.length === 5,
          'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-6': chains.length >= 6,

        }">
        <ChainSummary v-for="(chain, index) in chains" :key="index" :name="chain.chainName" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.logo path {
  fill: #242424;
}
</style>
