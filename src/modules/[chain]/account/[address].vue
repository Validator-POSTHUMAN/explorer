<script lang="ts" setup>
import {
  useBlockchain,
  useFormatter,
  useStakingStore,
  useTxDialog,
  useWalletStore,
} from '@/stores';
import { computed, reactive, ref } from '@vue/reactivity';
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue';
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
import defaultAvatar from '@/assets/images/redesign/defaultAvatar.png';
import { valconsToBase64 } from '@/libs';
import { useIndexModule } from '../indexStore';
import QrcodeVue from 'qrcode.vue'
import SortButton from '@/layouts/components/SortButton.vue';
import { useSortableList } from '@/stores/useSortableList';

const props = defineProps(['address', 'chain']);

const blockchain = useBlockchain();
const stakingStore = useStakingStore();
const dialog = useTxDialog();
const format = useFormatter();
const account = ref({} as AuthAccount);
const txs = ref<TxResponse[]>([]);
const delegations = ref([] as Delegation[]);
const recentReceived = ref<TxResponse[]>([]);
const rewards = ref({} as DelegatorRewards);
const balances = ref([] as Coin[]);
const unbonding = ref([] as UnbondingResponses[]);
const unbondingTotal = ref(0);
const store = useIndexModule();
const ticker = computed(() => store.coinInfo.tickers[store.tickerIndex]);
const walletStore = useWalletStore();

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

const cache = JSON.parse(localStorage.getItem('avatars') || '{}');
const avatars = ref(cache || {});

const logo = (identity?: string) => {
  if (!identity || !avatars.value[identity]) return '';
  const url = avatars.value[identity] || '';
  return url.startsWith('http')
    ? url
    : `https://s3.amazonaws.com/keybase_processed_uploads/${url}`;
};

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

  balances.value.map((balance, i) => balance.amount + delegations.value[i].balance.amount)

  const receivedQuery = `?&pagination.reverse=true&query=coin_received.receiver='${address}'`;
  blockchain.rpc.getTxs(receivedQuery, {}).then((x) => {
    recentReceived.value = x.tx_responses;
  });
}

function updateEvent() {
  loadAccount(props.address);
}

const scaleData = computed(() => ([
  {
    label: 'account.available',
    value: format.tokenValueNumber(balances.value[0]),
    bgColor: 'bg-[#55B958]',
    textColor: 'text-[#55B958]',
  },
  {
    label: 'account.delegated',
    value: format.tokenValueNumber(delegations.value[0]?.balance),
    bgColor: 'bg-[#2E878A]',
    textColor: 'text-[#2E878A]',
  },
  {
    label: 'account.rewards',
    value: rewardsSum.value,
    bgColor: 'bg-[#743BA6]',
    textColor: 'text-[#743BA6]',
  },
  {
    label: 'account.unbonding',
    value: unbondingSum.value,
    bgColor: 'bg-[#BC36C3]',
    textColor: 'text-[#BC36C3]',
  },
]));

const returnAmounItem = (amount: Coin | Coin[] | undefined) => {
  if (!amount) return;
  if (Array.isArray(amount)) {
    return amount[0]
  } else {
    return amount
  }
};

const activeValidator = ref('');
const rewardsSum = ref(0);

const calcAmount = (amount: Coin | Coin[] | undefined, type: 'value' | 'token') => {
  if (!amount) return '-';
  return format.formatToken(returnAmounItem(amount), true, '0,0.[000000]').split(' ')[type === 'value' ? 0 : 1]
};

const total = computed(() => scaleData.value.reduce((sum, item) => sum + +item.value, 0));
const keywords = ref('');
watch(() => rewards.value, (newVal) => {
  rewardsSum.value = newVal?.total?.map(item => format.tokenValueNumber(item)).reduce((sum, x) => {
    return sum + x
  });
});

function sumAllUnbondingBalances(responses: UnbondingResponses[]): number {
  return responses.reduce((total, response) => {
    const entriesSum = response.entries.reduce((entryTotal, entry) => {
      return entryTotal + parseFloat(entry.balance);
    }, 0);
    return total + entriesSum;
  }, 0);
};

const unbondingSum = ref(0);
watch(() => unbonding.value, newVal => {
  unbondingSum.value = sumAllUnbondingBalances(newVal);
});


