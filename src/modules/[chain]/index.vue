<script lang="ts" setup>
import MdEditor from 'md-editor-v3';
import PriceMarketChart from '@/components/charts/PriceMarketChart.vue';

import { Icon } from '@iconify/vue';
import {
  useBlockchain,
  useFormatter,
  useTxDialog,
  useWalletStore,
  useStakingStore,
  useParamStore,
} from '@/stores';
import { onMounted, ref } from 'vue';
import { useIndexModule, colorMap } from './indexStore';
import { computed } from '@vue/reactivity';

import CardStatisticsVertical from '@/components/CardStatisticsVertical.vue';
import ProposalListItem from '@/components/ProposalListItem.vue';
import ArrayObjectElement from '@/components/dynamic/ArrayObjectElement.vue';

const props = defineProps(['chain']);

const blockchain = useBlockchain();
const store = useIndexModule();
const walletStore = useWalletStore();
const format = useFormatter();
const dialog = useTxDialog();
const stakingStore = useStakingStore();
const paramStore = useParamStore();
const coinInfo = computed(() => {
  return store.coinInfo;
});

onMounted(() => {
  store.loadDashboard();
  walletStore.loadMyAsset();
  paramStore.handleAbciInfo();
  // if(!(coinInfo.value && coinInfo.value.name)) {
  // }
});
const ticker = computed(() => store.coinInfo.tickers[store.tickerIndex]);

const currName = ref('');
blockchain.$subscribe((m, s) => {
  if (s.chainName !== currName.value) {
    currName.value = s.chainName;
    store.loadDashboard();
    walletStore.loadMyAsset();
    paramStore.handleAbciInfo();
  }
});
function shortName(name: string, id: string) {
  return name.toLowerCase().startsWith('ibc/') ||
    name.toLowerCase().startsWith('0x')
    ? id
    : name;
}

const comLinks = [
  {
    name: 'Website',
    icon: 'mdi-web',
    href: store.homepage,
  },
  {
    name: 'Twitter',
    icon: 'mdi-twitter',
    href: store.twitter,
  },
  {
    name: 'Telegram',
    icon: 'mdi-telegram',
    href: store.telegram,
  },
  {
    name: 'Github',
    icon: 'mdi-github',
    href: store.github,
  },
];

// wallet box
const change = computed(() => {
  const token = walletStore.balanceOfStakingToken;
  return token ? format.priceChanges(token.denom) : 0;
});
const color = computed(() => {
  switch (true) {
    case change.value > 0:
      return 'text-[#03F237]';
    case change.value === 0:
      return 'text-[#686868]';
    case change.value < 0:
      return 'text-[#DE1D1D]';
  }
});

function updateState() {
  walletStore.loadMyAsset();
}

function trustColor(v: string) {
  return `text-${colorMap(v)}`;
}

const quantity = ref(100);
const qty = computed({
  get: () => {
    return parseFloat(quantity.value.toFixed(6));
  },
  set: (val) => {
    quantity.value = val;
  },
});
const amount = computed({
  get: () => {
    return quantity.value * ticker.value.converted_last.usd || 0;
  },
  set: (val) => {
    quantity.value = val / ticker.value.converted_last.usd || 0;
  },
});
</script>

