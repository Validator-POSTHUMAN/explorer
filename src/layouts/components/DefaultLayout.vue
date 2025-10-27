<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { computed, ref } from 'vue';

// Components
import NavbarSearch from '@/layouts/components/NavbarSearch.vue';
import ChainProfile from '@/layouts/components/ChainProfile.vue';

import { useDashboard } from '@/stores/useDashboard';
import { useBlockchain, useWalletStore } from '@/stores';

import NavBarWallet from './NavBarWallet.vue';
import type {
  NavGroup,
  NavLink,
  NavSectionTitle,
  VerticalNavItems,
} from '../types';
import { useRoute } from 'vue-router';
import Socials from '@/layouts/components/Socials.vue';

const route = useRoute();

const walletStore = useWalletStore();
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

function isNavGroup(nav: VerticalNavItems | any): nav is NavGroup {
  return (<NavGroup>nav).children !== undefined;
}
function isNavLink(nav: VerticalNavItems | any): nav is NavLink {
  return (<NavLink>nav).to !== undefined;
}
function selected(route: any, nav: NavLink) {
  const b =
    route.path === nav.to?.path ||
    (route.path.startsWith(nav.to?.path) &&
      nav.title.indexOf('dashboard') === -1);
  return b;
}

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
  <div
    class="relative min-h-screen w-full flex flex-col overflow-x-hidden"
    style="
      background: linear-gradient(
          to bottom,
          rgba(0, 0, 0, 1),
          rgba(0, 0, 0, 0.2)
        ),
        url('./public/images/main-bg.jpg') center 50vh / cover no-repeat;
      background-attachment: fixed;
    "
  >
    <!-- sidebar -->
    <div
      class="w-full fixed z-50 min-h-screen bg-menu-button/70"
      @click="sidebarShow = false"
      :class="{
        block: sidebarShow,
        hidden: !sidebarShow,
      }"
    >
      <div
        @click.stop
        class="w-3/4 h-screen left-0 top-0 bottom-0 overflow-auto bg-almost-black border-r rounded-r-2xl border-almost-black dark:border-[#171718]"
      >
        <NavBarWallet :isSidebar="true" />
        <div v-for="(item, index) of blockchain.computedChainMenu" :key="index">
          <div
            v-if="isNavGroup(item)"
            :tabindex="index"
            class="collapse"
            :class="{
              'collapse-arrow': item?.children?.length > 0,
              'collapse-open': index === 0 && sidebarOpen,
              'collapse-close': index === 0 && !sidebarOpen,
            }"
          >
            <input
              type="checkbox"
              class="cursor-pointer !h-10 block"
              @click="changeOpen(index)"
            />
            <div class="collapse-content w-full py-0 px-6">
              <div class="menu w-auto p-0 mb-1">
                <RouterLink
                  class="flex p-0 items-center"
                  :to="{ path: '/' }"
                  active-class="!text-header-text"
                  exact-active-class="!text-header-text"
                >
                  <div
                    class="header-16-medium tracking-wide capitalize text-[#C9C9C9] dark:text-gray-300 py-2 px-4 rounded-full"
                    :class="{
                      '!text-header-text shadow-[0_3px_2px_-1px_rgba(113,255,184,0.4)]':
                        route.path === '/',
                    }"
                  >
                    _Home
                  </div>
                </RouterLink>
              </div>

              <div
                v-for="(el, key) of item?.children?.filter(
                  (ch) => ch.title !== 'module.uptime'
                )"
                class="menu w-full p-0 mb-1 rounded-full"
              >
                <RouterLink
                  v-if="isNavLink(el)"
                  @click="sidebarShow = false"
                  class="flex items-center"
                  :to="el.to"
                >
                  <div
                    class="header-16-medium tracking-wide capitalize text-[#C9C9C9] dark:text-gray-300 py-2 px-4 rounded-full"
                    :class="{
                      '!text-header-text shadow-[0_3px_2px_-1px_rgba(113,255,184,0.4)]':
                        selected($route, el),
                    }"
                  >
                    {{
                      item?.title === 'Favorite'
                        ? `_${el?.title}`
                        : `_${$t(el?.title)}`
                    }}
                  </div>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
        <div class="px-2">
          <Socials :list="socials" className="flex" />
        </div>
      </div>
    </div>
    <header
      class="w-full flex justify-between border-y border-addition mt-[26px] mb-5 max-h-[52px]"
    >
      <RouterLink to="/" class="hidden xl:flex items-center mx-8">
        <img class="w-full max-w-32 h-auto" src="../../assets/logo.svg" />
      </RouterLink>
      <div
        class="text-2xl text-white px-5 my-3 cursor-pointer xl:!hidden"
        @click="sidebarShow = true"
      >
        <Icon icon="mdi-menu" />
      </div>
      <ChainProfile />
      <div class="flex items-center xl:w-full xl:justify-between">
        <div
          v-for="(item, index) of blockchain.computedChainMenu.filter(
            (item) => isNavGroup(item) && !item.badgeContent
          )"
          :key="index"
        >
          <div
            v-if="isNavGroup(item)"
            :tabindex="index"
            class="h-full"
            :class="{
              'collapse-arrow': item?.children?.length > 0,
              'collapse-open': index === 0 && sidebarOpen,
              'collapse-close': index === 0 && !sidebarOpen,
            }"
          >
            <div class="collapse-content flex w-full h-full !p-0">
              <div
                v-for="(el, key) of item?.children.filter(
                  (item) =>
                    isNavLink(item) && item?.to.path !== '/cosmos/uptime'
                )"
                class="relative h-full pl-8 pr-10 pt-4 pb-2 hidden xl:block before:hover:border-x before:hover:bg-menu-button-hover before:active:bg-menu-button-active before:scale-y-105 before:block before:absolute before:inset-0 before:-skew-x-[33deg] before:border-r-2 before:border-addition"
                :class="{
                  'before:bg-menu-button-active': selected($route, el),
                }"
              >
                <RouterLink
                  v-if="isNavLink(el)"
                  class="relative z-10"
                  :to="el.to"
                >
                  <div class="header-16 tracking-wide capitalize text-white">
                    {{ `_${$t(el?.title)}` }}
                  </div>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
        <div
          class="flex items-center xl:w-full"
          :class="{
            'xl:justify-between': !!walletStore?.currentAddress,
            'xl:justify-end': !walletStore?.currentAddress,
          }"
        >
          <NavbarSearch
            v-if="!!walletStore?.currentAddress"
            class="hidden md:!inline-block xl:ml-4 pr-2"
          />
          <NavBarWallet />
        </div>
      </div>
    </header>

    <!-- 👉 Pages -->
    <div class="flex flex-col grow px-3 xl:p-0 mt-4">
      <RouterView v-slot="{ Component }" class="grow">
        <Transition mode="out-in">
          <Component :is="Component" />
        </Transition>
      </RouterView>
    </div>
  </div>
