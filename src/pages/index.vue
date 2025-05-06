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


const socials = [
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
  // {
  //   name: 'telegram',
  //   icon: 'mdi:telegram',
  //   href: 'https://t.me/Crypto_Base_Chat',
  // },
];
</script>
<template>
  <div class="">
    <div class="flex md:!flex-row flex-col items-center justify-center mt-0 md:mt-32 gap-2">
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
      <SearchMain />
    </div>

    <div class="flex justify-center">
      <div class="w-full md:w-auto grid grid-cols-2 gap-5 mt-12 pt-0.5" :class="{
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
  </div>

  <Socials :list="socials" />

</template>

<style scoped>
.logo path {
  fill: #242424;
}
</style>