<template>
  <div>
    <!--Up-->
    <div
      class="bg-black bg-opacity-50 border-[0.5rem] border-[#1C1C21] rounded-lg mt-4 shadow"
    >
      <div
        class="flex justify-between px-4 pt-4 pb-2 text-lg font-semibold text-[#FFFFFF]"
      >
        <div>
          <span ref="textToCopy" class="truncate">{{
            walletStore.currentAddress || 'Not Connected'
          }}</span>
          <div @click="copyText" class="btn rounded-full ml-3 h-1 scale-75 bg-[#1C1C21] hover:bg-[#0F334E] border-none">
            <svg
              width="17"
              height="17"
              viewBox="0 0 19 19"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M6.1 6.1V3.72C6.1 2.76791 6.1 2.29187 6.28529 1.92822C6.44827 1.60834 6.70834 1.34827 7.02822 1.18529C7.39187 1 7.86791 1 8.82 1H15.28C16.2321 1 16.7081 1 17.0718 1.18529C17.3917 1.34827 17.6517 1.60834 17.8147 1.92822C18 2.29187 18 2.76791 18 3.72V10.18C18 11.1321 18 11.6081 17.8147 11.9718C17.6517 12.2917 17.3917 12.5517 17.0718 12.7147C16.7081 12.9 16.2321 12.9 15.28 12.9H12.9M3.72 18H10.18C11.1321 18 11.6081 18 11.9718 17.8147C12.2917 17.6517 12.5517 17.3917 12.7147 17.0718C12.9 16.7081 12.9 16.2321 12.9 15.28V8.82C12.9 7.86791 12.9 7.39187 12.7147 7.02822C12.5517 6.70834 12.2917 6.44827 11.9718 6.28529C11.6081 6.1 11.1321 6.1 10.18 6.1H3.72C2.76791 6.1 2.29187 6.1 1.92822 6.28529C1.60834 6.44827 1.34827 6.70834 1.18529 7.02822C1 7.39187 1 7.86791 1 8.82V15.28C1 16.2321 1 16.7081 1.18529 17.0718C1.34827 17.3917 1.60834 17.6517 1.92822 17.8147C2.29187 18 2.76791 18 3.72 18Z"
                stroke="#E2E2E2"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </div>
        </div>
        <!-- <RouterLink
          v-if="walletStore.currentAddress"
          class="float-right text-sm cursor-pointert link link-primary no-underline font-medium"
          :to="`/${chain}/account/${walletStore.currentAddress}`"
          >{{ $t('index.more') }}</RouterLink
        > -->
        <div class="grid grid-cols-3 gap-4 px-4 pb-6 mt-4">
          <label
            for="PingTokenConvert"
            class="btn bg-[#1C1C21] hover:bg-[#0F334E] text-[#3FB6A8] px-[5rem] rounded-full border-1 border-[#71FFB8]"
            >{{ $t('index.btn_swap') }}</label
          >
          <label
            for="send"
            class="btn bg-[#1C1C21] hover:bg-[#0F334E] text-[#3FB6A8] px-[5rem] rounded-full border-1 border-[#71FFB8]"
            @click="dialog.open('send', {}, updateState)"
            >{{ $t('account.btn_send') }}</label
          >
          <label
            for="delegate"
            class="btn bg-[#1C1C21] hover:bg-[#0F334E] text-[#3FB6A8] px-[5rem] rounded-full border-1 border-[#71FFB8]"
            @click="dialog.open('delegate', {}, updateState)"
            >{{ $t('account.btn_delegate') }}</label
          >
          <!-- <RouterLink
            to="/wallet/receive"
            class="btn !bg-info !border-info text-white hidden"
            >{{ $t('index.receive') }}</RouterLink
          > -->
        </div>
      </div>
      <div class="flex flex-row gap-4 px-4 pb-6">
        <div class="bg-[#1F1F22] rounded-sm px-4 py-3 w-full">
          <div class="text-sm mb-1 text-[#71FFB8]">
            {{ $t('account.balance') }}
          </div>
          <div class="text-lg font-semibold text-[#FFFFFF]">
            {{ format.formatToken(walletStore.balanceOfStakingToken) }}
          </div>
          <div class="text-sm" :class="color">
            ${{ format.tokenValue(walletStore.balanceOfStakingToken) }}
          </div>
        </div>
        <div class="bg-[#1F1F22] rounded-sm px-4 py-3 w-full">
          <div class="text-sm mb-1 text-[#71FFB8]">
            {{ $t('module.staking') }}
          </div>
          <div class="text-lg font-semibold text-[#FFFFFF]">
            {{ format.formatToken(walletStore.stakingAmount) }}
          </div>
          <div class="text-sm" :class="color">
            ${{ format.tokenValue(walletStore.stakingAmount) }}
          </div>
        </div>
        <div class="bg-[#1F1F22] rounded-sm px-4 py-3 w-full">
          <div class="text-sm mb-1 text-[#71FFB8]">
            {{ $t('index.reward') }}
          </div>
          <div class="text-lg font-semibold text-[#FFFFFF]">
            {{ format.formatToken(walletStore.rewardAmount) }}
          </div>
          <div class="text-sm" :class="color">
            ${{ format.tokenValue(walletStore.rewardAmount) }}
          </div>
        </div>
        <div class="bg-[#1F1F22] rounded-sm px-4 py-3 w-full">
          <div class="text-sm mb-1 text-[#71FFB8]">
            {{ $t('index.unbonding') }}
          </div>
          <div class="text-lg font-semibold text-[#FFFFFF]">
            {{ format.formatToken(walletStore.unbondingAmount) }}
          </div>
          <div class="text-sm" :class="color">
            ${{ format.tokenValue(walletStore.unbondingAmount) }}
          </div>
        </div>
      </div>

      <div
        v-if="walletStore.delegations.length > 0"
        class="px-4 pb-4 overflow-auto bg-[#141415]"
      >
        <table class="table table-compact w-full table-zebra">
          <thead>
            <tr>
              <th>{{ $t('account.validator') }}</th>
              <th>{{ $t('account.delegations') }}</th>
              <th>{{ $t('account.rewards') }}</th>
              <th>{{ $t('staking.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in walletStore.delegations" :key="index">
              <td>
                <RouterLink
                  class="link link-primary no-underline"
                  :to="`/${chain}/staking/${item?.delegation?.validator_address}`"
                >
                  {{
                    format.validatorFromBech32(
                      item?.delegation?.validator_address
                    )
                  }}
                </RouterLink>
              </td>
              <td>{{ format.formatToken(item?.balance) }}</td>
              <td>
                {{
                  format.formatTokens(
                    walletStore?.rewards?.rewards?.find(
                      (el) =>
                        el?.validator_address ===
                        item?.delegation?.validator_address
                    )?.reward
                  )
                }}
              </td>
              <td>
                <div>
                  <label
                    for="delegate"
                    class="btn !btn-xs !btn-primary btn-ghost rounded-sm mr-2"
                    @click="
                      dialog.open(
                        'delegate',
                        {
                          validator_address: item.delegation.validator_address,
                        },
                        updateState
                      )
                    "
                  >
                    {{ $t('account.btn_delegate') }}
                  </label>
                  <label
                    for="withdraw"
                    class="btn !btn-xs !btn-primary btn-ghost rounded-sm"
                    @click="
                      dialog.open(
                        'withdraw',
                        {
                          validator_address: item.delegation.validator_address,
                        },
                        updateState
                      )
                    "
                  >
                    {{ $t('index.btn_withdraw_reward') }}
                  </label>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Teleport to="body">
        <ping-token-convert
          :chain-name="blockchain?.current?.prettyName"
          :endpoint="blockchain?.endpoint?.address"
          :hd-path="walletStore?.connectedWallet?.hdPath"
        ></ping-token-convert>
      </Teleport>
    </div>

    <!--Down-->
    <div
      v-if="coinInfo && coinInfo.name"
      class="bg-black bg-opacity-50 rounded shadow mb-4"
    >
      <div class="grid grid-cols-2 md:grid-cols-3 p-4">
        <div class="col-span-2 md:col-span-1">
          <div class="text-xl font-semibold text-[#FFFFFF]">
            {{ coinInfo.name }} (<span class="uppercase">{{
              coinInfo.symbol
            }}</span
            >)
          </div>
          <div class="text-xs mt-2 text-[#686868]">
            {{ $t('index.rank') }}:
            <div
              class="badge text-xs badge-error bg-[#33583B] dark:bg-[#33583B] text-green-400"
            >
              #{{ coinInfo.market_cap_rank }}
            </div>
          </div>

          <div class="my-4 flex flex-wrap items-center">
            <a
              v-for="(item, index) of comLinks"
              :key="index"
              :href="item.href"
              class="link link-primary px-2 py-1 rounded-sm no-underline hover:text-primary hover:bg-gray-100 dark:hover:bg-slate-800 flex items-center"
            >
              <Icon :icon="item?.icon" />
              <span class="ml-1 text-sm uppercase text-[#54829F]">{{
                item?.name
              }}</span>
            </a>
          </div>

          <div>
            <div class="dropdown dropdown-hover w-full hover:z-30">
              <label>
                <div
                  class="bg-[#1F1F22] flex items-center justify-between px-4 py-2 cursor-pointer rounded"
                >
                  <div>
                    <div class="text-xl font-semibold text-[#FFFFFF]">
                      ${{ ticker?.converted_last?.usd }}
                    </div>
                    <div class="text-sm" :class="store.priceColor">
                      {{ store.priceChange }}%
                    </div>
                  </div>

                  <div class="text-right">
                    <div class="text-[#FFFFFF] text-sm">
                      {{ shortName(ticker?.base, ticker?.coin_id) }}/{{
                        shortName(ticker?.target, ticker?.target_coin_id)
                      }}
                    </div>
                    <div class="font-semibold text-[#686868]">
                      {{ ticker?.market?.name || '' }}
                    </div>
                  </div>
                </div>
              </label>
              <div class="dropdown-content pt-1">
                <div class="h-64 overflow-auto w-full shadow rounded">
                  <ul class="menu w-full bg-[#1F1F22] rounded">
                    <li
                      v-for="(item, index) in store.coinInfo.tickers"
                      :key="index"
                      @click="store.selectTicker(index)"
                    >
                      <div
                        class="flex items-center justify-between hover:bg-base-100"
                      >
                        <div class="flex-1 text-[#FFFFFF]">
                          ${{ item?.converted_last?.usd }}
                        </div>

                        <div class="text-base text-main">
                          <div class="text-sm text-[#FFFFFF]">
                            {{ shortName(item?.base, item?.coin_id) }}/{{
                              shortName(item?.target, item?.target_coin_id)
                            }}
                          </div>
                          <div class="text-[#686868] text-sm">
                            {{ item?.market?.name }}
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="flex">
              <label class="btn btn-[#323232] !px-1 my-5 mr-2" for="calculator">
                <svg
                  class="w-8 h-8"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#8F8F8F"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    <rect x="4" y="2" width="16" height="20" rx="2"></rect>
                    <line x1="8" x2="16" y1="6" y2="6"></line>
                    <line x1="16" x2="16" y1="14" y2="18"></line>
                    <path d="M16 10h.01"></path>
                    <path d="M12 10h.01"></path>
                    <path d="M8 10h.01"></path>
                    <path d="M12 14h.01"></path>
                    <path d="M8 14h.01"></path>
                    <path d="M12 18h.01"></path>
                    <path d="M8 18h.01"></path>
                  </g>
                </svg>
              </label>
              <!-- Put this part before </body> tag -->
              <input type="checkbox" id="calculator" class="modal-toggle" />
              <div class="modal">
                <div class="modal-box">
                  <h3 class="text-lg font-bold">
                    {{ $t('index.price_calculator') }}
                  </h3>
                  <div class="flex flex-col w-full mt-5">
                    <div
                      class="grid h-20 flex-grow card rounded-box place-items-center"
                    >
                      <div class="join w-full">
                        <label class="join-item btn">
                          <span class="uppercase">{{ coinInfo.symbol }}</span>
                        </label>
                        <input
                          type="number"
                          v-model="qty"
                          min="0"
                          placeholder="Input a number"
                          class="input grow input-bordered join-item"
                        />
                      </div>
                    </div>
                    <div class="divider">=</div>
                    <div
                      class="grid h-20 flex-grow card rounded-box place-items-center"
                    >
                      <div class="join w-full">
                        <label class="join-item btn">
                          <span>USD</span>
                        </label>
                        <input
                          type="number"
                          v-model="amount"
                          min="0"
                          placeholder="Input amount"
                          class="join-item grow input input-bordered"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <label class="modal-backdrop" for="calculator">{{
                  $t('index.close')
                }}</label>
              </div>
              <a
                class="my-5 '!btn-[#334358] btn grow"
                :class="{
                  '!text-[#71FFB8]': store.trustColor === 'green',
                  '!text-warning': store.trustColor === 'yellow',
                }"
                :href="ticker.trade_url"
                target="_blank"
              >
                {{ $t('index.buy') }} {{ coinInfo.symbol || '' }}
              </a>
            </div>
          </div>
        </div>

        <div class="col-span-2">
          <!-- <PriceMarketChart /> -->
        </div>
      </div>
      <div class="h-[1px] w-full bg-[#384059]"></div>
    </div>

    <!-- <div class="grid grid-cols-1 gap-4 md:!grid-cols-3 lg:!grid-cols-6">
      <div v-for="(item, key) in store.stats" :key="key">
        <CardStatisticsVertical v-bind="item" />
      </div>
    </div> -->

    <div v-if="!store.coingeckoId" class="bg-base-100 rounded mt-4">
      <div class="px-4 pt-4 pb-2 text-lg font-semibold text-main">
        {{ $t('index.node_info') }}
      </div>
      <ArrayObjectElement
        :value="paramStore.nodeVersion?.items"
        :thead="false"
      />
      <div class="h-4"></div>
    </div>
  </div>
</template>

<route>
  {
    meta: {
      i18n: 'dashboard',
      order: 1,
    }
  }
</route>

<script lang="ts">
export default {
  data() {
    return {
      copied: false
    }
  },
  methods: {
    copyText() {
      //@ts-ignore
      const text = this.$refs.textToCopy.innerText;
      navigator.clipboard.writeText(text);
    }
  }
}

</script>
