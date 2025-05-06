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
const showFavoriteChains = ref(true);
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

// toggle show favorite chains
function toggleShowFavoriteChains() {
  showFavoriteChains.value = !showFavoriteChains.value;
}

</script>

<template>
  <div class="px-3 mb-5 md:mb-14">
    <div v-if="route.path !== '/'" class="flex justify-center mb-6">
      <div class="w-full md:w-auto grid grid-cols-2 gap-5 pt-0.5" :class="{
        'md:!grid-cols-1 lg:!grid-cols-1 2xl:!grid-cols-1': (showFavoriteChains ? favoriteChains : chains).length === 1,
        'md:!grid-cols-2 lg:!grid-cols-2 2xl:!grid-cols-2': (showFavoriteChains ? favoriteChains : chains).length === 2,
        'md:!grid-cols-3 lg:!grid-cols-3 2xl:!grid-cols-3': (showFavoriteChains ? favoriteChains : chains).length === 3,
        'md:!grid-cols-4 lg:!grid-cols-4 2xl:!grid-cols-4': (showFavoriteChains ? favoriteChains : chains).length === 4,
        'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-5': (showFavoriteChains ? favoriteChains : chains).length === 5,
        'md:!grid-cols-4 lg:!grid-cols-5 2xl:!grid-cols-6': (showFavoriteChains ? favoriteChains : chains).length >= 6,
      }">
        <ChainSummary v-for="(chain, index) in (showFavoriteChains ? favoriteChains : chains)" :key="index" :name="chain.chainName" />
      </div>
    </div>
    <div class="flex justify-center w-full ">
      <button
        @click="toggleShowFavoriteChains"
        class="w-full md:w-[374px] py-3.5 p header-16 text-white flex gap-4 justify-center items-center rounded-full bg-button-v2-hover/60 hover:bg-button-v2/60 border border-addition">
        <Icon v-if="showFavoriteChains" icon="ic:baseline-plus" width="24" height="24" />
        <Icon v-else icon="ic:baseline-minus" width="24" height="24" />
        <span  v-if="showFavoriteChains">{{ $t('module.add_network') }}</span>
      </button>
    </div>
  </div>
</template>