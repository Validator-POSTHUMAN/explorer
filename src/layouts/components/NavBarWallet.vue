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

function transformAddress(address: string): string {
  const prefix = address.slice(0, 8);
  const suffix = address.slice(-4);

  return `${prefix}..${suffix}`;
}

// Пример использования
const originalAddress = 'your_cosmos_address_here';
const transformedAddress = transformAddress(originalAddress);
console.log(transformedAddress);
</script>

<template>
  <div class="dropdown dropdown-hover dropdown-end h-16">
    <div
      class="relative flex gap-3 flex-row-reverse px-12 text-white items-center h-16 cursor-pointer"
    >
      <!-- <svg
        class="absolute h-16"
        width="376"
        height="51"
        viewBox="0 0 376 51"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M1.92992 50L36.5182 1H374.5V50H1.92992Z"
          fill="#1D1C30"
          stroke="#7300FF"
          stroke-width="2"
        />
      </svg> -->

      <span class="z-10" v-if="walletStore?.currentAddress">{{
        transformAddress(walletStore.currentAddress)
      }}</span>
      <span class="z-10" v-else>Connect wallet</span>
      <Icon icon="mdi:wallet" class="text-[#D9D9D9] w-6 h-6 z-10" />
    </div>
    <!-- <label
      tabindex="0"
      class="btn btn-sm btn-[#222226] hover:bg-[#2E2C50] rounded-full m-1 lowercase truncate !inline-flex text-xs md:!text-sm"
    >
      <Icon icon="mdi:wallet" class="text-[#D9D9D9]" />
    </label> -->
    <div
      tabindex="0"
      class="dropdown-content menu shadow p-2 bg-[#171718] rounded w-52 md:!w-64 overflow-auto"
    >
      <label
        v-if="!walletStore?.currentAddress"
        for="PingConnectWallet"
        class="btn btn-sm btn-primary hover:bg-[#2E2C50]"
      >
        <Icon icon="mdi:wallet" /><span class="ml-1 block">Connect Wallet</span>
      </label>
      <div class="px-2 mb-1 text-[#71FFB8] font-semibold">
        {{ walletStore.connectedWallet?.wallet }}
      </div>
      <div>
        <a
          v-if="walletStore.currentAddress"
          class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          style="overflow-wrap: anywhere"
          @click="copyAdress(walletStore.currentAddress)"
        >
          {{ walletStore.currentAddress }}
        </a>
        <div class="divider mt-1 mb-1"></div>
        <RouterLink to="/wallet/accounts">
          <div
            class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          >
            Accounts
          </div>
        </RouterLink>
        <RouterLink to="/wallet/portfolio">
          <div
            class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          >
            Portfolio
          </div>
        </RouterLink>
        <div v-if="walletStore.currentAddress" class="divider mt-1 mb-1"></div>
        <a
          v-if="walletStore.currentAddress"
          class="block py-2 px-2 text-[#FFFFFF] hover:bg-[#1F1F22] rounded cursor-pointer"
          @click="walletStore.disconnect()"
          >Disconnect</a
        >
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
    <ping-connect-wallet
      :chain-id="baseStore.currentChainId"
      :hd-path="chainStore.defaultHDPath"
      :addr-prefix="chainStore.current?.bech32Prefix || 'cosmos'"
      @connect="walletStateChange"
      @keplr-config="walletStore.suggestChain()"
    />
  </Teleport>
</template>

<style>
.ping-connect-btn,
.ping-connect-dropdown {
  display: none !important;
}
</style>
