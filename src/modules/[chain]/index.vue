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
import { onMounted, ref, computed } from 'vue';
import { useIndexModule, colorMap } from './indexStore';

import CardStatisticsVertical from '@/components/CardStatisticsVertical.vue';
import ProposalListItem from '@/components/ProposalListItem.vue';
import ArrayObjectElement from '@/components/dynamic/ArrayObjectElement.vue';
import AddressWithCopy from '@/components/AddressWithCopy.vue';

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
    icon: 'mdi:web-box',
    href: store.homepage,
  },
  {
    name: 'Twitter',
    icon: 'prime:twitter',
    href: store.twitter,
  },
  {
    name: 'Telegram',
    icon: 'ic:baseline-telegram',
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

const coinStatisticsInfo = [
  {
    title: 'account.balance',
    icon: 'iconoir:coins',
    cost: 'balanceOfStakingToken',
  },
  {
    title: 'module.staking',
    cost: 'stakingAmount'
  },
  {
    title: 'index.reward',
    icon: 'ph:hand-coins-bold',
    cost: 'rewardAmount'
  },
  {
    title: 'index.unbonding',
    icon: 'lets-icons:unlock',
    cost: 'unbondingAmount'
  },
];

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
    <div v-if="coinInfo && coinInfo.name" class="flex flex-col gap-3 rounded shadow mb-4 mt-1.5 mx-0 md:mx-3">
      <!-- Top block -->
      <div class="grid grid-cols-2 xl:grid-cols-12 gap-3.5">

        <!-- Coin info -->
        <div class="col-span-2 xl:col-span-9 thick-border-block px-3 md:px-[30px] pt-5 pb-8">

          <div class="flex justify-center md:justify-between items-center mb-[50px] gap-6">
            <!-- address -->
            <AddressWithCopy :href="`/${chain}/account/${walletStore.currentAddress}`"
              :address="walletStore.currentAddress" icon outline />

            <!-- buttons panel -->
            <div class="grid grid-cols-3 gap-4">
              <label for="PingTokenConvert" class="btn-outline">{{
                $t('index.btn_swap')
              }}</label>
              <label for="send" class="btn-outline" @click="dialog.open('send', {}, walletStore.loadMyAsset)">{{
                $t('account.btn_send') }}</label>
              <label for="delegate" class="btn-outline" @click="dialog.open('delegate', {}, walletStore.loadMyAsset)">{{
                $t('account.btn_delegate') }}</label>
              <RouterLink to="/wallet/receive" class="btn !bg-info !border-info text-white hidden">{{
                $t('index.receive') }}
              </RouterLink>
            </div>
          </div>

          <div class="grid grid-cols-1 md:!grid-cols-2 xl:!grid-cols-4 auto-cols-auto gap-2.5">
            <div v-for="item in coinStatisticsInfo" class="flex border rounded border-[#222226] bg-black/50"
              :key="item.title">
              <div class="flex justify-center items-center bg-[#0D110E] rounded text-button-text h-full px-2">
                <Icon v-if="item.icon" :icon="item.icon" width="24" height="24" />
                <svg v-else width="25" height="25" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" clip-rule="evenodd"
                    d="M2.61326 0.718446C3.97274 0.265339 5.79595 0 7.77035 0C9.74475 0 11.568 0.265339 12.9274 0.718446C13.6027 0.943496 14.2114 1.23053 14.669 1.59126C15.117 1.94437 15.5407 2.46989 15.5407 3.1657C15.5407 3.8615 15.117 4.38703 14.669 4.74014C14.2114 5.10086 13.6027 5.3879 12.9274 5.61295C11.568 6.06606 9.74475 6.3314 7.77035 6.3314C5.79595 6.3314 3.97274 6.06606 2.61326 5.61295C1.93803 5.3879 1.3293 5.10086 0.871652 4.74014C0.423664 4.38703 0 3.8615 0 3.1657C0 2.46989 0.423664 1.94437 0.871652 1.59126C1.3293 1.23053 1.93803 0.943496 2.61326 0.718446ZM1.72482 3.18506C1.72475 3.18506 1.72493 3.18408 1.72554 3.18214C1.72519 3.1841 1.72488 3.18507 1.72482 3.18506ZM1.73261 3.1657C1.74931 3.13285 1.79929 3.05874 1.94057 2.94738C2.18189 2.75717 2.5846 2.54813 3.15925 2.3566C4.29952 1.97655 5.92979 1.72674 7.77035 1.72674C9.6109 1.72674 11.2412 1.97655 12.3815 2.3566C12.9561 2.54813 13.3588 2.75717 13.6001 2.94738C13.7414 3.05874 13.7914 3.13285 13.8081 3.1657C13.7914 3.19854 13.7414 3.27266 13.6001 3.38401C13.3588 3.57423 12.9561 3.78327 12.3815 3.9748C11.2412 4.35484 9.6109 4.60465 7.77035 4.60465C5.92979 4.60465 4.29952 4.35484 3.15925 3.9748C2.5846 3.78327 2.18189 3.57423 1.94057 3.38401C1.79929 3.27265 1.74931 3.19854 1.73261 3.1657ZM13.8159 3.18506C13.8158 3.18507 13.8155 3.18409 13.8152 3.18213C13.8158 3.18408 13.8159 3.18506 13.8159 3.18506ZM13.8152 3.14926C13.8155 3.1473 13.8158 3.14633 13.8159 3.14633C13.8159 3.14634 13.8158 3.14731 13.8152 3.14926ZM1.72554 3.14926C1.72493 3.14732 1.72475 3.14634 1.72482 3.14633C1.72488 3.14633 1.72519 3.1473 1.72554 3.14926ZM10.5026 10.5026C12.0678 8.93744 14.1906 8.05814 16.4041 8.05814C18.6175 8.05814 20.7404 8.93744 22.3055 10.5026C23.8707 12.0678 24.75 14.1906 24.75 16.4041C24.75 18.6175 23.8707 20.7404 22.3055 22.3055C20.7404 23.8707 18.6175 24.75 16.4041 24.75C14.1906 24.75 12.0678 23.8707 10.5026 22.3055C8.93744 20.7404 8.05814 18.6175 8.05814 16.4041C8.05814 14.1906 8.93744 12.0678 10.5026 10.5026ZM16.4041 9.78488C14.6486 9.78488 12.9649 10.4823 11.7236 11.7236C10.4823 12.9649 9.78488 14.6486 9.78488 16.4041C9.78488 18.1596 10.4823 19.8432 11.7236 21.0845C12.9649 22.3259 14.6486 23.0233 16.4041 23.0233C18.1596 23.0233 19.8432 22.3259 21.0845 21.0845C22.3259 19.8432 23.0233 18.1596 23.0233 16.4041C23.0233 14.6486 22.3259 12.9649 21.0845 11.7236C19.8432 10.4823 18.1596 9.78488 16.4041 9.78488Z"
                    fill="#3FB6A8" />
                  <path fill-rule="evenodd" clip-rule="evenodd"
                    d="M0.863372 2.30225C1.3402 2.30225 1.72674 2.68879 1.72674 3.16562V7.89313C2.90672 8.80623 5.0175 9.27829 7.48716 9.27829C7.96399 9.27829 8.35053 9.66484 8.35053 10.1417C8.35053 10.6185 7.96399 11.005 7.48716 11.005C5.4257 11.005 3.32932 10.7019 1.72674 9.91127V12.404C1.7327 12.4125 1.79845 12.6271 2.37383 12.9352C3.00934 13.2756 4.08278 13.6164 5.72419 13.8205C6.19738 13.8793 6.53328 14.3106 6.47445 14.7838C6.41562 15.2569 5.98434 15.5929 5.51116 15.534C3.75434 15.3156 2.45063 14.9352 1.55855 14.4574C0.721038 14.0088 0 13.3286 0 12.4244V3.16562C0 2.68879 0.386545 2.30225 0.863372 2.30225ZM14.6635 2.44154C15.1403 2.44154 15.5269 2.82808 15.5269 3.30491V5.6245C15.5269 6.10133 15.1403 6.48787 14.6635 6.48787C14.1867 6.48787 13.8001 6.10133 13.8001 5.6245V3.30491C13.8001 2.82808 14.1867 2.44154 14.6635 2.44154ZM15.8932 11.6164C16.0229 11.5644 16.1948 11.5115 16.4041 11.5115C16.6133 11.5115 16.7852 11.5644 16.9149 11.6164C17.0187 11.658 17.131 11.7145 17.2234 11.7611C17.232 11.7654 17.2405 11.7697 17.2488 11.7739L17.2527 11.7758L19.0525 12.6919C19.0701 12.7008 19.0883 12.7101 19.1059 12.719C19.4598 12.8986 19.8065 13.0746 20.0577 13.2525C20.3198 13.4382 20.7209 13.7938 20.7209 14.3895V18.4185C20.7209 19.0141 20.3198 19.3698 20.0577 19.5555C19.8065 19.7334 19.4598 19.9094 19.1059 20.089C19.0883 20.0979 19.0707 20.1069 19.0531 20.1158L17.2488 21.0341C17.2405 21.0383 17.232 21.0426 17.2233 21.0469C17.1309 21.0935 17.0186 21.15 16.9149 21.1916C16.7852 21.2436 16.6133 21.2964 16.4041 21.2964C16.1948 21.2964 16.0229 21.2436 15.8932 21.1916C15.7895 21.15 15.6772 21.0935 15.5848 21.0469C15.5761 21.0426 15.5677 21.0383 15.5594 21.0341L15.5554 21.0321L13.7556 20.1161C13.738 20.1072 13.7198 20.0979 13.7022 20.089C13.3484 19.9094 13.0016 19.7334 12.7504 19.5555C12.4883 19.3698 12.0872 19.0141 12.0872 18.4185V14.3895C12.0872 13.7944 12.4876 13.4384 12.7501 13.2523C13.0036 13.0726 13.3537 12.8953 13.7108 12.7146C13.7257 12.707 13.7406 12.6995 13.7555 12.6919C13.7552 12.6921 13.7559 12.6918 13.7555 12.6919L15.5594 11.7739C15.5676 11.7697 15.5761 11.7654 15.5848 11.7611C15.6772 11.7145 15.7895 11.658 15.8932 11.6164ZM14.2277 14.3893C14.3198 14.3418 14.422 14.29 14.5367 14.2318L14.5382 14.2311L16.3348 13.3167L16.3387 13.3147L16.3485 13.3098C16.3689 13.2995 16.3873 13.2903 16.4041 13.2819C16.4209 13.2903 16.4392 13.2995 16.4597 13.3098L16.4695 13.3147L16.4734 13.3167L18.2699 14.2311C18.3849 14.2895 18.4879 14.3418 18.5801 14.3895C18.4879 14.4371 18.3855 14.4891 18.2705 14.5475L16.4734 15.4622L16.4695 15.4642L16.4597 15.4691C16.4392 15.4794 16.4209 15.4886 16.4041 15.497C16.3873 15.4886 16.3689 15.4794 16.3485 15.4691L16.3387 15.4642L16.3348 15.4622L14.5382 14.5478C14.4231 14.4894 14.32 14.437 14.2277 14.3893ZM18.9942 16.1167L17.2674 16.9956V19.0871L18.2699 18.5769C18.4725 18.474 18.6366 18.3907 18.7741 18.3162C18.8687 18.2651 18.9401 18.2238 18.9942 18.1898V16.1167ZM15.5407 19.0871L14.5382 18.5769C14.3356 18.474 14.1716 18.3907 14.034 18.3162C13.9394 18.2651 13.868 18.2238 13.814 18.1898V16.1167L15.5407 16.9956V19.0871Z"
                    fill="#3FB6A8" />
                </svg>
              </div>

              <div class="grow px-2.5 pt-2 pb-4">
                <p class="uppercase header-14-medium-aa tracking-wide text-header-text mb-2">
                  {{ $t(item.title) }}
                </p>
                <p class="text-white header-20-medium-aa">
                  {{ format.formatToken((walletStore as any)[item.cost]) }}
                </p>
              </div>

              <p class="body-text-14 text-[#03F237] py-2 px-4">
                ${{ format.tokenValue((walletStore as any)[item.cost]) }}
              </p>

            </div>
          </div>
        </div>

        <!-- Price calculator -->
        <div
          class="col-span-2 xl:col-span-3 thick-border-block border-menu-button-active px-3.5 py-5 flex flex-col gap-3">
          <h3 class="header-20-medium-aa text-header-text tracking-wide uppercase mb-2 px-3">
            {{ $t('index.price_calculator') }}
          </h3>

          <div>
            <div class="flex gap-3.5 item-center header-20-medium-aa truncate">
              <label
                class="min-w-[104px] bg-[#0D0D11] border border-addition rounded-full flex justify-center items-center py-2 px-4">
                <span class="uppercase">{{ coinInfo.symbol }}</span>
              </label>
              <input type="number" v-model="qty" min="0" placeholder="Input a number" class="bg-transparent" />
            </div>
          </div>

          <div class="divider m-0 header-24 text-addition/50">=</div>

          <div class="flex gap-3.5 item-center header-20-medium-aa truncate">
            <label
              class="min-w-[104px] bg-[#0D0D11] border border-addition rounded-full flex justify-center items-center py-2 px-4">
              <span>USD</span>
            </label>
            <input type="number" v-model="amount" min="0" placeholder="Input amount" class="bg-transparent" />
          </div>
        </div>

      </div>

      <!-- Bottom block -->
      <div
        class="relative grid grid-cols-1 md:grid-cols-10 gap-5 thick-border-block p-3 md:pt-6 md:pb-8 md:px-5 h-full">
        <div
          class="w-full md:w-auto md:absolute xl:top-6 left-0 md:translate-x-1/2 my-0 flex md:flex-wrap justify-center items-center md:px-12">
          <a v-for="(item, index) of comLinks" :key="index" :href="item.href"
            class="link link-primary px-2 py-1 rounded-sm no-underline text-addition hover:text-addition flex items-center">
            <Icon :icon="item?.icon" class="w-6 h-6 md:w-4 md:h-4" />
            <span class="hidden md:block ml-1.5 text-sm capitalize text-[#54829F]">{{
              item?.name
            }}</span>
          </a>
        </div>

        <!-- Purchase coin -->
        <div class="col-span-1 md:col-span-3 xl:col-span-2">
          <div class="flex md:flex-col justify-between items-center md:items-start mb-4 gap-1">
            <div class="text-header-text header-20-medium-aa uppercase">
              {{ coinInfo.name }}
            </div>
            <div class="text-sm text-addition">
              {{ $t('index.rank') }}:
              <span class="bg-[#33583B] dark:bg-[#33583B] text-green-400 text-[10px] py-0.5 px-3 rounded-full">
                #{{ coinInfo.market_cap_rank }}
              </span>
            </div>
          </div>

          <div>
            <div class="dropdown dropdown-hover w-full hover:z-30 ">
              <label>
                <div class="w-full thin-border-block cursor-pointer">
                  <div class="w-full flex items-center justify-between">
                    <div class="text-addition body-text-16">
                      {{ shortName(ticker?.base, ticker?.coin_id) }}/{{
                        shortName(ticker?.target, ticker?.target_coin_id)
                      }}
                    </div>
                    <div class="font-semibold text-addition">
                      {{ ticker?.market?.name || '' }}
                    </div>
                  </div>

                  <div class="w-full">
                    <div class="header-24 tracking-wide text-[#FFFFFF]">
                      ${{ ticker?.converted_last?.usd }}
                    </div>
                    <div class="text-sm" :class="store.priceColor">
                      {{ store.priceChange }}%
                    </div>
                  </div>


                </div>
              </label>
              <div class="dropdown-content pt-1">
                <div class="h-64 overflow-auto w-full shadow rounded">
                  <ul class="menu w-full bg-[#1F1F22] rounded">
                    <li v-for="(item, index) in store.coinInfo.tickers" :key="index" @click="store.selectTicker(index)">
                      <div class="flex items-center justify-between hover:bg-base-100">
                        <div class="flex-1 text-[#FFFFFF]">
                          ${{ item?.converted_last?.usd }}
                        </div>

                        <div class="text-base text-main">
                          <div class="text-sm text-[#FFFFFF]">
                            {{ shortName(item?.base, item?.coin_id) }}/{{
                              shortName(item?.target, item?.target_coin_id)
                            }}
                          </div>
                          <div class="text-addition text-sm">
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
              <!-- Put this part before </body> tag -->
              <input type="checkbox" id="calculator" class="modal-toggle" />

              <div class="modal">
                <label class="modal-backdrop" for="calculator">{{
                  $t('index.close')
                }}</label>
              </div>
              <a class="header-16-medium my-2.5 py-1 grow bg-green-button hover:bg-green-button-hover rounded-full flex justify-center uppercase"
                :class="{
                  'text-header-text': store.trustColor === 'green',
                  '!text-warning': store.trustColor === 'yellow',
                }" :href="ticker.trade_url" target="_blank">
                {{ `${$t('index.buy')} ${coinInfo.symbol || ''} ` }}
              </a>
            </div>
          </div>
        </div>

        <!-- Price chart -->
        <div class="col-span-1 md:col-span-7 xl:col-span-8">
          <PriceMarketChart />
        </div>

      </div>
    </div>

    <!-- <div class="grid grid-cols-1 gap-4 md:!grid-cols-3 lg:!grid-cols-6">
      <div v-for="(item, key) in store.stats" :key="key">
        <CardStatisticsVertical v-bind="item" />
      </div>
    </div> -->

    <div class="bg-[#141415] rounded mt-4 shadow">

      <div v-if="walletStore.delegations.length > 0" class="px-4 pb-4 overflow-auto bg-[#141415]">
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
                <RouterLink class="link link-primary no-underline"
                  :to="`/${chain}/staking/${item?.delegation?.validator_address}`">
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
                  <label for="delegate" class="btn !btn-xs !btn-primary btn-ghost rounded-sm mr-2" @click="
                    dialog.open(
                      'delegate',
                      {
                        validator_address: item.delegation.validator_address,
                      },
                      updateState
                    )
                    ">
                    {{ $t('account.btn_delegate') }}
                  </label>
                  <label for="withdraw" class="btn !btn-xs !btn-primary btn-ghost rounded-sm" @click="
                    dialog.open(
                      'withdraw',
                      {
                        validator_address: item.delegation.validator_address,
                      },
                      updateState
                    )
                    ">
                    {{ $t('index.btn_withdraw_reward') }}
                  </label>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Teleport to="body">
        <ping-token-convert :chain-name="blockchain?.current?.prettyName" :endpoint="blockchain?.endpoint?.address"
          :hd-path="walletStore?.connectedWallet?.hdPath"></ping-token-convert>
      </Teleport>
    </div>

    <div v-if="!store.coingeckoId" class="bg-base-100 rounded mt-4">
      <div class="px-4 pt-4 pb-2 text-lg font-semibold text-main">
        {{ $t('index.node_info') }}
      </div>
      <ArrayObjectElement :value="paramStore.nodeVersion?.items" :thead="false" />
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
