<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import {
  useDashboard,
  LoadingStatus,
  type ChainConfig,
} from '@/stores/useDashboard';
import ChainSummary from '@/components/ChainSummary.vue';
import SearchMain from '@/layouts/components/SearchMain.vue';
import { computed, ref } from 'vue';
import { useBlockchain } from '@/stores';
import Socials from '@/layouts/components/Socials.vue';
import AddNetworkComponent from '../layouts/components/AddNetworkComponent.vue';

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

const favoriteChains = computed(() =>
  chains.value.filter((chain) => dashboard?.favoriteMap?.[chain.chainName])
);

const socials = [
  {
    name: 'telegram',
    icon: 'ic:baseline-telegram',
    href: 'https://t.me/Crypto_Base_Chat',
  },
  {
    name: 'twitter',
    icon: 'prime:twitter',
    href: 'https://twitter.com/POSTHUMAN_DVS',
  },
  {
    name: 'discord',
    icon: 'ic:baseline-discord',
    href: 'https://discord.gg/csWJMCjQHh',
  },
];
</script>
<template>
  <div class="">
    <div
      class="flex md:!flex-row flex-col items-center justify-center mt-0 md:mt-32 gap-2"
    >
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
    <div
      v-if="dashboard.status !== LoadingStatus.Loaded"
      class="flex justify-center"
    >
      <progress class="progress progress-info w-80 h-1"></progress>
    </div>

    <!-- <div class="text-center text-base mt-6">
      <h2 class="mb-6">{{ $t('pages.description') }}</h2>
    </div> -->

    <SearchMain />
  </div>
  <AddNetworkComponent />

  <Socials :list="socials" className="hidden" />
</template>

<style scoped>
.logo path {
  fill: #242424;
}
</style>
