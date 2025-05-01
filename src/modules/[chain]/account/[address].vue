<script lang="ts" setup>
import {
  useBlockchain,
  useFormatter,
  useStakingStore,
  useTxDialog,
} from '@/stores';
import DynamicComponent from '@/components/dynamic/DynamicComponent.vue';
import DonutChart from '@/components/charts/DonutChart.vue';
import { computed, ref } from '@vue/reactivity';
import { onMounted, watch } from 'vue';
import { Icon } from '@iconify/vue';

import type {
  AuthAccount,
  Delegation,
  TxResponse,
  DelegatorRewards,
  UnbondingResponses,
} from '@/types';
import type { Coin } from '@cosmjs/amino';
import Countdown from '@/components/Countdown.vue';
import { fromBase64 } from '@cosmjs/encoding';
import AddressWithCopy from '@/components/AddressWithCopy.vue';
import ActionsPanel from '@/components/ActionsPanel.vue';

const props = defineProps(['address', 'chain']);

const blockchain = useBlockchain();
const stakingStore = useStakingStore();
const dialog = useTxDialog();
const format = useFormatter();
const account = ref({} as AuthAccount);
const txs = ref({} as TxResponse[]);
const delegations = ref([] as Delegation[]);
const recentReceived = ref([] as TxResponse[]);
const rewards = ref({} as DelegatorRewards);
const balances = ref([] as Coin[]);
const unbonding = ref([] as UnbondingResponses[]);
const unbondingTotal = ref(0);
const chart = {};
onMounted(() => {
  loadAccount(props.address);
});
const totalAmountByCategory = computed(() => {
  let sumDel = 0;
  delegations.value?.forEach((x) => {
    sumDel += Number(x.balance.amount);
  });
  let sumRew = 0;
  rewards.value?.total?.forEach((x) => {
    sumRew += Number(x.amount);
  });
  let sumBal = 0;
  balances.value?.forEach((x) => {
    sumBal += Number(x.amount);
  });
  let sumUn = 0;
  unbonding.value?.forEach((x) => {
    x.entries?.forEach((y) => {
      sumUn += Number(y.balance);
    });
  });
  return [sumBal, sumDel, sumRew, sumUn];
});

const labels = ['Balance', 'Delegation', 'Reward', 'Unbonding'];

const totalAmount = computed(() => {
  return totalAmountByCategory.value.reduce((p, c) => c + p, 0);
});

const totalValue = computed(() => {
  let value = 0;
  delegations.value?.forEach((x) => {
    value += format.tokenValueNumber(x.balance);
  });
  rewards.value?.total?.forEach((x) => {
    value += format.tokenValueNumber(x);
  });
  balances.value?.forEach((x) => {
    value += format.tokenValueNumber(x);
  });
  unbonding.value?.forEach((x) => {
    x.entries?.forEach((y) => {
      value += format.tokenValueNumber({ amount: y.balance, denom: stakingStore.params.bond_denom });
    });
  });
  return format.formatNumber(value, '0,0.00');
});


function loadAccount(address: string) {
  blockchain.rpc.getAuthAccount(address).then((x) => {
    account.value = x.account;
  });
  blockchain.rpc.getTxsBySender(address).then((x) => {
    txs.value = x.tx_responses;
  });
  blockchain.rpc.getDistributionDelegatorRewards(address).then((x) => {
    rewards.value = x;
  });
  blockchain.rpc.getStakingDelegations(address).then((x) => {
    delegations.value = x.delegation_responses;
  });
  blockchain.rpc.getBankBalances(address).then((x) => {
    balances.value = x.balances;
  });
  blockchain.rpc.getStakingDelegatorUnbonding(address).then((x) => {
    unbonding.value = x.unbonding_responses;
    x.unbonding_responses?.forEach((y) => {
      y.entries.forEach((z) => {
        unbondingTotal.value += Number(z.balance);
      });
    });
  });

  const receivedQuery = `?&pagination.reverse=true&query=coin_received.receiver='${address}'`;
  blockchain.rpc.getTxs(receivedQuery, {}).then((x) => {
    recentReceived.value = x.tx_responses;
  });
}

function updateEvent() {
  loadAccount(props.address);
}

function mapAmount(events: { type: string, attributes: { key: string, value: string }[] }[]) {
  if (!events) return []
  return events.find(x => x.type === 'coin_received')?.attributes
    .filter(x => x.key === 'YW1vdW50' || x.key === `amount`)
    .map(x => x.key === 'amount' ? x.value : String.fromCharCode(...fromBase64(x.value)))
}

