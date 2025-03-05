<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { ref } from 'vue';

// Components
import newFooter from '@/layouts/components/NavFooter.vue';
import NavbarThemeSwitcher from '@/layouts/components/NavbarThemeSwitcher.vue';
import NavbarSearch from '@/layouts/components/NavbarSearch.vue';
import ChainProfile from '@/layouts/components/ChainProfile.vue';
import NavbarLinks from './NavbarLinks.vue';

import { useDashboard } from '@/stores/useDashboard';
import { useBlockchain } from '@/stores';

import NavBarI18n from './NavBarI18n.vue';
import NavBarWallet from './NavBarWallet.vue';
import type {
  NavGroup,
  NavLink,
  NavSectionTitle,
  VerticalNavItems,
} from '../types';

const dashboard = useDashboard();
dashboard.initial();
const blockchain = useBlockchain();
blockchain.randomSetupEndpoint();

const current = ref(''); // the current chain
const temp = ref('');
blockchain.$subscribe((m, s) => {
  if (current.value === s.chainName && temp.value != s.endpoint.address) {
    temp.value = s.endpoint.address;
    blockchain.initial();
  }
  if (current.value != s.chainName) {
    current.value = s.chainName;
    blockchain.randomSetupEndpoint();
  }
});

const sidebarShow = ref(false);
const sidebarOpen = ref(true);

const changeOpen = (index: Number) => {
  if (index === 0) {
    sidebarOpen.value = !sidebarOpen.value;
  }
};
const showDiscord = window.location.host.search('ping.pub') > -1;

function isNavGroup(nav: VerticalNavItems | any): nav is NavGroup {
  return (<NavGroup>nav).children !== undefined;
}
function isNavLink(nav: VerticalNavItems | any): nav is NavLink {
  return (<NavLink>nav).to !== undefined;
}
function isNavTitle(nav: VerticalNavItems | any): nav is NavSectionTitle {
  return (<NavSectionTitle>nav).heading !== undefined;
}
function selected(route: any, nav: NavLink) {
  const b =
    route.path === nav.to?.path ||
    (route.path.startsWith(nav.to?.path) &&
      nav.title.indexOf('dashboard') === -1);
  return b;
}
</script>

<template>
  <div
    class="w-screen h-screen bg-[url('src/assets/images/background/cosmos-background.png')] bg-cover bg-center bg-[#0D0D0E]"
  >
    <!-- header -->
    <div class="w-full sticky top-0 z-50 py-5">
      <div class="border-b border-t border-y-[#686868] bg-black">
        <div class="flex h-12">
          <svg
            class="-mr-[1rem]"
            width="174"
            height="74"
            viewBox="0 0 174 74"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2 0.5H1.03311L1.59199 1.28901L52.592 73.289L52.7414 73.5H53H120.695H120.954L121.104 73.2883L171.909 1.28827L172.465 0.5H171.5H2Z"
              fill="black"
              stroke="#686868"
            />
          </svg>
          <NavbarLinks/>
          <!-- <ChainProfile /> -->

          <!-- <NavSearchBar />-->
          <!-- <NavBarI18n class="hidden md:!inline-block" /> -->
          <!-- <NavbarThemeSwitcher class="!inline-block" /> -->
          <!-- <NavbarSearch class="!inline-block" /> -->
          <div class="ml-auto h-16 flex items-center">
            <NavBarWallet />
          </div>
        </div>
      </div>
    </div>
    <!-- <button class="btn skew-x-[-50deg] transform bg-blue-500 text-white px-6 py-3">
        <span class="skew-x-[50deg] transform">Нажми меня</span>
    </button> -->
    <!-- 👉 Pages -->
    <RouterView v-slot="{ Component }">
      <Transition mode="out-in">
        <Component :is="Component" />
      </Transition>
    </RouterView>
    <div class="flex justify-center mt-20">
      <div class="border border-[#686868] hover:bg-[#242424] bg-black bg-opacity-50 rounded-full w-[23rem] h-12 text-center cursor-pointer">
        <div class="mt-3 text-white flex flex-row justify-center gap-2">
          <p class="text-2xl -mt-[0.4rem]">+</p>Add Favorite Networks
        </div>
      </div>
    </div>
    <newFooter />
  </div>
</template>
