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
import { RouterLink } from 'vue-router';

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
    class="min-h-screen min-w-full bg-[url('src/assets/images/background/cosmos-background.png')] bg-cover bg-center bg-fixed bg-[#0D0D0E]"
  >
    <!-- header -->
    <div class="w-full sticky top-0 z-50 py-5">
      <div class="border-b border-t border-y-[#686868] bg-black relative">
        <div class="flex h-12">
          <NavbarLinks />
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
      <div class="flex flex-row gap-[7.6rem] text-[#686868] ml-20 mt-2">
        <p>You explore:</p>
        <p class="capitalize">
          {{ blockchain.current?.chainName }}
        </p>
      </div>
    </div>
    <!-- 👉 Pages -->
    <RouterView v-slot="{ Component }">
      <Transition mode="out-in">
        <Component :is="Component" />
      </Transition>
    </RouterView>
    <div class="flex justify-center mt-20">
      <button
        class="btn cosmos-styles rounded-full w-[23rem] h-12 text-center cursor-pointer"
      >
        <div class="flex flex-row justify-center gap-2">
          Add Favorite Networks
        </div>
      </button>
    </div>
    <newFooter />
  </div>
</template>