const scaleData = computed(() => ([
  {
    label: 'account.available',
    value: '999999999',
    bgColor: 'bg-[#55B958]',
    textColor: 'text-[#55B958]',
  },
  {
    label: 'account.delegated',
    value: '777777777',
    bgColor: 'bg-[#2E878A]',
    textColor: 'text-[#2E878A]',
  },
  {
    label: 'account.rewards',
    value: '333333333',
    bgColor: 'bg-[#743BA6]',
    textColor: 'text-[#743BA6]',
  },
  {
    label: 'account.unbonding',
    value: '111111111',
    bgColor: 'bg-[#BC36C3]',
    textColor: 'text-[#BC36C3]',
  },
]));

const total = computed(() => scaleData.value.reduce((sum, item) => sum + +item.value, 0));
</script>
<template>
  <div v-if="account" class="px-5 py-1">
    <!-- headcer -->
    <div class="flex justify-between">
      <div class="text-white mb-5">
        <AddressWithCopy :href="`/${chain}/account/${address}`" :address="address" :size="20"
          styles="header-16 gap-6 mb-5" icon hasIconOutline hasQr />
        <p class="header-36 tracking-wide">${{ totalValue }}</p>
      </div>

      <div id="scale" class="w-[790px] flex">
        <div v-for="(item, i) in scaleData" class="relative header-14-medium-aa tracking-wide" :class="item.textColor"
          :style="{
            width: `${(+item.value * 790) / total}px`,
            zIndex: 10 - (i + 1),
            // textAlign: i === 0 ? 'left' : i === scaleData.length-1 ? 'right' : 'center'
          }">
          <p v-if="+item.value" class="">{{ `$${format.formatNumber(+item.value, '0,0')}` }}</p>
          <div v-if="+item.value" class="h-8 rounded-full my-3" :class="[item.bgColor, i !== 0 ? '-ml-8' : '']"></div>
          <p v-if="+item.value" class="uppercase">{{ $t(item.label) }}</p>
        </div>
      </div>

    </div>

    <!-- transactions -->
    <div class="thick-border-block pt-6 px-4 mb-7">
      <div class="flex justify-between items-center">
        <h3 class="header-20-medium-aa text-header-text uppercase mb-7">{{ $t('account.transactions') }}</h3>
        <div>
          <Icon icon="codicon:debug-restart" width="24" height="24"
            class="inline-block bg-addition/20 rounded mr-2.5" />
          <Icon icon="mynaui:filter" width="24" height="24" class="inline-block bg-addition/20 rounded" />
        </div>
      </div>
      <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-80">
        <table class=" table bg-black/20 staking-table w-full">
          <thead class="bg-black sticky top-0 z-10">
            <tr class="text-header-text body-text-14 border-addition/20">
              <td scope="col">
                {{ $t('account.result') }}
              </td>
              <td scope="col" class="text-end">
                {{ $t('account.amount') }}
              </td>
              <td scope="col" class="text-center">
                {{ $t('account.operation_message') }}
              </td>
              <td scope="col">
                <div class="flex gap-1 items-center justify-end">
                  <span>{{ $t('account.time') }}</span>
                  <span class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </span>
                </div>
              </td>
              <td scope="col" class="text-end">
                {{ $t('account.tx_hash') }}
              </td>

            </tr>
          </thead>

          <tbody class="">
            <tr v-if="recentReceived.length === 0" class="border-addition/20">
              <td colspan="10">
                <div class="text-center">{{ $t('account.no_transactions') }}</div>
              </td>
            </tr>

            <tr v-for="(recentReceivedItem, index) in recentReceived" :key="index" class="border-addition/20">
              <!-- 👉 result: v.code -->
              <td>
                <div class="w-full">
                  <p class="header-16-medium tracking-wide" :class="{
                    'text-tx-status-success': recentReceivedItem.code === 0,
                    'text-tx-status-error': recentReceivedItem.code === 1,
                    'text-tx-status-warning': recentReceivedItem.code !== 0 && recentReceivedItem.code !== 1
                  }">
                    {{
                      recentReceivedItem.code === 0
                        ? $t('account.success')
                        : recentReceivedItem.code === 1
                          ? $t('account.failed')
                          : $t('account.processing')
                    }}
                  </p>
                </div>
              </td>

              <!-- 👉 amount -->
              <td class="">
                <div class="text-end">
                  <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                    <span>{{
                      format.formatTokens(
                        recentReceivedItem.tx?.body.messages[0].amount,
                        true,
                        '0,0'
                      ).split(' ')[0]
                    }}</span>
                    <span class="text-header-text header-14-medium-aa uppercase">{{
                      ` [${format.formatTokens(
                        recentReceivedItem.tx?.body.messages[0].amount,
                        true,
                        '0,0'
                      ).split(' ')[1]}]`
                    }}</span>
                  </h6>
                  <span class="body-text-14 text-[#80BDBD]">{{
                    `$${format.tokenValueNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item =>
                      item))}`}}</span>
                </div>
              </td>
              <!-- 👉 operation -->
              <td>
                <div class="w-full flex justify-center">
                  <div class="badge-transparent w-60">
                    {{ format.messages(recentReceivedItem.tx.body.messages) }}
                  </div>
                  <!-- <div class="text-red-text header-16 tracking-wide text-centerw-60">
                  {{ $t('account.no_gas') }}
                </div> -->
                </div>
              </td>
              <!-- 👉 time -->
              <td class="">
                <div class="flex flex-col items-end body-text-14">
                  <span class="text-white">
                    {{ format.toDay(recentReceivedItem.timestamp, 'advancedFormat') }}
                  </span>
                  <span class="text-[#8899AA]">
                    {{ format.toDay(recentReceivedItem.timestamp, 'time') }}
                    ({{
                      format.toDay(recentReceivedItem.timestamp, 'from') }})
                  </span>
                </div>
              </td>
              <!-- 👉 TxHash -->
              <td class="text-end">
                <AddressWithCopy styles="header-14-medium-aa justify-end"
                  :href="`/${chain}/tx/${recentReceivedItem.txhash}`" :address="recentReceivedItem.txhash" :size="16"
                  icon isShort />
              </td>
            </tr>
            <tr v-for="(txsItem, index) in txs" :key="index" class="border-addition/20">
              <!-- 👉 result: v.code -->
              <td>
                <div class="w-full">
                  <p class="header-16-medium tracking-wide" :class="{
                    'text-tx-status-success': txsItem.code === 0,
                    'text-tx-status-error': txsItem.code === 1,
                    'text-tx-status-warning': txsItem.code !== 0 && txsItem.code !== 1
                  }">
                    {{
                      txsItem.code === 0
                        ? $t('account.success')
                        : txsItem.code === 1
                          ? $t('account.failed')
                          : $t('account.processing')
                    }}
                  </p>
                </div>
              </td>

              <!-- 👉 amount -->
              <td class="">
                <div class="text-end">
                  <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                    <span>{{
                      format.formatTokens(
                        txsItem.tx?.body.messages[0].amount,
                        true,
                        '0,0'
                      ).split(' ')[0]
                    }}</span>
                    <span class="text-header-text header-14-medium-aa uppercase">{{
                      ` [${format.formatTokens(
                        txsItem.tx?.body.messages[0].amount,
                        true,
                        '0,0'
                      ).split(' ')[1]}]`
                    }}</span>
                  </h6>
                  <span class="body-text-14 text-[#80BDBD]">{{
                    `$${format.tokenValueNumber(txsItem.tx?.body.messages[0].amount?.find(item => item))}`}}</span>
                </div>
              </td>
              <!-- 👉 operation -->
              <td>
                <div class="w-full flex justify-center">
                  <div class="badge-transparent w-60">
                    {{ format.messages(txsItem.tx.body.messages) }}
                  </div>
                  <!-- <div class="text-red-text header-16 tracking-wide text-centerw-60">
                  {{ $t('account.no_gas') }}
                </div> -->
                </div>
              </td>
              <!-- 👉 time -->
              <td class="">
                <div class="flex flex-col items-end body-text-14">
                  <span class="text-white">
                    {{ format.toDay(txsItem.timestamp, 'advancedFormat') }}
                  </span>
                  <span class="text-[#8899AA]">
                    {{ format.toDay(txsItem.timestamp, 'time') }}
                    ({{
                      format.toDay(txsItem.timestamp, 'from') }})
                  </span>
                </div>
              </td>
              <!-- 👉 TxHash -->
              <td class="text-end">
                <AddressWithCopy styles="header-14-medium-aa justify-end" :href="`/${chain}/tx/${txsItem.txhash}`"
                  :address="txsItem.txhash" :size="16" icon isShort />
              </td>
            </tr>
            <tr v-for="(delegationItem, index) in delegations" :key="index" class="border-addition/20">
              <!-- 👉 result: v.code -->
              <td>
                <div class="w-full">
                  <p class="header-16-medium tracking-wide text-tx-status-success">
                    {{ $t('account.success') }}
                  </p>
                </div>
              </td>

              <!-- 👉 amount -->
              <td class="">
                <div class="text-end">
                  <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                    <span> {{ format.formatToken(delegationItem?.balance).split(' ')[0] }}
                    </span>
                    <span class="text-header-text header-14-medium-aa uppercase">{{
                      ` [${format.formatToken(delegationItem?.balance).split(' ')[1]}]`
                    }}</span>
                  </h6>
                  <span class="body-text-14 text-[#80BDBD]">{{
                    `$${format.tokenValueNumber(delegationItem?.balance)}` }}</span>
                </div>
              </td>
              <!-- 👉 operation -->
              <td>
                <div class="w-full flex justify-center">
                  <div class="badge-transparent w-60">
                    {{ $t('account.delegate') }}
                  </div>
                  <!-- <div class="text-red-text header-16 tracking-wide text-centerw-60">
                  {{ $t('account.no_gas') }}
                </div> -->
                </div>
              </td>
              <!-- 👉 time -->
              <td class="">
                <div class="flex flex-col items-end body-text-14">
                  <span class="text-white">
                    {{ format.toDay(delegationItem.delegation.shares, 'advancedFormat') }}
                  </span>
                  <span class="text-[#8899AA]">
                    {{ format.toDay(delegationItem.delegation.shares, 'time') }}
                    ({{
                      format.toDay(delegationItem.delegation.shares, 'from') }})
                  </span>
                </div>
              </td>
              <!-- 👉 TxHash -->
              <td class="text-end">


                <AddressWithCopy styles="header-14-medium-aa justify-end"
                  :href="`/${chain}/tx/${delegationItem.delegation.delegator_address}`"
                  :address="delegationItem.delegation.delegator_address" :size="16" icon isShort />


              </td>
            </tr>

          </tbody>
        </table>
      </div>

    </div>

    <div class="flex gap-7 mb-8">
      <!-- assets -->
      <div class="thick-border-block w-1/2 p-5">
        <div class="flex justify-between items-center mb-7">
          <h3 class="header-20-medium-aa text-header-text uppercase ">{{ $t('account.assets') }}</h3>
          <div
            class="w-full max-w-[500px] border border-addition rounded-full flex justify-between items-center py-2 px-6">
            <input :placeholder="$t('account.search_placeholder')" class="md:px-4 bg-transparent flex-1 outline-none header-20 text-white min-w-[400px]
              placeholder:text-addition placeholder:body-text-14 placeholder:text-xl" />
            <Icon icon="icon-park-outline:search" class="text-base text-addition" />
          </div>
        </div>

        <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-44">
          <table class=" table bg-black/20 staking-table w-full">
            <thead class="bg-black sticky top-0 z-10">
              <tr class="text-header-text body-text-14 border-addition/20">
                <td scope="col">
                  {{ $t('account.chain') }}
                </td>
                <td scope="col" class="text-end">
                  {{ $t('account.available') }}
                  <span class="cursor-pointer inline-block">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </span>
                </td>
                <td scope="col" class="flex gap-1 items-center justify-end">
                  {{ $t('account.market_price') }}
                  <span class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </span>
                </td>
                <td scope="col">
                  <div class="flex gap-1 items-center justify-end">
                    <span>{{ $t('account.total') }}</span>
                    <span class="cursor-pointer">
                      <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                      <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                    </span>
                  </div>
                </td>
              </tr>
            </thead>

            <tbody class="">
              <tr v-if="recentReceived.length === 0" class="border-addition/20">
                <td colspan="10">
                  <div class="text-center">{{ $t('account.no_transactions') }}</div>
                </td>
              </tr>

              <tr v-for="(recentReceivedItem, index) in recentReceived" :key="index" class="border-addition/20">
                <!-- 👉 Chain -->
                <td>
                  <div class="w-full">
                    <p class="header-16-medium tracking-wide" :class="{
                      'text-tx-status-success': recentReceivedItem.code === 0,
                      'text-tx-status-error': recentReceivedItem.code === 1,
                      'text-tx-status-warning': recentReceivedItem.code !== 0 && recentReceivedItem.code !== 1
                    }">
                      {{
                        recentReceivedItem.code === 0
                          ? $t('account.success')
                          : recentReceivedItem.code === 1
                            ? $t('account.failed')
                            : $t('account.processing')
                      }}
                    </p>
                  </div>
                </td>

                <!-- 👉 Available -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.formatNumber(
                          format.tokenDisplayNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item => item)),
                          '0,0')
                      }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item =>
                        item))}`}}</span>
                  </div>
                </td>
                <!-- 👉 Market price -->
                <td>
                  <div class="w-full flex justify-center">
                    <div class="badge-transparent w-60">
                      {{ format.messages(recentReceivedItem.tx.body.messages) }}
                    </div>
                    <!-- <div class="text-red-text header-16 tracking-wide text-centerw-60">
                  {{ $t('account.no_gas') }}
                </div> -->
                  </div>
                </td>
                <!-- 👉 Total -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.formatNumber(
                          format.tokenDisplayNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item => item)),
                          '0,0')
                      }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item =>
                        item))}`}}</span>
                  </div>
                </td>

              </tr>

            </tbody>
          </table>
        </div>

        <div class="flex justify-center gap-5 my-5">
          <label for="send" class="btn-outline w-44" @click="dialog.open('send', {}, updateEvent)">{{
            $t('account.btn_send') }}</label>

          <label for="transfer" class="btn-outline w-44" @click="
            dialog.open(
              'transfer',
              {
                chain_name: blockchain.current?.prettyName,
              },
              updateEvent
            )
            ">{{ $t('account.btn_transfer') }}</label>

        </div>
      </div>

      <!-- Delegations -->
      <div class="thick-border-block w-1/2 p-5">
        <div>
          <h3 class="header-20-medium-aa text-header-text uppercase mb-7">{{ $t('account.delegations') }}</h3>
        </div>

        <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-44">
          <table class=" table bg-black/20 staking-table w-full">
            <thead class="bg-black sticky top-0 z-10">
              <tr class="text-header-text body-text-14 border-addition/20">
                <td scope="col">
                  {{ $t('account.validator') }}
                </td>
                <td scope="col" class="text-end">
                  {{ $t('account.staked_amount') }}
                </td>
                <td scope="col" class="text-center">
                  {{ $t('account.rewards') }}
                </td>
              </tr>
            </thead>

            <tbody class="">
              <tr v-if="recentReceived.length === 0" class="border-addition/20">
                <td colspan="10">
                  <div class="text-center">{{ $t('account.no_transactions') }}</div>
                </td>
              </tr>

              <tr v-for="(recentReceivedItem, index) in recentReceived" :key="index" class="border-addition/20">
                <!-- 👉 Validator -->
                <td>
                  <div class="w-full">
                    <p class="header-16-medium tracking-wide" :class="{
                      'text-tx-status-success': recentReceivedItem.code === 0,
                      'text-tx-status-error': recentReceivedItem.code === 1,
                      'text-tx-status-warning': recentReceivedItem.code !== 0 && recentReceivedItem.code !== 1
                    }">
                      {{
                        recentReceivedItem.code === 0
                          ? $t('account.success')
                          : recentReceivedItem.code === 1
                            ? $t('account.failed')
                            : $t('account.processing')
                      }}
                    </p>
                  </div>
                </td>

                <!-- 👉 Stacked amount -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.formatNumber(
                          format.tokenDisplayNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item => item)),
                          '0,0')
                      }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item =>
                        item))}`}}</span>
                  </div>
                </td>
                <!-- 👉 Rewards -->
                <td>
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.formatNumber(
                          format.tokenDisplayNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item => item)),
                          '0,0')
                      }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(recentReceivedItem.tx?.body.messages[0].amount?.find(item =>
                        item))}`}}</span>
                  </div>
                </td>
              </tr>

            </tbody>
          </table>
        </div>

        <ActionsPanel class="my-5" />

      </div>


    </div>





    <!-- address -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <div class="flex items-center">
        <!-- img -->
        <div class="inline-flex relative w-11 h-11 rounded-md">
          <div class="w-11 h-11 absolute rounded-md opacity-10 bg-primary"></div>
          <div class="w-full inline-flex items-center align-middle flex-none justify-center">
            <Icon icon="mdi-qrcode" class="text-primary" style="width: 27px; height: 27px" />
          </div>
        </div>
        <!-- content -->
        <div class="flex flex-1 flex-col truncate pl-4">
          <h2 class="text-sm card-title">{{ $t('account.address') }}:</h2>
          <span class="text-xs truncate"> {{ address }}</span>
        </div>
      </div>
    </div>

    <!-- Assets -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <div class="flex justify-between">
        <h2 class="card-title mb-4">{{ $t('account.assets') }}</h2>
        <!-- button -->
        <div class="flex justify-end mb-4 pr-5">
          <label for="send" class="btn btn-primary btn-sm mr-2" @click="dialog.open('send', {}, updateEvent)">{{
            $t('account.btn_send') }}</label>
          <label for="transfer" class="btn btn-primary btn-sm" @click="
            dialog.open(
              'transfer',
              {
                chain_name: blockchain.current?.prettyName,
              },
              updateEvent
            )
            ">{{ $t('account.btn_transfer') }}</label>
        </div>
      </div>
      <div class="grid md:!grid-cols-3">
        <div class="md:!col-span-1">
          <DonutChart :series="totalAmountByCategory" :labels="labels" />
        </div>
        <div class="mt-4 md:!col-span-2 md:!mt-0 md:!ml-4">
          <!-- list-->
          <div class="">
            <!--balances  -->
            <div class="flex items-center px-4 mb-2" v-for="(balanceItem, index) in balances" :key="index">
              <div class="w-9 h-9 rounded overflow-hidden flex items-center justify-center relative mr-4">
                <Icon icon="mdi-account-cash" class="text-info" size="20" />
                <div class="absolute top-0 bottom-0 left-0 right-0 bg-info opacity-20"></div>
              </div>
              <div class="flex-1">
                <div class="text-sm font-semibold">
                  {{ format.formatToken(balanceItem) }}
                </div>
                <div class="text-xs">
                  {{ format.calculatePercent(balanceItem.amount, totalAmount) }}
                </div>
              </div>
              <div class="text-xs truncate relative py-1 px-3 rounded-full w-fit text-primary dark:invert mr-2">
                <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-primary dark:invert text-sm"></span>
                ${{ format.tokenValue(balanceItem) }}
              </div>
            </div>
            <!--delegations  -->
            <div class="flex items-center px-4 mb-2" v-for="(delegationItem, index) in delegations" :key="index">
              <div class="w-9 h-9 rounded overflow-hidden flex items-center justify-center relative mr-4">
                <Icon icon="mdi-user-clock" class="text-warning" size="20" />
                <div class="absolute top-0 bottom-0 left-0 right-0 bg-warning opacity-20"></div>
              </div>
              <div class="flex-1">
                <div class="text-sm font-semibold">
                  {{ format.formatToken(delegationItem?.balance) }}
                </div>
                <div class="text-xs">
                  {{
                    format.calculatePercent(
                      delegationItem?.balance?.amount,
                      totalAmount
                    )
                  }}
                </div>
              </div>
              <div class="text-xs truncate relative py-1 px-3 rounded-full w-fit text-primary dark:invert mr-2">
                <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-primary dark:invert text-sm"></span>
                ${{ format.tokenValue(delegationItem?.balance) }}
              </div>
            </div>
            <!-- rewards.total -->
            <div class="flex items-center px-4 mb-2" v-for="(rewardItem, index) in rewards.total" :key="index">
              <div class="w-9 h-9 rounded overflow-hidden flex items-center justify-center relative mr-4">
                <Icon icon="mdi-account-arrow-up" class="text-success" size="20" />
                <div class="absolute top-0 bottom-0 left-0 right-0 bg-success opacity-20"></div>
              </div>
              <div class="flex-1">
                <div class="text-sm font-semibold">
                  {{ format.formatToken(rewardItem) }}
                </div>
                <div class="text-xs">{{ format.calculatePercent(rewardItem.amount, totalAmount) }}</div>
              </div>
              <div class="text-xs truncate relative py-1 px-3 rounded-full w-fit text-primary dark:invert mr-2">
                <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-primary  dark:invert text-sm"></span>${{
                  format.tokenValue(rewardItem) }}

              </div>
            </div>
            <!-- mdi-account-arrow-right -->
            <div class="flex items-center px-4">
              <div class="w-9 h-9 rounded overflow-hidden flex items-center justify-center relative mr-4">
                <Icon icon="mdi-account-arrow-right" class="text-error" size="20" />
                <div class="absolute top-0 bottom-0 left-0 right-0 bg-error opacity-20"></div>
              </div>
              <div class="flex-1">
                <div class="text-sm font-semibold">
                  {{
                    format.formatToken({
                      amount: String(unbondingTotal),
                      denom: stakingStore.params.bond_denom,
                    })
                  }}
                </div>
                <div class="text-xs">
                  {{ format.calculatePercent(unbondingTotal, totalAmount) }}
                </div>
              </div>
              <div class="text-xs truncate relative py-1 px-3 rounded-full w-fit text-primary dark:invert mr-2">
                <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-primary dark:invert"></span>
                ${{ format.tokenValue({
                  amount: String(unbondingTotal),
                  denom: stakingStore.params.bond_denom,
                })
                }}
              </div>
            </div>
          </div>
          <div class="mt-4 text-lg font-semibold mr-5 pl-5 border-t pt-4 text-right">
            {{ $t('account.total_value') }}: ${{ totalValue }}
          </div>
        </div>
      </div>
    </div>

    <!-- Delegations -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <div class="flex justify-between">
        <h2 class="card-title mb-4">{{ $t('account.delegations') }}</h2>
        <div class="flex justify-end mb-4">
          <label for="delegate" class="btn btn-primary btn-sm mr-2" @click="dialog.open('delegate', {}, updateEvent)">{{
            $t('account.btn_delegate') }}</label>
          <label for="withdraw" class="btn btn-primary btn-sm" @click="dialog.open('withdraw', {}, updateEvent)">{{
            $t('account.btn_withdraw') }}</label>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="table w-full text-sm table-zebra">
          <thead>
            <tr>
              <th class="py-3">{{ $t('account.validator') }}</th>
              <th class="py-3">{{ $t('account.delegation') }}</th>
              <th class="py-3">{{ $t('account.rewards') }}</th>
              <th class="py-3">{{ $t('account.action') }}</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-if="delegations.length === 0">
              <td colspan="10">
                <div class="text-center">{{ $t('account.no_delegations') }}</div>
              </td>
            </tr>
            <tr v-for="(v, index) in delegations" :key="index">
              <td class="text-caption text-primary py-3">
                <RouterLink :to="`/${chain}/staking/${v.delegation.validator_address}`">{{
                  format.validatorFromBech32(v.delegation.validator_address) || v.delegation.validator_address
                }}</RouterLink>
              </td>
              <td class="py-3">
                {{ format.formatToken(v.balance, true, '0,0.[000000]') }}
              </td>
              <td class="py-3">
                {{
                  format.formatTokens(
                    rewards?.rewards?.find(
                      (x) =>
                        x.validator_address === v.delegation.validator_address
                    )?.reward
                  )
                }}
              </td>
              <td class="py-3">
                <div v-if="v.balance" class="flex justify-end">
                  <label for="delegate" class="btn btn-primary btn-xs mr-2" @click="
                    dialog.open(
                      'delegate',
                      {
                        validator_address: v.delegation.validator_address,
                      },
                      updateEvent
                    )
                    ">{{ $t('account.btn_delegate') }}</label>
                  <label for="redelegate" class="btn btn-primary btn-xs mr-2" @click="
                    dialog.open(
                      'redelegate',
                      {
                        validator_address: v.delegation.validator_address,
                      },
                      updateEvent
                    )
                    ">{{ $t('account.btn_redelegate') }}</label>
                  <label for="unbond" class="btn btn-primary btn-xs" @click="
                    dialog.open(
                      'unbond',
                      {
                        validator_address: v.delegation.validator_address,
                      },
                      updateEvent
                    )
                    ">{{ $t('account.btn_unbond') }}</label>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Unbonding Delegations -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow" v-if="unbonding && unbonding.length > 0">
      <h2 class="card-title mb-4">{{ $t('account.unbonding_delegations') }}</h2>
      <div class="overflow-x-auto">
        <table class="table text-sm w-full">
          <thead>
            <tr>
              <th class="py-3">{{ $t('account.creation_height') }}</th>
              <th class="py-3">{{ $t('account.initial_balance') }}</th>
              <th class="py-3">{{ $t('account.balance') }}</th>
              <th class="py-3">{{ $t('account.completion_time') }}</th>
            </tr>
          </thead>
          <tbody class="text-sm" v-for="(v, index) in unbonding" :key="index">
            <tr>
              <td class="text-caption text-primary py-3 bg-slate-200" colspan="10">
                <RouterLink :to="`/${chain}/staking/${v.validator_address}`">{{
                  v.validator_address
                }}</RouterLink>
              </td>
            </tr>
            <tr v-for="entry in v.entries">
              <td class="py-3">{{ entry.creation_height }}</td>
              <td class="py-3">
                {{
                  format.formatToken(
                    {
                      amount: entry.initial_balance,
                      denom: stakingStore.params.bond_denom,
                    },
                    true,
                    '0,0.[00]'
                  )
                }}
              </td>
              <td class="py-3">
                {{
                  format.formatToken(
                    {
                      amount: entry.balance,
                      denom: stakingStore.params.bond_denom,
                    },
                    true,
                    '0,0.[00]'
                  )
                }}
              </td>
              <td class="py-3">
                <Countdown :time="new Date(entry.completion_time).getTime() - new Date().getTime()" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Transactions -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <h2 class="card-title mb-4">{{ $t('account.transactions') }}</h2>
      <div class="overflow-x-auto">
        <table class="table w-full text-sm">
          <thead>
            <tr>
              <th class="py-3">{{ $t('account.height') }}</th>
              <th class="py-3">{{ $t('account.hash') }}</th>
              <th class="py-3">{{ $t('account.messages') }}</th>
              <th class="py-3">{{ $t('account.time') }}</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-if="txs.length === 0">
              <td colspan="10">
                <div class="text-center">{{ $t('account.no_transactions') }}</div>
              </td>
            </tr>
            <tr v-for="(v, index) in txs" :key="index">
              <td class="text-sm py-3">
                <RouterLink :to="`/${chain}/block/${v.height}`" class="dark:invert">{{
                  v.height
                }}</RouterLink>
              </td>
              <td class="truncate py-3" style="max-width: 200px">
                <RouterLink :to="`/${chain}/tx/${v.txhash}`" class="dark:invert">
                  {{ v.txhash }}
                </RouterLink>
              </td>
              <td class="flex items-center py-3">
                <div class="mr-2">
                  {{ format.messages(v.tx.body.messages) }}
                </div>
                <Icon v-if="v.code === 0" icon="mdi-check" class="text-success text-lg" />
                <Icon v-else icon="mdi-multiply" class="text-error text-lg" />
              </td>
              <td class="py-3">{{ format.toLocaleDate(v.timestamp) }} <span class=" text-xs">({{
                format.toDay(v.timestamp, 'from') }})</span> </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Received -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <h2 class="card-title mb-4">{{ $t('account.received') }}</h2>
      <div class="overflow-x-auto">
        <table class="table w-full text-sm">
          <thead>
            <tr>
              <th class="py-3">{{ $t('account.height') }}</th>
              <th class="py-3">{{ $t('account.hash') }}</th>
              <th class="py-3">{{ $t('account.amount') }}</th>
              <th class="py-3">{{ $t('account.time') }}</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-if="recentReceived.length === 0">
              <td colspan="10">
                <div class="text-center">{{ $t('account.no_transactions') }}</div>
              </td>
            </tr>
            <tr v-for="(v, index) in recentReceived" :key="index">
              <td class="text-sm py-3">
                <RouterLink :to="`/${chain}/block/${v.height}`" class="dark:invert">{{
                  v.height
                }}</RouterLink>
              </td>
              <td class="truncate py-3" style="max-width: 200px">
                <RouterLink :to="`/${chain}/tx/${v.txhash}`" class="dark:invert">
                  {{ v.txhash }}
                </RouterLink>
              </td>
              <td class="flex items-center py-3">
                <div class="mr-2">
                  {{ mapAmount(v.events)?.join(", ") }}
                </div>
                <Icon v-if="v.code === 0" icon="mdi-check" class="text-success text-lg" />
                <Icon v-else icon="mdi-multiply" class="text-error text-lg" />
              </td>
              <td class="py-3">{{ format.toLocaleDate(v.timestamp) }} <span class=" text-xs">({{
                format.toDay(v.timestamp, 'from') }})</span> </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Account -->
    <div class="bg-base-100 px-4 pt-3 pb-4 rounded mb-4 shadow">
      <h2 class="card-title mb-4">{{ $t('account.acc') }}</h2>
      <DynamicComponent :value="account" />
    </div>
  </div>
  <div v-else class="text-no text-sm">{{ $t('account.error') }}</div>
</template>
