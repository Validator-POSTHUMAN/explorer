<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { ref } from 'vue';

// Components
import newFooter from '@/layouts/components/NavFooter.vue';
import NavbarThemeSwitcher from '@/layouts/components/NavbarThemeSwitcher.vue';
import NavbarSearch from '@/layouts/components/NavbarSearch.vue';
import ChainProfile from '@/layouts/components/ChainProfile.vue';

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
      <div class="border-b border-t border-y-[#686868]">
        <div class="flex">
          <div class="flex flex-row-reverse">
            <div class="order-1">
              <svg
                width="174"
                height="74"
                viewBox="0 0 174 74"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M2 0.5H1.03311L1.59199 1.28901L52.592 73.289L52.7414 73.5H53H120.695H120.954L121.104 73.2883L171.909 1.28827L172.465 0.5H171.5H2Z"
                  fill="#010101"
                  stroke="#686868"
                />
              </svg>
            </div>
            <div class="">
              <svg
                width="219"
                height="51"
                viewBox="0 0 219 51"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M1 50.5L36.5 0.5H217.5L182.5 50.5H1Z"
                  fill="#010101"
                  stroke="#686868"
                />
                <text
                  x="50"
                  y="30"
                  font-family="Arial"
                  font-size="20"
                  fill="white"
                >
                  Привет, мир!
                </text>
              </svg>
            </div>
            <div class="">
              <svg
                width="219"
                height="51"
                viewBox="0 0 219 51"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M1 50.5L36.5 0.5H217.5L182.5 50.5H1Z"
                  fill="#010101"
                  stroke="#686868"
                />
              </svg>
            </div>
            <div class="">
              <svg
                width="219"
                height="51"
                viewBox="0 0 219 51"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M1 50.5L36.5 0.5H217.5L182.5 50.5H1Z"
                  fill="#010101"
                  stroke="#686868"
                />
              </svg>
            </div>
          </div>
          <!-- <ChainProfile /> -->

          <!-- <NavSearchBar />-->
          <!-- <NavBarI18n class="hidden md:!inline-block" /> -->
          <!-- <NavbarThemeSwitcher class="!inline-block" /> -->
          <!-- <NavbarSearch class="!inline-block" /> -->
          <div class="ml-auto">
            <NavBarWallet />
          </div>
        </div>
      </div>
    </div>

    <!-- 👉 Pages -->
    <div style="min-height: calc(100vh - 180px)">
      <RouterView v-slot="{ Component }">
        <Transition mode="out-in">
          <Component :is="Component" />
        </Transition>
      </RouterView>
    </div>
    <newFooter />
  </div>
</template>