async function copyUrl(url: string) {
  if (!url) return;
  const host = window.location.origin;
  const newUrl = `${host}${url}`;
  try {
    await navigator.clipboard.writeText(newUrl);
  } catch (err) {
  }
}

const getLogo = (v: Delegation) => {
  const x = stakingStore.validators.map((x, i) => {
    return {
      v: x,
      logo: logo(x.description.identity),
    }
  }).find(item => {
    if (item.v.operator_address === v.delegation.validator_address) {
      return item.logo
    }
  })
  return x?.logo || defaultAvatar
}

function groupAndSumByDenom(arr: Coin[]): Coin[] {
  const grouped = Object.values(
    arr.reduce((acc, item) => {
      if (!acc[item.denom]) {
        acc[item.denom] = { denom: item.denom, amount: 0 };
      }
      acc[item.denom].amount += parseFloat(item.amount);
      return acc;
    }, {} as Record<string, { denom: string; amount: number }>)
  );

  return grouped.map((item) => ({
    denom: item.denom,
    amount: item.amount.toString(),
  }));
}

const assets = computed(() => {
  const filteredAssets = groupAndSumByDenom(balances.value)?.filter(item => item?.denom?.includes(keywords.value))
    .map(balanceItem => ({
      balance: balanceItem,
      chain: {
        name: store.coinInfo.name || '',
        logo: store.coinInfo.image.thumb || defaultAvatar
      },
      available_amount: walletStore.balanceOfStakingToken.amount,
      available: walletStore.balanceOfStakingToken,
      market_price_value: ticker.value?.converted_last?.usd,
      marketPrice: {
        value: ticker.value?.converted_last?.usd,
        priceChange: store.priceChange,
      },
      staking: walletStore.stakingAmount as Coin,
      total_value: +walletStore.stakingAmount.amount,
      total: groupAndSumByDenom([walletStore.balanceOfStakingToken, walletStore.stakingAmount]),
      getToken: (balanceItem: any) => calcAmount(balanceItem, 'token')
    }));

  return filteredAssets
});

const unbondingList = computed(() =>
  unbonding.value.flatMap(v =>
    v.entries.map(entry => ({
      ...entry,
      validator_address: v.validator_address,
      delegator_address: v.delegator_address,
    }))
  )
);

const barContainers = ref<(HTMLElement | null)[]>([]);
const containerWidths = ref<number[]>([]);

const updateWidths = () => {
  nextTick(() => {
    containerWidths.value = barContainers.value.map(el => el?.offsetWidth || 0);
  });
};

const isOpenQR = ref(false);
const isOpenFilters = ref(false);

const filters = reactive([
  { name: 'account.send_receive', value: false },
  { name: 'account.multi_send', value: false },
  { name: 'account.get_reward', value: false },
  { name: 'account.get_commission', value: false },
  { name: 'account.vote', value: false },
  { name: 'account.delegate', value: false },
  { name: 'account.redelegate', value: false },
  { name: 'account.undelegate', value: false },
  { name: 'account.IBC_transfer', value: false },
  { name: 'account.IBC_receive', value: false },
  { name: 'account.IBC_timeout', value: false },
  { name: 'account.IBC_ack', value: false },
  { name: 'account.grant_authz', value: false },
  { name: 'account.revoke_authz', value: false },
  { name: 'account.execute_contract', value: false },
]);
const selectedFilters = computed(() => filters.filter(item => item.value) ?? []);

const selectAllFilters = () => {
  if (filters.some(item => item.value === false)) {
    filters.map(item => item.value = true)
  } else
    filters.map(item => item.value = !item.value);
};

const clearFilters = () => filters.map(item => item.value = false);

