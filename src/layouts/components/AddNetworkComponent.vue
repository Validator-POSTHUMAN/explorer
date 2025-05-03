<script lang="ts" setup>
import ChainSummary from '@/components/ChainSummary.vue';
import {
  useDashboard,
  LoadingStatus,
  type ChainConfig,
} from '@/stores/useDashboard';
import { Icon } from '@iconify/vue';
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router'

const route = useRoute()
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
const favoriteChains = computed(() => chains.value.filter(chain => dashboard?.favoriteMap?.[chain.chainName]));

</script>

<template>
  <div class="px-3 mb-5 md:mb-14">
    <div v-if="route.path !== '/'" class="flex justify-center mb-6">
      <div class="w-full md:w-auto grid grid-cols-2 gap-5 pt-0.5" :class="{
        'md:!grid-cols-1 lg:!grid-cols-1 2xl:!grid-cols-1': favoriteChains.length === 1,
        'md:!grid-cols-2 lg:!grid-cols-2 2xl:!grid-cols-2': favoriteChains.length === 2,
        'md:!grid-cols-3 lg:!grid-cols-3 2xl:!grid-cols-3': favoriteChains.length === 3,
        'md:!grid-cols-4 lg:!grid-cols-4 2xl:!grid-cols-4': favoriteChains.length === 4,
        'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-5': favoriteChains.length === 5,
        'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-6': favoriteChains.length >= 6,

      }">
        <ChainSummary v-for="(chain, index) in favoriteChains" :key="index" :name="chain.chainName" />
      </div>
    </div>
    <div class="flex justify-center w-full ">
      <button
        class="w-full md:w-[374px] py-3.5 p header-16 text-white flex gap-4 justify-center items-center rounded-full bg-button-v2-hover/60 hover:bg-button-v2/60 border border-addition">
        <Icon icon="ic:baseline-plus" width="24" height="24" />
        <span>{{ $t('module.add_network') }}</span>
      </button>
    </div>
  </div>
</template>