</template>

<style lang="scss">
.modal-box {
  background-color: #111113;
  border: solid 1px #3fb6a8;

  h3 {
    color: #3fb6a8;
    font-family: 'Red Hat Mono';
    text-transform: uppercase;
  }

  //  swap
  div.flex.items-center.relative.h-14.bg-gray-100.dark\:bg-\[\#232333\].rounded-tl-lg.rounded-tr-lg.mt-4 {
    border: 1px solid #686868;
    border-radius: 50px;
    overflow: hidden;

    input {
      border: none !important;
    }
  }

  div:nth-child(1) > div:nth-child(6) {
    border: 1px solid #686868;
    border-radius: 50px;
    overflow: hidden;
  }

  div.flex.items-center.justify-center.-mt-3.-mb-3 {
    margin: 0 0 24px 0;
  }

  div {
    background: #111113;
  }

  .dropdown {
    background: #111113;
    height: 100%;
    border-right: 1px solid #686868;
  }

  div.absolute.right-4.top-4.dropdown.dropdown-end.dropdown-hover {
    height: auto;
    border-right: none !important;
  }

  .btn-primary {
    font-family: 'Red Hat Mono';
    font-size: 16px;
    border-radius: 100px;
    border: 1px solid #3fb6a8;
    color: #71ffb8;
    cursor: pointer;
    background-color: rgba(104, 104, 104, 10%);
  }

  .btn-primary:hover {
    background-color: rgba(14, 255, 187, 20%);
  }

  // send, delegate, vote
  input {
    border-radius: 200px;
    border: 1px solid #686868 !important;
    border-color: #686868 !important;
  }

  select {
    border-radius: 100px;
    border-color: #686868 !important;
  }

  .input-group {
    input {
      border-top-left-radius: 100px;
      border-bottom-left-radius: 100px;
      border-color: #686868 !important;
    }

    select {
      border-top-right-radius: 100px;
      border-bottom-right-radius: 100px;
      border-color: #686868 !important;
    }
  }
}
</style>