const applyFilters = () => {
  isOpenFilters.value = false;
  updateEvent();
  txs.value = txs.value.map(item => {
    if (selectedFilters.value?.length) {

      // Send/Receive
      if (selectedFilters.value.find(filter => filter.name === "account.send_receive")
        &&
        item.tx['@type']?.includes('MsgSend')) {
        return item
      }
      // Multi Send
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.multi_send")
        &&
        item.tx['@type']?.includes('MsgMultiSend')) {
        return item
      }
      // Get Reward
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.get_reward")
        &&
        item.tx['@type']?.includes('MsgWithdrawDelegatorReward')) {
        return item
      }
      // Get Commission
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.get_commission")
        &&
        item.tx['@type']?.includes('MsgWithdrawValidatorCommission')) {
        return item
      }
      // Vote
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.vote")
        &&
        item.tx['@type']?.includes('MsgVote')) {
        return item
      }
      // Delegate
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.delegate")
        &&
        item.tx['@type']?.includes('MsgDelegate')) {
        return item
      }
      // Redelegate
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.redelegate")
        &&
        item.tx['@type']?.includes('MsgBeginRedelegate')) {
        return item
      }
      // Undelegate
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.undelegate")
        &&
        item.tx['@type']?.includes('MsgUndelegate')) {
        return item
      }
      // IBC Transfer
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.IBC_transfer")
        &&
        item.tx['@type']?.includes('MsgTransfer')) {
        return item
      }
      // Grant Authz
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.grant_authz")
        &&
        item.tx['@type']?.includes('MsgGrant')) {
        return item
      }
      // Revoke Authz
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.revoke_authz")
        &&
        item.tx['@type']?.includes('MsgRevoke')) {
        return item
      }
      // Execute Contract
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.execute_contract")
        &&
        item.tx['@type']?.includes('MsgExecuteContract')) {
        return item
      }
      // IBC Receive
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.IBC_receive")
        &&
        item.events.some(event => event.type === 'recv_packet')) {
        return item
      }
      // IBC Timeout
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.IBC_timeout")
        &&
        item.events.some(event => event.type === 'timeout_packet')) {
        return item
      }
      // IBC Ack
      if (selectedFilters.value.find((filter: { name: string, value: boolean }) => filter.name === "account.IBC_ack")
        &&
        item.events.some(event => event.type === 'write_acknowledgement')) {
        return item
      }
    }
    return item
  });
}

const transactionsList = computed(() => {
  const trList = txs.value.map(item => ({ ...item, amount: item.tx.body.messages[0].amount, messages: [...item.tx.body.messages] })) ?? [];
  const recentList = recentReceived.value.map(item => ({ ...item, amount: item.tx.body.messages[0].amount, messages: [...item.tx.body.messages] })) ?? [];

  return [...trList, ...recentList]
})

const closeFiltersModal = () => {
  filters.map(item => {
    if (selectedFilters.value?.find((sf: any) => sf?.name === item.name)) {
      item.value = true
    } else item.value = false
  });

  isOpenFilters.value = false;

};

const updateTransactionsList = () => {
  clearFilters();
  applyFilters();
  updateEvent();
};

const {
  sortedList: sortedTransactionsList,
  toggleSort: toggleTxsSortDirection
} = useSortableList(() => transactionsList.value);

const {
  sortedList: sortedAssetsList,
  toggleSort: toggleAssetsSortDirection
} = useSortableList(() => assets.value);

const {
  sortedList: sortedUnbondingList,
  toggleSort: toggleUnbondingSortDirection
} = useSortableList(() => unbondingList.value);

onMounted(() => {
  loadAccount(props.address);

  store.loadDashboard();
  walletStore.loadMyAsset();

  updateWidths();
  window.addEventListener('resize', updateWidths);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateWidths);
});


watch(() => scaleData, () => {
  updateWidths();
});

