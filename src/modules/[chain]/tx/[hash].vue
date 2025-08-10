<script lang="ts" setup>
import { useBaseStore, useBlockchain, useFormatter } from '@/stores';
import DynamicComponent from '@/components/dynamic/DynamicComponent.vue';
import { computed, ref } from '@vue/reactivity';
import type { Coin, Tx, TxResponse } from '@/types';
import { Icon } from '@iconify/vue';

import { JsonViewer } from 'vue3-json-viewer';
// if you used v1.0.5 or latster ,you should add import "vue3-json-viewer/dist/index.css"
import 'vue3-json-viewer/dist/index.css';
import BackButton from '@/components/BackButton.vue';

const props = defineProps(['hash', 'chain']);

const blockchain = useBlockchain();
const baseStore = useBaseStore();
const format = useFormatter();
const tx = ref(
  {} as {
    tx: Tx;
    tx_response: TxResponse;
  }
);
if (props.hash) {
  blockchain.rpc.getTx(props.hash).then((x) => (tx.value = x));
}
const messages = computed(() => {
  return tx.value.tx?.body?.messages || [];
});

let showCopyToast = ref(0);

async function copyAdress(address?: string) {
  const url = window.location.href;
  try {
    await navigator.clipboard.writeText(address || url);
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

const returnAmounItem = (amount: Coin | Coin[] | undefined) => {
  if (!amount) return;
  if (Array.isArray(amount)) {
    return amount[0];
  } else {
    return amount;
  }
};

const calcAmount = (amount: Coin | Coin[] | undefined) => {
  if (!amount) return '-';
  return format.formatToken(returnAmounItem(amount), true, '0,0.[00]');
};

const data = computed(() => [
  {
    label: 'tx.from',
    value:
      tx.value.tx.body.messages[0].from_address ??
      tx.value.tx.body.messages[0].delegator_address,
    action: () =>
      copyAdress(
        tx.value.tx.body.messages[0].from_address ??
          tx.value.tx.body.messages[0].delegator_address
      ),
  },
  {
    label: 'tx.to',
    value:
      tx.value.tx.body.messages[0].to_address ??
      tx.value.tx.body.messages[0].validator_address,
    action: () =>
      copyAdress(
        tx.value.tx.body.messages[0].to_address ??
          tx.value.tx.body.messages[0].validator_address
      ),
  },
  {
    label: 'tx.amount',
    value: calcAmount(tx.value.tx.body.messages[0].amount),
  },
  { label: 'tx.memo', value: tx.value.tx.body.memo },
  {
    label: 'tx.time',
    value: format.toDay(tx.value.tx_response.timestamp, 'txFormat'),
  },
  { label: 'tx.height', value: tx.value.tx_response.height },
  {
    label: 'tx.gas',
    value: `${tx.value.tx_response.gas_used} / ${tx.value.tx_response.gas_wanted}`,
  },
  {
    label: 'tx.fee',
    value: calcAmount(tx.value.tx?.auth_info?.fee?.amount),
  },
  {
    label: 'tx.tx_hash',
    value: tx.value.tx_response.txhash,
    action: () => copyAdress(),
  },
]);
</script>

<template>
  <div class="flex flex-col justify-center items-center md:px-20 pt-3">
    <BackButton class="-mt-6 mb-5 md:mb-0 md:mt-0" />
    <div
      class="overflow-auto w-full md:max-w-[930px] thick-border-block p-7 pt-6 mb-7"
    >
      <div class="flex justify-between items-center mb-7">
        <h3 class="header-20-medium-aa text-header-text uppercase">
          {{ $t('tx.transaction_summary') }}
        </h3>
        <div
          @click="() => copyAdress()"
          class="cursor-pointer flex justify-center items-center gap-2 px-2 before:z-[1] before:absolute before:rounded-full before:bg-button-v2-hover before:hover:bg-button-v2 before:w-9 before:h-9"
        >
          <Icon class="relative z-10" icon="bx:copy" :width="18" :height="18" />
        </div>
      </div>
      <div class="flex gap-4 mb-10">
        <div class="badge-transparent md:w-[152px]">
          {{ $t('tx.transfer') }}
        </div>
        <div
          class="badge-transparent md:w-[152px]"
          :class="{
            'text-tx-status-success bg-tx-status-success/20':
              tx.tx_response.code === 0,
            'text-tx-status-error bg-tx-status-error/20':
              tx.tx_response.code === 1,
            'text-tx-status-warning bg-tx-status-warning/20':
              tx.tx_response.code !== 0 && tx.tx_response.code !== 1,
          }"
        >
          {{
            tx.tx_response.code === 0
              ? $t('tx.success')
              : tx.tx_response.code === 1
              ? $t('tx.failed')
              : $t('tx.processing')
          }}
        </div>
        <div
          v-if="tx.tx_response.code === 1"
          class="text-red-text header-16 tracking-wide text-centerw-60"
        >
          {{ $t('account.no_gas') }}
        </div>
      </div>
      <div
        v-for="item in data"
        class="flex border-b border-addition text-white pt-5 pb-0.5 px-0.5"
      >
        <p class="header-16-medium w-1/3 tracking-wide truncate">
          {{ $t(item.label) }}
        </p>
        <p
          class="flex items-center cursor-pointer body-text-14 w-2/3 truncate"
          @click="item.action"
        >
          <span v-if="item.action">
            <Icon class="relative z-10" icon="bx:copy" />
          </span>
          <span>{{ item.value }}</span>
        </p>
      </div>
    </div>
    <div class="toast" v-show="showCopyToast === 1">
      <div
        class="relative bg-almost-black flex items-center gap-4 p-4 border border-button-text rounded text-green-text"
      >
        <Icon
          @click="showCopyToast = 0"
          class="absolute top-0 right-0 text-addition cursor-pointer"
          icon="codex:cross"
          width="16"
          height="16"
        />
        <div
          class="flex justify-center items-center gap-2 before:z-[1] before:absolute before:rounded-full before:bg-[#0A2B0C] before:w-9 before:h-9"
        >
          <Icon
            class="relative z-10"
            icon="material-symbols:check-rounded"
            width="34"
            height="34"
          />
        </div>
        <div class="header-20 tracking-wide">
          <span>{{ tipMsg.msg }}</span>
        </div>
      </div>
    </div>
    <div class="toast" v-show="showCopyToast === 2">
      <div
        class="relative bg-almost-black flex items-center gap-4 p-4 border border-button-text rounded text-red-text"
      >
        <Icon
          @click="showCopyToast = 0"
          class="absolute top-0 right-0 text-addition cursor-pointer"
          icon="codex:cross"
          width="16"
          height="16"
        />
        <div
          class="flex justify-center items-center gap-2 before:z-[1] before:absolute before:rounded-full before:bg-[#480D0D] before:w-9 before:h-9"
        >
          <Icon
            class="relative z-10"
            icon="codex:cross"
            width="34"
            height="34"
          />
        </div>
        <div class="header-20 tracking-wide">
          <span>{{ tipMsg.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
