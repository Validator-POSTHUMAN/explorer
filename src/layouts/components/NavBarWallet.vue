<script setup lang="ts">
import { useBaseStore, useBlockchain, useWalletStore } from '@/stores';
import { Icon } from '@iconify/vue';
import { ref, computed } from 'vue';

const walletStore = useWalletStore();
const chainStore = useBlockchain();
const baseStore = useBaseStore();
// walletStore.$subscribe((m, s) => {
//   console.log(m, s);
// });
function walletStateChange(res: any) {
  walletStore.setConnectedWallet(res.detail?.value);
}
let showCopyToast = ref(0);
async function copyAdress(address: string) {
  try {
    await navigator.clipboard.writeText(address);
    showCopyToast.value = 1;
    setTimeout(() => {
      showCopyToast.value = 0;
    }, 1000);
  } catch (err) {
    showCopyToast.value = 2;
    setTimeout(() => {
      showCopyToast.value = 0;
    }, 1000);
  }
}
const tipMsg = computed(() => {
  return showCopyToast.value === 2
    ? { class: 'error', msg: 'Copy Error!' }
    : { class: 'success', msg: 'Copy Success!' };
});
</script>

<template>
  <div class="dropdown dropdown-hover dropdown-end">
    <label tabindex="0" class="inline-flex xl:hidden px-4 m-1 text-2xl text-white">
      <!-- :class="walletStore?.currentAddress ? 'bg-wallet-button py-1 border-2 border-[#7300FF] rounded-full' : ''" -->
      <!-- btn btn-sm btn-[#222226] hover:bg-[#2E2C50] rounded-full -->
      <Icon icon="mdi:wallet" />
    </label>

    <label tabindex="0">
      <button
        class="hidden min-w-80 w-80 h-full relative bg-wallet-button hover:bg-wallet-button-hover
                xl:flex justify-center items-center gap-5 py-3 px-3 header-20 border-y-2 border-[#7300FF]
                before:block before:absolute before:inset-0 before:border-r-2 before:border-[#7300FF] before:z-10 before:-top-0.5
                after:block after:absolute after:inset-0 after:-skew-x-[33deg] after:border-l-2 after:border-[#7300FF] after:bg-wallet-button
                after:hover:bg-wallet-button-hover after:translate-x-6 after:border-y-2 after:scale-x-125 after:-top-0.5 after:-bottom-0.5">
        <Icon icon="mdi:wallet" class="h-6 w-7 text-[#D9D9D9]" />

        <!-- <span v-if="!walletStore?.currentAddress" class="tracking-wide">{{ $t('module.connect_wallet') }}</span>
        <span v-else class="header-16"> {{ walletStore.connectedWallet?.wallet }} </span> -->

        <div class="absolute z-20 text-white flex items-center gap-5 header-20 ">
          <Icon icon="mdi:wallet" class="h-7 w-7 text-[#D9D9D9]" />
          <span v-if="!walletStore?.currentAddress" class="tracking-wide">{{ $t('module.connect_wallet') }}</span>
          <span v-else class="header-16  tracking-wide"> {{ `${walletStore?.currentAddress.slice(0,
            13)}...${walletStore?.currentAddress.slice(-4)}` }} </span>
        </div>
      </button>
    </label>

    <div tabindex="0" class="dropdown-content menu shadow p-2 bg-[#171718] rounded w-52 md:!w-64 overflow-auto z-30">
      <label v-if="!walletStore?.currentAddress" for="PingConnectWallet"
        class="btn btn-sm btn-primary hover:bg-[#2E2C50]">
        <Icon icon="mdi:wallet" /><span class="ml-1 block">Connect Wallet</span>
      </label>
      <div class="px-2 mb-1 text-[#71FFB8] font-semibold">
        {{ walletStore.connectedWallet?.wallet }}
      </div>
      <div>
        <a v-if="walletStore.currentAddress"
          class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          style="overflow-wrap: anywhere" @click="copyAdress(walletStore.currentAddress)">
          {{ walletStore.currentAddress }}
        </a>
        <div class="divider mt-1 mb-1"></div>
        <RouterLink to="/wallet/accounts">
          <div class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer">
            Accounts
          </div>
        </RouterLink>
        <RouterLink to="/wallet/portfolio">
          <div class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer">
            Portfolio
          </div>
        </RouterLink>
        <div v-if="walletStore.currentAddress" class="divider mt-1 mb-1"></div>
        <a v-if="walletStore.currentAddress"
          class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          @click="walletStore.disconnect()">Disconnect</a>
      </div>
    </div>
    <div class="toast" v-show="showCopyToast === 1">
      <div class="alert alert-success">
        <div class="text-xs md:!text-sm">
          <span>{{ tipMsg.msg }}</span>
        </div>
      </div>
    </div>
    <div class="toast" v-show="showCopyToast === 2">
      <div class="alert alert-error">
        <div class="text-xs md:!text-sm">
          <span>{{ tipMsg.msg }}</span>
        </div>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <ping-connect-wallet :chain-id="baseStore.currentChainId" :hd-path="chainStore.defaultHDPath"
      :addr-prefix="chainStore.current?.bech32Prefix || 'cosmos'" @connect="walletStateChange"
      @keplr-config="walletStore.suggestChain()" />
  </Teleport>
</template>

<style>
.ping-connect-btn,
.ping-connect-dropdown {
  display: none !important;
}
</style>