</script>
<template>
  <div v-if="account" class="md:px-5 py-1 relative">
    <!-- headcer -->
    <div class="flex flex-col xl:flex-row justify-between mb-5 xl:mb-8">
      <div class="text-white mb-5">
        <AddressWithCopy :href="`/${chain}/account/${address}`" :address="address" :size="20"
          styles="header-16 gap-6 mb-5" icon hasIconOutline :openQR="() => isOpenQR = true" />
        <p class="header-36 tracking-wide">{{ `${totalValue} $` }}</p>
      </div>

      <div id="scale" class="w-full xl:w-1/2 flex flex-col gap-2.5 md:gap-0">
        <div v-for="(item, i) in scaleData" :key="i" :class="item.textColor"
          class="grid grid-cols-6 items-center md:gap-5">
          <div class="flex justify-between md:hidden col-span-6 ">
            <p class="uppercase">{{ $t(item.label) }}</p>
            <p>{{ item.value ? `$${format.formatNumber(+item.value, '0,0')}` : '$0' }}</p>
          </div>

          <div class="hidden md:grid col-span-2 gap-2.5 grid-cols-9 items-center">
            <p class="col-span-4 uppercase text-right">{{ $t(item.label) }}</p>
            <div class="w-full flex justify-center">
              <p class="col-span-1 rounded-full w-3 h-3 text-center" :class="item.bgColor"></p>
            </div>
            <p class="col-span-4 text-left">{{ item.value ? `$${format.formatNumber(+item.value, '0,0')}` : '$0' }}</p>
          </div>

          <div :ref="el => barContainers[i] = el as HTMLElement | null"
            :style="{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }"
            class="h-3  col-span-6 md:col-span-4 items-center rounded-full relative overflow-hidden">
            <div class="absolute rounded-full top-0 bottom-0 left-0" :class="item.bgColor" :style="{
              width: containerWidths[i]
                ? `${(+item.value * containerWidths[i]) / total}px`
                : '0px'
            }"></div>

          </div>
        </div>
      </div>

    </div>

    <!-- transactions -->
    <div class="thick-border-block pt-6 px-4 mb-7">
      <div class="flex justify-between items-center">
        <h3 class="header-20-medium-aa text-header-text uppercase mb-7">{{ $t('account.transactions') }}</h3>
        <div>

          <div
            class="cursor-pointer p-0.5 inline-block bg-addition/20 hover:bg-button-v2 active:scale-90 rounded relative mr-2.5">
            <Icon icon="codicon:debug-restart" width="24" height="24" @click="updateTransactionsList" />
          </div>
          <div
            class="cursor-pointer p-0.5 inline-block bg-addition/20 hover:bg-button-v2 active:scale-90 rounded relative"
            :class="{ 'before:block before:absolute before:top-0 before:right-0 content-none before:w-1.5 before:h-1.5 before:bg-red-text before:rounded-full before:translate-x-1/2 ': selectedFilters.length }">
            <Icon icon="mynaui:filter" width="24" height="24" @click="isOpenFilters = true" />
          </div>
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
                  <SortButton @click="() => toggleTxsSortDirection('timestamp')" />
                </div>
              </td>
              <td scope="col" class="text-end">
                {{ $t('account.tx_hash') }}
              </td>

            </tr>
          </thead>

          <tbody class="">
            <tr v-if="transactionsList.length === 0" class="border-addition/20">
              <td colspan="10">
                <div class="text-center">{{ $t('account.no_transactions') }}</div>
              </td>
            </tr>

            <tr v-for="({ code, messages, amount, timestamp, txhash }, index) in sortedTransactionsList" :key="index"
              class="border-addition/20">
              <!-- 👉 result: v.code -->
              <td>
                <div class="w-full">
                  <p class="header-16-medium tracking-wide" :class="{
                    'text-tx-status-success': code === 0,
                    'text-tx-status-error': code === 1,
                    'text-tx-status-warning': code !== 0 && code !== 1
                  }">
                    {{
                      code === 0
                        ? $t('account.success')
                        : code === 1
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
                      calcAmount(amount, 'value')
                    }}</span>
                    <span class="text-header-text header-14-medium-aa uppercase">{{
                      ` [${calcAmount(amount, 'token')}]`
                    }}</span>
                  </h6>
                  <span class="body-text-14 text-[#80BDBD]">{{
                    `$${format.tokenValueNumber(returnAmounItem(amount))}` }}</span>
                </div>
              </td>
              <!-- 👉 operation -->
              <td>
                <div class="w-full flex justify-center">
                  <div v-if="code === 1" class="text-red-text header-16 tracking-wide text-centerw-60">
                    {{ $t('account.no_gas') }}
                  </div>
                  <div v-else class="badge-transparent w-60">
                    {{ format.messages(messages) }}
                  </div>

                </div>
              </td>
              <!-- 👉 time -->
              <td class="">
                <div class="flex flex-col items-end body-text-14">
                  <span class="text-white">
                    {{ format.toDay(timestamp, 'advancedFormat') }}
                  </span>
                  <span class="text-[#8899AA]">
                    {{ format.toDay(timestamp, 'time') }}
                    ({{
                      format.toDay(timestamp, 'from') }})
                  </span>
                </div>
              </td>
              <!-- 👉 TxHash -->
              <td class="text-end">
                <AddressWithCopy styles="header-14-medium-aa justify-end" :href="`/${chain}/tx/${txhash}`"
                  :address="txhash" :size="16" icon isShort isCopyHref />
                <Icon class="text-base md:hidden" icon="bx:copy" @click="() => copyUrl(`/${chain}/tx/${txhash}`)" />
              </td>
            </tr>

          </tbody>
        </table>
      </div>

    </div>

    <div class="flex flex-col md:flex-row gap-7 mb-8">
      <!-- Assets -->
      <div class="thick-border-block md:w-1/2 py-3 px-2 md:p-5">
        <div class="flex flex-col xl:flex-row gap-3 justify-between md:items-center mb-7">
          <h3 class="header-20-medium-aa text-header-text uppercase ">{{ $t('account.assets') }}</h3>
          <div
            class="w-full max-w-[500px] border border-addition rounded-full flex justify-between items-center py-2 px-6">
            <input v-model="keywords" :placeholder="$t('account.search_placeholder')" class="md:px-4 bg-transparent flex-1 outline-none header-20 text-white min-w-[400px]
              placeholder:text-addition placeholder:body-text-14 placeholder:text-xl" />
            <Icon icon="icon-park-outline:search" class="text-base text-addition" />
          </div>
        </div>

        <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-48">
          <table class=" table bg-black/20 staking-table w-full">
            <thead class="bg-black sticky top-0 z-10">
              <tr class="text-header-text body-text-14 border-addition/20">
                <td scope="col">
                  {{ $t('account.chain') }}
                </td>
                <td scope="col">
                  <div class="flex gap-1 items-center justify-end">
                    <span class="inline-block">{{ $t('account.available') }}</span>
                    <SortButton @click="() => toggleAssetsSortDirection('available_amount')" />
                  </div>
                </td>
                <td scope="col">
                  <div class="flex gap-1 items-center justify-end">
                    {{ $t('account.market_price') }}
                    <SortButton @click="() => toggleAssetsSortDirection('market_price_value')" />
                  </div>
                </td>
                <td scope="col">
                  <div class="flex gap-1 items-center justify-end">
                    <span>{{ $t('account.total') }}</span>
                    <SortButton @click="() => toggleAssetsSortDirection('total_value')" />
                  </div>
                </td>
              </tr>
            </thead>

            <tbody class="">
              <tr v-if="balances?.length === 0" class="border-addition/20">
                <td colspan="10">
                  <div class="text-center">{{ $t('account.no_data') }}</div>
                </td>
              </tr>

              <tr v-for="(balanceItem, index) in sortedAssetsList" :key="index" class="border-addition/20">
                <!-- 👉 Chain -->
                <td>
                  <div class="max-w-[300px] flex gap-2.5 items-center overflow-hidden">
                    <div class="avatar relative w-10 h-10 rounded-full">
                      <div class="w-10 h-10 rounded-full bg-gray-400 absolute opacity-10"></div>
                      <div class="w-10 h-10 rounded-full">
                        <!-- <img :src="logo ? logo : defaultAvatar" class="object-contain" @error="
                          (e) => {
                            const identity = v.description?.identity;
                            if (identity) loadAvatar(identity);
                          }
                        " /> -->
                        <img :src="balanceItem.chain.logo" class="object-contain" />
                      </div>
                    </div>

                    <div class="flex flex-col gap-1">
                      <span class="header-16-medium text-white uppercase">
                        {{ balanceItem.getToken(balanceItem.balance) }}
                      </span>
                      <span class="body-text-14 tracking-wide text-[#80BDBD]">
                        {{ balanceItem.chain.name }}
                      </span>

                    </div>
                  </div>
                </td>

                <!-- 👉 Available -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{ format.formatToken(balanceItem.available) }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">
                      {{ `$${format.tokenValue(balanceItem.available)}` }}
                    </span>
                  </div>
                </td>

                <!-- 👉 Market price -->
                <td>
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{ balanceItem.marketPrice.value }}
                    </h6>
                    <span class="body-text-14 text-green-text">
                      {{ balanceItem.marketPrice.priceChange }}%
                    </span>
                  </div>
                </td>
                <!-- 👉 Total -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{ format.formatToken(balanceItem.total[0]) }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">
                      {{ `$${format.tokenValue(balanceItem.total[0])}` }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="flex flex-wrap justify-center gap-3 md:gap-5 my-5">
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
      <div class="thick-border-block md:w-1/2 py-3 px-2 md:p-5">
        <div>
          <h3 class="header-20-medium-aa text-header-text uppercase mb-7">{{ $t('account.delegations') }}</h3>
        </div>

        <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-48">
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
              <tr v-if="delegations.length === 0" class="border-addition/20">
                <td colspan="10">
                  <div class="text-center">{{ $t('account.no_delegations') }}</div>
                </td>
              </tr>

              <tr v-for="(v, index) in delegations" :key="index" class="border-addition/20    cursor-pointer"
                :class="{ 'bg-addition/10': activeValidator === v.delegation.validator_address }"
                @click="activeValidator = v.delegation.validator_address">
                <!-- 👉 Validator -->
                <td>
                  <div class="max-w-[300px] flex gap-2.5 items-center overflow-hidden">
                    <div class="avatar relative w-10 h-10 rounded-full">
                      <div class="w-10 h-10 rounded-full bg-gray-400 absolute opacity-10"></div>
                      <div class="w-10 h-10 rounded-full">
                        <!-- <img :src="logo ? logo : defaultAvatar" class="object-contain" @error="
                            (e) => {
                              const identity = v.description?.identity;
                              if (identity) loadAvatar(identity);
                            }
                          " /> -->
                        <img :src="getLogo(v)" class="object-cover w-full h-full" />
                      </div>
                    </div>

                    <div class="flex flex-col">
                      <!-- <RouterLink class="header-16-medium tracking-wide text-white truncate"
                        :to="`/${chain}/staking/${v.delegation.validator_address}`">{{
                          format.validatorFromBech32(v.delegation.validator_address) || v.delegation.validator_address
                        }}</RouterLink> -->
                      <p class="header-16-medium tracking-wide text-white truncate">{{
                        format.validatorFromBech32(v.delegation.validator_address) || v.delegation.validator_address
                      }}</p>
                    </div>
                  </div>
                </td>

                <!-- 👉 Stacked amount -->
                <td class="">
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.formatNumber(
                          format.tokenDisplayNumber(v.balance),
                          '0,0')
                      }}
                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(v.balance)}` }}</span>
                  </div>
                </td>
                <!-- 👉 Rewards -->
                <td>
                  <div class="text-end">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      {{
                        format.tokenDisplayNumber(rewards?.rewards?.find(
                          (x) =>
                            x.validator_address === v.delegation.validator_address
                        )?.reward.find(item => item))
                      }}

                    </h6>
                    <span class="body-text-14 text-[#80BDBD]">{{
                      `$${format.tokenValueNumber(rewards?.rewards?.find(
                        (x) =>
                          x.validator_address === v.delegation.validator_address
                      )?.reward.find(item => item))}`}}</span>
                  </div>
                </td>
              </tr>

            </tbody>
          </table>
        </div>

        <ActionsPanel class="my-5" :key="activeValidator" :address="activeValidator" />
      </div>
    </div>

    <!-- unbonding -->
    <div class="thick-border-block pt-6 px-4 mb-7">
      <h3 class="header-20-medium-aa text-header-text uppercase mb-7">{{ $t('account.unbonding') }}</h3>

      <div class="overflow-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin max-h-80">
        <table class=" table bg-black/20 staking-table w-full">
          <thead class="bg-black sticky top-0 z-10">
            <tr class="text-header-text body-text-14 border-addition/20">
              <td scope="col">
                {{ $t('account.balance') }}
              </td>
              <td scope="col" class="text-end">
                {{ $t('account.initial_balance') }}
              </td>
              <td scope="col">
                <div class="flex gap-1 items-center justify-end">
                  <span>{{ $t('account.completion_time') }}</span>
                  <SortButton @click="() => toggleUnbondingSortDirection('completion_time')" />
                </div>
              </td>
              <td scope="col" class="flex gap-1 items-center justify-end">{{ $t('account.creation_height') }}</td>
            </tr>
          </thead>

          <tr v-if="unbonding.length === 0" class="border-addition/20">
            <td colspan="10">
              <div class="text-center">{{ $t('account.no_transactions') }}</div>
            </td>
          </tr>

          <tbody class="text-sm">
            <tr v-for="(entry, index) in sortedUnbondingList" :key="index">
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
                <Countdown :time="new Date(entry.completion_time).getTime() - new Date().getTime()" />
              </td>
              <td class="py-3">{{ entry.creation_height }}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- QR -->
    <div v-if="isOpenQR" class="fixed top-0 bottom-0 left-0 right-0 bg-menu-button/70 z-10" @click="isOpenQR = false">
      <div
        class="absolute flex items-center flex-col top-1/2 left-1/2 z-20 -translate-x-1/2 -translate-y-1/2 p-6 bg-chart-stroke border border-button-text rounded"
        @click.stop>
        <div class="w-full mb-6 flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full overflow-hidden">
            <img :src="store.coinInfo.image.thumb ?? defaultAvatar" class="object-cover w-full h-full" />
          </div>
          <h3 class="w-60 header-20-medium text-header-text flex-1 uppercase">{{ store.coinInfo.name || '' }}</h3>
          <Icon icon="codex:cross" width="24" height="24"
            class="cursor-pointer inline-block bg-addition/20 hover:bg-button-v2 active:scale-90 rounded text-white"
            @click="isOpenQR = false" />
        </div>
        <div class="flex justify-center p-2 bg-white mb-4">
          <qrcode-vue :value="`/${chain}/account/${address}`" :size="200" :level="'H'" />
        </div>
      </div>
    </div>

    <!-- filters -->
    <div v-if="isOpenFilters" class="fixed z-50 top-0 bottom-0 left-0 right-0 bg-menu-button/70"
      @click="closeFiltersModal">
      <div
        class="w-full h-screen md:h-auto max-w-[514px] absolute flex justify-center items-center flex-col top-1/2 left-1/2 z-20 -translate-x-1/2 -translate-y-1/2 p-6 bg-chart-stroke md:border border-button-text rounded-none md:rounded"
        @click.stop>
        <div class="w-full mb-6 flex items-center gap-2.5">
          <h3 class="header-20-medium text-header-text flex-1 uppercase">{{ $t('account.event_type') }}</h3>
          <Icon icon="codex:cross" width="24" height="24"
            class="cursor-pointer inline-block bg-addition/20 hover:bg-button-v2 active:scale-90 rounded text-white"
            @click="closeFiltersModal" />
        </div>
        <div class="w-full pr-4 mb-5">
          <div class="w-full flex items-center gap-2 rounded-[10px] border border-addition/40 p-2.5">
            <span class="w-7 h-7 relative border border-addition/40 rounded-full bg-black cursor-pointer" :class="{
              'before:block before:absolute before:top-1/2 before:left-1/2 content-none before:w-2.5 before:h-2.5 before:bg-white before:rounded-full before:-translate-x-1/2 before:-translate-y-1/2':
                filters.every(item => item.value)
            }" @click="selectAllFilters"></span>
            <span class="text-white"> {{ $t('account.all_select') }} </span>
          </div>
        </div>
        <div
          class="w-full flex flex-col flex-1 gap-1 h-full max-h-96 pr-1 mb-4 overflow-y-auto scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin">
          <div v-for="(item, i) in filters"
            class="w-full flex items-center gap-2 rounded-[10px] border border-addition/40 p-2.5">
            <span class="w-7 h-7 relative border border-addition/40 rounded-full bg-black cursor-pointer" :class="{
              'before:block before:absolute before:top-1/2 before:left-1/2 content-none before:w-2.5 before:h-2.5 before:bg-white before:rounded-full before:-translate-x-1/2 before:-translate-y-1/2':
                item.value
            }" @click="() => filters[i].value = !filters[i].value"></span>
            <span class="text-white">
              {{ $t(item.name) }}
            </span>
          </div>
        </div>
        <div class="flex flex-wrap justify-center gap-3 md:gap-5">
          <label class="btn-outline w-44" @click="clearFilters">{{
            $t('account.btn_clear') }}</label>
          <label class="btn-outline w-44" @click="applyFilters">{{ $t('account.btn_confirm') }}</label>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="text-no text-sm">{{ $t('account.error') }}</div>
</template>
