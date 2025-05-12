<script lang="ts" setup>
import { Icon } from '@iconify/vue';
import { computed, ref } from 'vue';

// Components
import newFooter from '@/layouts/components/NavFooter.vue';
import NavbarThemeSwitcher from '@/layouts/components/NavbarThemeSwitcher.vue';
import NavbarSearch from '@/layouts/components/NavbarSearch.vue';
import ChainProfile from '@/layouts/components/ChainProfile.vue';

import { useDashboard } from '@/stores/useDashboard';
import { useBlockchain, useWalletStore } from '@/stores';

import NavBarI18n from './NavBarI18n.vue';
import NavBarWallet from './NavBarWallet.vue';
import type {
  NavGroup,
  NavLink,
  NavSectionTitle,
  VerticalNavItems,
} from '../types';
import AddNetworkComponent from './AddNetworkComponent.vue';
import { useRoute } from 'vue-router'

const route = useRoute()

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
const showNawSearch = ref(false);

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

const shouldShow = computed(() => route.path === '/' || /^\/[^/]+$/.test(route.path));

</script>

<template>
  <div class="relative min-h-screen w-full flex flex-col overflow-x-hidden" style="background: linear-gradient(to bottom, rgba(0, 0, 0, 1), rgba(0, 0, 0, 0.2)),
        url('./public/images/main-bg.png') center 50vh/cover no-repeat;
        background-attachment: fixed;
        ">
    <!-- sidebar -->
    <div
      class="w-64 fixed z-50 left-0 top-0 bottom-0 overflow-auto bg-[#171718] border-r border-[#171718] dark:border-[#171718]"
      :class="{ block: sidebarShow, 'hidden': !sidebarShow }">
      <div class="flex justify-center mt-1 py-4 mb-1">
        <RouterLink to="/" class="flex items-center">
          <img class="w-157 h-53" src="../../assets/logo.svg" />
        </RouterLink>
        <div class="pl-4 cursor-pointer xl:!hidden" @click="sidebarShow = false">
          <Icon icon="mdi-close" class="text-2xl" />
        </div>
      </div>
      <div v-for="(item, index) of blockchain.computedChainMenu" :key="index">
        <div v-if="isNavGroup(item)" :tabindex="index" class="collapse" :class="{
          'collapse-arrow': item?.children?.length > 0,
          'collapse-open': index === 0 && sidebarOpen,
          'collapse-close': index === 0 && !sidebarOpen,
        }">
          <input type="checkbox" class="cursor-pointer !h-10 block" @click="changeOpen(index)" />
          <div
            class="collapse-title !py-0 px-4 flex items-center cursor-pointer hover:bg-gray-100 dark:hover:bg-[#535353]">
            <Icon v-if="item?.icon?.icon" :icon="item?.icon?.icon" class="text-xl mr-2" :class="{
              'text-yellow-500': item?.title === 'Favorite',
              'text-gray-500': item?.title !== 'Favorite',
            }" />
            <img v-if="item?.icon?.image" :src="item?.icon?.image" class="w-6 h-6 rounded-full mr-3" />
            <div class="text-base capitalize flex-1 text-[#FFFFFF] dark:text-[#FFFFFF] whitespace-nowrap">
              {{ item?.title }}
            </div>
            <div v-if="item?.badgeContent" class="mr-6 badge badge-sm text-white border-none" :class="item?.badgeClass">
              {{ item?.badgeContent }}
            </div>
          </div>
          <div class="collapse-content w-full !p-0">
            <div v-for="(el, key) of item?.children" class="menu bg-[#141415] w-full !p-0">
              <RouterLink v-if="isNavLink(el)" @click="sidebarShow = false"
                class="hover:bg-[#19191C] cursor-pointer px-3 py-2 flex items-center" :class="{
                  'bg-[#2B2A37]': selected($route, el),
                }" :to="el.to">
                <Icon v-if="!el?.icon?.image" icon="mdi:rhombus-medium" class="mr-2 ml-3" :class="{
                  'text-[#D9D9D9]':
                    $route.path === el?.to?.path &&
                    item?.title !== 'Favorite',
                }" />
                <img v-if="el?.icon?.image" :src="el?.icon?.image" class="w-6 h-6 rounded-full mr-3 ml-4" :class="{
                  'border border-gray-300 bg-white': selected($route, el),
                }" />
                <div class="text-base capitalize text-gray-500 dark:text-gray-300" :class="{
                  '!text-white': selected($route, el),
                }">
                  {{ item?.title === 'Favorite' ? el?.title : $t(el?.title) }}
                </div>
              </RouterLink>
            </div>
          </div>
        </div>

        <RouterLink v-if="isNavLink(item)" :to="item?.to" @click="sidebarShow = false"
          class="cursor-pointer rounded-lg px-4 flex items-center py-2 hover:bg-gray-100 dark:hover:bg-[#373f59]">
          <Icon v-if="item?.icon?.icon" :icon="item?.icon?.icon" class="text-xl mr-2" :class="{
            'text-yellow-500': item?.title === 'Favorite',
            'text-gray-500': item?.title !== 'Favorite',
          }" />
          <img v-if="item?.icon?.image" :src="item?.icon?.image"
            class="w-6 h-6 rounded-full mr-3 border border-blue-100" />
          <div class="text-base capitalize flex-1 text-gray-700 dark:text-gray-200 whitespace-nowrap">
            {{ item?.title }}
          </div>
          <div v-if="item?.badgeContent" class="badge badge-sm text-white border-none" :class="item?.badgeClass">
            {{ item?.badgeContent }}
          </div>
        </RouterLink>
        <div v-if="isNavTitle(item)" class="px-4 text-sm text-gray-400 pb-2 uppercase">
          {{ item?.heading }}
        </div>
      </div>
      <div class="px-2">
        <div class="px-4 text-sm pt-2 text-gray-400 pb-2 uppercase">Tools</div>
        <RouterLink to="/wallet/suggest"
          class="py-2 px-4 flex items-center cursor-pointer rounded-lg hover:bg-gray-100 dark:hover:bg-[#373f59]">
          <Icon icon="mdi:frequently-asked-questions" class="text-xl mr-2" />
          <div class="text-base capitalize flex-1 text-gray-600 dark:text-gray-200">
            Wallet Helper
          </div>
        </RouterLink>

        <div class="px-4 text-sm pt-2 text-gray-400 pb-2 uppercase">
          {{ $t('module.links') }}
        </div>

        <a v-for="social in socials"
          class="py-2 px-4 flex items-center cursor-pointer rounded-lg hover:bg-gray-100 dark:hover:bg-[#373f59]"
          :href="social.href" target="_blank" :key="social.name">
          <Icon :icon="social.icon" class="text-xl mr-2" width="20" height="20" />
          <span class="text-base capitalize flex-1 text-gray-600 dark:text-gray-200">{{ social.name }}</span>
        </a>

      </div>
    </div>

    <header class="w-full flex justify-between border-y border-addition mt-[26px] mb-5 max-h-[52px]">
      <RouterLink to="/" class=" hidden xl:flex items-center mx-8 min-w-32">
        <img class="w-32 h-53" src="../../assets/logo.svg" />
      </RouterLink>

      <div class="text-2xl text-white px-5 my-3 cursor-pointer xl:!hidden" @click="sidebarShow = true">
        <Icon icon="mdi-menu" />
      </div>

      <ChainProfile />

      <div class="flex items-center xl:w-full xl:justify-between">
        <div
          v-for="(item, index) of blockchain.computedChainMenu.filter(item => isNavGroup(item) && !item.badgeContent)"
          :key="index">
          <div v-if="isNavGroup(item)" :tabindex="index" class="h-full" :class="{
            'collapse-arrow': item?.children?.length > 0,
            'collapse-open': index === 0 && sidebarOpen,
            'collapse-close': index === 0 && !sidebarOpen,
          }">

            <div class="collapse-content flex w-full h-full !p-0">
              <div
                v-for="(el, key) of item?.children.filter(item => isNavLink(item) && item?.to.path !== '/cosmos/uptime')"
                class="relative h-full pl-8 pr-10 pt-4 pb-2 hidden xl:block 
                    before:hover:border-x before:hover:bg-menu-button-hover before:active:bg-menu-button-active before:scale-y-105
                    before:block before:absolute before:inset-0 before:-skew-x-[33deg] before:border-r-2 before:border-addition"
                :class="{
                  'before:bg-menu-button-active': selected($route, el),
                }">

                <RouterLink v-if="isNavLink(el)" class="relative z-10 " :to="el.to">

                  <div class="header-16 tracking-wide capitalize text-white">
                    {{ `_${$t(el?.title)}` }}
                  </div>
                </RouterLink>
              </div>
            </div>
          </div>
        </div>

        <div class="flex items-center xl:w-full" :class="{
          'xl:justify-between': !!walletStore?.currentAddress,
          'xl:justify-end': !walletStore?.currentAddress
        }">
          <!-- <div></div> -->
          <NavbarSearch v-if="!!walletStore?.currentAddress" class="hidden md:!inline-block xl:ml-4 pr-2" />
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


    <!-- <newFooter /> -->
    <!-- </div> -->
  </div>
</template>


<style lang="scss">
.modal-box {
  background-color: #111113;
  border: solid 1px #3FB6A8;

  h3 {
    color: #3FB6A8;
    font-family: "Red Hat Mono";
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

  div:nth-child(1)>div:nth-child(6) {
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
    font-family: "Red Hat Mono";
    font-size: 16px;
    border-radius: 100px;
    border: 1px solid #3FB6A8;
    color: #71FFB8;
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
