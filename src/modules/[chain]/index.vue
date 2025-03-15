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

import ApexCharts from 'vue3-apexcharts';
import { getMarketPriceChartConfig } from '@/components/charts/apexChartConfig';
import { useBaseStore } from '@/stores';

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
    if(ticker.value !== undefined) {
      return quantity.value * ticker.value.converted_last.usd || 0;
    } else {
      return 0;
    }
  },
  set: (val) => {
    quantity.value = val / ticker.value.converted_last.usd || 0;
  },
});

const baseStore = useBaseStore();
const chartConfig = computed(() => {
  const theme = baseStore.theme;
  const labels = store.marketData.prices.map((item: any) => item[0]);
  return getMarketPriceChartConfig(theme, labels);
});

const kind = ref('price');
const series = computed(() => {
  return [
    {
      name: 'Price',
      data:
        kind.value === 'price'
          ? store.marketData.prices.map((item: any) => item[1])
          : store.marketData.total_volumes.map((item: any) => item[1]),
    },
  ];
});

function changeChart(type: string) {
  kind.value = type;
}
</script>

<template>
  <div>
    <!--Up-->
    <div class="flex flex-row gap-4 px-2">
      <div
        class="bg-black bg-opacity-50 border-[0.5rem] border-[#1C1C21] rounded-lg mt-4"
      >
        <div
          class="flex justify-between px-4 pt-4 pb-2 text-lg font-semibold text-[#FFFFFF]"
        >
          <div>
            <span ref="textToCopy" class="truncate">{{
              walletStore.currentAddress || 'Not Connected'
            }}</span>
            <div
              @click="copyText"
              class="btn rounded-full ml-3 h-1 scale-75 bg-[#1C1C21] hover:bg-[#0F334E] border-none indicator"
            >
              <span v-if="copied" class="indicator-item badge badge-success"
                >Copied</span
              >
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
          <div class="join border-[0.01rem] border-[#222226] w-full">
            <div class="join-item bg-[#0D110E] flex items-center px-2">
              <svg
                class="overflow-visible"
                width="25"
                height="25"
                viewBox="0 0 25 25"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M13.2552 8.98741C12.2182 9.50597 11.9359 10.0477 11.9359 10.3653C11.9359 10.6829 12.2182 11.2247 13.2552 11.7432C14.2356 12.2335 15.6558 12.564 17.2756 12.564C18.8954 12.564 20.3156 12.2335 21.2961 11.7432C22.333 11.2247 22.6154 10.6829 22.6154 10.3653C22.6154 10.0477 22.333 9.50597 21.2961 8.98741C20.3156 8.49714 18.8954 8.1666 17.2756 8.1666C15.6558 8.1666 14.2356 8.49714 13.2552 8.98741ZM12.4123 7.30181C13.7057 6.65503 15.4265 6.28198 17.2756 6.28198C19.1248 6.28198 20.8456 6.65503 22.139 7.30181C23.3758 7.9203 24.5 8.94905 24.5 10.3653C24.5 11.7816 23.3758 12.8103 22.139 13.4288C20.8456 14.0756 19.1248 14.4486 17.2756 14.4486C15.4265 14.4486 13.7057 14.0756 12.4123 13.4288C11.9538 13.1995 11.5107 12.9138 11.1347 12.5729C10.0038 12.9692 8.65576 13.1922 7.22436 13.1922C5.3752 13.1922 3.65439 12.8192 2.36102 12.1724C1.12421 11.5539 0 10.5252 0 9.10891C0 8.58848 0.421886 8.1666 0.942308 8.1666C1.46273 8.1666 1.88462 8.58848 1.88462 9.10891C1.88462 9.42649 2.16696 9.96825 3.20394 10.4868C4.18436 10.9771 5.60457 11.3076 7.22436 11.3076C8.29375 11.3076 9.28034 11.1636 10.1113 10.9222C10.0721 10.7438 10.0513 10.5582 10.0513 10.3653C10.0513 8.94905 11.1755 7.9203 12.4123 7.30181ZM0.942308 12.564C1.46273 12.564 1.88462 12.9859 1.88462 13.5063C1.88462 13.8239 2.16696 14.3657 3.20394 14.8842C4.18436 15.3745 5.60457 15.7051 7.22436 15.7051C8.26879 15.7051 9.23366 15.5677 10.0528 15.3363C10.0812 14.8413 10.4915 14.4486 10.9936 14.4486C11.514 14.4486 11.9359 14.8705 11.9359 15.391C11.9359 15.7085 12.2182 16.2503 13.2552 16.7689C14.2356 17.2591 15.6558 17.5897 17.2756 17.5897C18.8954 17.5897 20.3156 17.2591 21.2961 16.7689C22.333 16.2503 22.6154 15.7085 22.6154 15.391C22.6154 14.8705 23.0373 14.4486 23.5577 14.4486C24.0781 14.4486 24.5 14.8705 24.5 15.391C24.5 16.8072 23.3758 17.836 22.139 18.4545C20.8456 19.1012 19.1248 19.4743 17.2756 19.4743C15.4265 19.4743 13.7057 19.1012 12.4123 18.4545C11.7519 18.1242 11.1236 17.677 10.6814 17.1163C9.65048 17.4209 8.4695 17.5897 7.22436 17.5897C5.3752 17.5897 3.65439 17.2166 2.36102 16.5698C1.12421 15.9514 0 14.9226 0 13.5063C0 12.9859 0.421886 12.564 0.942308 12.564Z"
                  fill="url(#paint0_linear_421_1114)"
                />
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M0.942308 3.14111C1.46273 3.14111 1.88462 3.563 1.88462 4.08342V17.9039C1.88462 18.2215 2.16696 18.7633 3.20394 19.2818C4.18436 19.7721 5.60457 20.1027 7.22436 20.1027C8.26813 20.1027 9.23243 19.9655 10.0513 19.7343V10.3655C10.0513 9.84505 10.4732 9.42316 10.9936 9.42316C11.514 9.42316 11.9359 9.84505 11.9359 10.3655V20.4168C11.9359 20.7343 12.2182 21.2761 13.2552 21.7947C14.2356 22.2849 15.6558 22.6155 17.2756 22.6155C18.8954 22.6155 20.3156 22.2849 21.2961 21.7947C22.333 21.2761 22.6154 20.7343 22.6154 20.4168V10.3655C22.6154 9.84505 23.0373 9.42316 23.5577 9.42316C24.0781 9.42316 24.5 9.84505 24.5 10.3655V20.4168C24.5 21.833 23.3758 22.8618 22.139 23.4803C20.8456 24.127 19.1248 24.5001 17.2756 24.5001C15.4265 24.5001 13.7057 24.127 12.4123 23.4803C11.5544 23.0513 10.7507 22.4249 10.3388 21.6087C9.39203 21.8533 8.33365 21.9873 7.22436 21.9873C5.3752 21.9873 3.65439 21.6142 2.36102 20.9674C1.12421 20.349 0 19.3202 0 17.9039V4.08342C0 3.563 0.421886 3.14111 0.942308 3.14111ZM13.5064 3.14111C14.0268 3.14111 14.4487 3.563 14.4487 4.08342V7.85265C14.4487 8.37307 14.0268 8.79496 13.5064 8.79496C12.986 8.79496 12.5641 8.37307 12.5641 7.85265V4.08342C12.5641 3.563 12.986 3.14111 13.5064 3.14111Z"
                  fill="url(#paint1_linear_421_1114)"
                />
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M3.20394 2.70543C2.16696 3.22399 1.88462 3.76575 1.88462 4.08333C1.88462 4.40091 2.16696 4.94268 3.20394 5.46124C4.18436 5.95151 5.60457 6.28205 7.22436 6.28205C8.84415 6.28205 10.2644 5.95151 11.2448 5.46124C12.2818 4.94268 12.5641 4.40091 12.5641 4.08333C12.5641 3.76575 12.2818 3.22399 11.2448 2.70543C10.2644 2.21515 8.84415 1.88462 7.22436 1.88462C5.60457 1.88462 4.18436 2.21515 3.20394 2.70543ZM2.36102 1.01983C3.65439 0.373051 5.3752 0 7.22436 0C9.07352 0 10.7943 0.373051 12.0877 1.01983C13.3245 1.63832 14.4487 2.66707 14.4487 4.08333C14.4487 5.4996 13.3245 6.52835 12.0877 7.14684C10.7943 7.79362 9.07352 8.16667 7.22436 8.16667C5.3752 8.16667 3.65439 7.79362 2.36102 7.14684C1.12421 6.52835 0 5.4996 0 4.08333C0 2.66707 1.12421 1.63832 2.36102 1.01983Z"
                  fill="url(#paint2_linear_421_1114)"
                />
                <defs>
                  <linearGradient
                    id="paint0_linear_421_1114"
                    x1="12"
                    y1="6.82044"
                    x2="12.0725"
                    y2="19.4753"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop stop-color="#3FB6A8" />
                    <stop offset="1" stop-color="#1C504A" />
                  </linearGradient>
                  <linearGradient
                    id="paint1_linear_421_1114"
                    x1="12"
                    y1="4.01291"
                    x2="12.19"
                    y2="24.5006"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop stop-color="#3FB6A8" />
                    <stop offset="1" stop-color="#1C504A" />
                  </linearGradient>
                  <linearGradient
                    id="paint2_linear_421_1114"
                    x1="10"
                    y1="-1.03036e-07"
                    x2="9.62865"
                    y2="28.9952"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop stop-color="#3FB6A8" />
                    <stop offset="1" stop-color="#1C504A" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div
              class="join-item rounded-lg bg-black bg-opacity-50 px-4 py-3 flex-1"
            >
              <div class="flex justify-between">
                <div class="text-sm mb-1 text-[#71FFB8] uppercase">
                  {{ $t('account.balance') }}
                </div>
                <div class="text-sm" :class="color">
                  ${{ format.tokenValue(walletStore.balanceOfStakingToken) }}
                </div>
              </div>
              <div class="text-lg font-semibold text-[#FFFFFF]">
                {{ format.formatToken(walletStore.balanceOfStakingToken) }}
              </div>
            </div>
          </div>
          <div class="join border-[0.01rem] border-[#222226] w-full">
            <div class="join-item bg-[#0D110E] flex items-center px-2">
              <svg
                class="overflow-visible"
                width="25"
                height="25"
                viewBox="0 0 25 25"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M2.61326 0.718446C3.97274 0.265339 5.79595 0 7.77035 0C9.74475 0 11.568 0.265339 12.9274 0.718446C13.6027 0.943496 14.2114 1.23053 14.669 1.59126C15.117 1.94437 15.5407 2.46989 15.5407 3.1657C15.5407 3.8615 15.117 4.38703 14.669 4.74014C14.2114 5.10086 13.6027 5.3879 12.9274 5.61295C11.568 6.06606 9.74475 6.3314 7.77035 6.3314C5.79595 6.3314 3.97274 6.06606 2.61326 5.61295C1.93803 5.3879 1.3293 5.10086 0.871652 4.74014C0.423664 4.38703 0 3.8615 0 3.1657C0 2.46989 0.423664 1.94437 0.871652 1.59126C1.3293 1.23053 1.93803 0.943496 2.61326 0.718446ZM1.72482 3.18506C1.72475 3.18506 1.72493 3.18408 1.72554 3.18214C1.72519 3.1841 1.72488 3.18507 1.72482 3.18506ZM1.73261 3.1657C1.74931 3.13285 1.79929 3.05874 1.94057 2.94738C2.18189 2.75717 2.5846 2.54813 3.15925 2.3566C4.29952 1.97655 5.92979 1.72674 7.77035 1.72674C9.6109 1.72674 11.2412 1.97655 12.3815 2.3566C12.9561 2.54813 13.3588 2.75717 13.6001 2.94738C13.7414 3.05874 13.7914 3.13285 13.8081 3.1657C13.7914 3.19854 13.7414 3.27266 13.6001 3.38401C13.3588 3.57423 12.9561 3.78327 12.3815 3.9748C11.2412 4.35484 9.6109 4.60465 7.77035 4.60465C5.92979 4.60465 4.29952 4.35484 3.15925 3.9748C2.5846 3.78327 2.18189 3.57423 1.94057 3.38401C1.79929 3.27265 1.74931 3.19854 1.73261 3.1657ZM13.8159 3.18506C13.8158 3.18507 13.8155 3.18409 13.8152 3.18213C13.8158 3.18408 13.8159 3.18506 13.8159 3.18506ZM13.8152 3.14926C13.8155 3.1473 13.8158 3.14633 13.8159 3.14633C13.8159 3.14634 13.8158 3.14731 13.8152 3.14926ZM1.72554 3.14926C1.72493 3.14732 1.72475 3.14634 1.72482 3.14633C1.72488 3.14633 1.72519 3.1473 1.72554 3.14926ZM10.5026 10.5026C12.0678 8.93744 14.1906 8.05814 16.4041 8.05814C18.6175 8.05814 20.7404 8.93744 22.3055 10.5026C23.8707 12.0678 24.75 14.1906 24.75 16.4041C24.75 18.6175 23.8707 20.7404 22.3055 22.3055C20.7404 23.8707 18.6175 24.75 16.4041 24.75C14.1906 24.75 12.0678 23.8707 10.5026 22.3055C8.93744 20.7404 8.05814 18.6175 8.05814 16.4041C8.05814 14.1906 8.93744 12.0678 10.5026 10.5026ZM16.4041 9.78488C14.6486 9.78488 12.9649 10.4823 11.7236 11.7236C10.4823 12.9649 9.78488 14.6486 9.78488 16.4041C9.78488 18.1596 10.4823 19.8432 11.7236 21.0845C12.9649 22.3259 14.6486 23.0233 16.4041 23.0233C18.1596 23.0233 19.8432 22.3259 21.0845 21.0845C22.3259 19.8432 23.0233 18.1596 23.0233 16.4041C23.0233 14.6486 22.3259 12.9649 21.0845 11.7236C19.8432 10.4823 18.1596 9.78488 16.4041 9.78488Z"
                  fill="#3FB6A8"
                />
                <path
                  fill-rule="evenodd"
                  clip-rule="evenodd"
                  d="M0.863372 2.30225C1.3402 2.30225 1.72674 2.68879 1.72674 3.16562V7.89313C2.90672 8.80623 5.0175 9.27829 7.48716 9.27829C7.96399 9.27829 8.35053 9.66484 8.35053 10.1417C8.35053 10.6185 7.96399 11.005 7.48716 11.005C5.4257 11.005 3.32932 10.7019 1.72674 9.91127V12.404C1.7327 12.4125 1.79845 12.6271 2.37383 12.9352C3.00934 13.2756 4.08278 13.6164 5.72419 13.8205C6.19738 13.8793 6.53328 14.3106 6.47445 14.7838C6.41562 15.2569 5.98434 15.5929 5.51116 15.534C3.75434 15.3156 2.45063 14.9352 1.55855 14.4574C0.721038 14.0088 0 13.3286 0 12.4244V3.16562C0 2.68879 0.386545 2.30225 0.863372 2.30225ZM14.6635 2.44154C15.1403 2.44154 15.5269 2.82808 15.5269 3.30491V5.6245C15.5269 6.10133 15.1403 6.48787 14.6635 6.48787C14.1867 6.48787 13.8001 6.10133 13.8001 5.6245V3.30491C13.8001 2.82808 14.1867 2.44154 14.6635 2.44154ZM15.8932 11.6164C16.0229 11.5644 16.1948 11.5115 16.4041 11.5115C16.6133 11.5115 16.7852 11.5644 16.9149 11.6164C17.0187 11.658 17.131 11.7145 17.2234 11.7611C17.232 11.7654 17.2405 11.7697 17.2488 11.7739L17.2527 11.7758L19.0525 12.6919C19.0701 12.7008 19.0883 12.7101 19.1059 12.719C19.4598 12.8986 19.8065 13.0746 20.0577 13.2525C20.3198 13.4382 20.7209 13.7938 20.7209 14.3895V18.4185C20.7209 19.0141 20.3198 19.3698 20.0577 19.5555C19.8065 19.7334 19.4598 19.9094 19.1059 20.089C19.0883 20.0979 19.0707 20.1069 19.0531 20.1158L17.2488 21.0341C17.2405 21.0383 17.232 21.0426 17.2233 21.0469C17.1309 21.0935 17.0186 21.15 16.9149 21.1916C16.7852 21.2436 16.6133 21.2964 16.4041 21.2964C16.1948 21.2964 16.0229 21.2436 15.8932 21.1916C15.7895 21.15 15.6772 21.0935 15.5848 21.0469C15.5761 21.0426 15.5677 21.0383 15.5594 21.0341L15.5554 21.0321L13.7556 20.1161C13.738 20.1072 13.7198 20.0979 13.7022 20.089C13.3484 19.9094 13.0016 19.7334 12.7504 19.5555C12.4883 19.3698 12.0872 19.0141 12.0872 18.4185V14.3895C12.0872 13.7944 12.4876 13.4384 12.7501 13.2523C13.0036 13.0726 13.3537 12.8953 13.7108 12.7146C13.7257 12.707 13.7406 12.6995 13.7555 12.6919C13.7552 12.6921 13.7559 12.6918 13.7555 12.6919L15.5594 11.7739C15.5676 11.7697 15.5761 11.7654 15.5848 11.7611C15.6772 11.7145 15.7895 11.658 15.8932 11.6164ZM14.2277 14.3893C14.3198 14.3418 14.422 14.29 14.5367 14.2318L14.5382 14.2311L16.3348 13.3167L16.3387 13.3147L16.3485 13.3098C16.3689 13.2995 16.3873 13.2903 16.4041 13.2819C16.4209 13.2903 16.4392 13.2995 16.4597 13.3098L16.4695 13.3147L16.4734 13.3167L18.2699 14.2311C18.3849 14.2895 18.4879 14.3418 18.5801 14.3895C18.4879 14.4371 18.3855 14.4891 18.2705 14.5475L16.4734 15.4622L16.4695 15.4642L16.4597 15.4691C16.4392 15.4794 16.4209 15.4886 16.4041 15.497C16.3873 15.4886 16.3689 15.4794 16.3485 15.4691L16.3387 15.4642L16.3348 15.4622L14.5382 14.5478C14.4231 14.4894 14.32 14.437 14.2277 14.3893ZM18.9942 16.1167L17.2674 16.9956V19.0871L18.2699 18.5769C18.4725 18.474 18.6366 18.3907 18.7741 18.3162C18.8687 18.2651 18.9401 18.2238 18.9942 18.1898V16.1167ZM15.5407 19.0871L14.5382 18.5769C14.3356 18.474 14.1716 18.3907 14.034 18.3162C13.9394 18.2651 13.868 18.2238 13.814 18.1898V16.1167L15.5407 16.9956V19.0871Z"
                  fill="#3FB6A8"
                />
              </svg>
            </div>
            <div
              class="join-item rounded-lg bg-black bg-opacity-50 px-4 py-3 flex-1"
            >
              <div class="flex justify-between">
                <div class="text-sm mb-1 text-[#71FFB8] uppercase">
                  {{ $t('module.staking') }}
                </div>
                <div class="text-sm" :class="color">
                  ${{ format.tokenValue(walletStore.stakingAmount) }}
                </div>
              </div>
              <div class="text-lg font-semibold text-[#FFFFFF]">
                {{ format.formatToken(walletStore.stakingAmount) }}
              </div>
            </div>
          </div>
          <div class="join border-[0.01rem] border-[#222226] w-full">
            <div class="join-item bg-[#0D110E] flex items-center px-2">
              <svg
                class="overflow-visible"
                width="25"
                height="20"
                viewBox="0 0 25 20"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M23.9883 12.1938C23.6783 11.9552 23.3174 11.7913 22.9337 11.7149C22.5501 11.6385 22.154 11.6515 21.7762 11.7531L17.4187 12.7552C17.5201 12.3269 17.5232 11.8811 17.4278 11.4514C17.3325 11.0217 17.1411 10.6191 16.8681 10.2739C16.5951 9.92865 16.2475 9.64971 15.8513 9.45796C15.4552 9.2662 15.0208 9.16662 14.5807 9.16667H9.36703C8.9292 9.16557 8.49548 9.25126 8.09095 9.41879C7.68641 9.58632 7.31908 9.83236 7.01017 10.1427L4.65436 12.5H1.66636C1.22441 12.5 0.800569 12.6756 0.488066 12.9882C0.175563 13.3007 0 13.7246 0 14.1667L0 18.3333C0 18.7754 0.175563 19.1993 0.488066 19.5118C0.800569 19.8244 1.22441 20 1.66636 20H12.4977C12.5658 20 12.6337 19.9916 12.6998 19.975L19.3652 18.3083C19.4077 18.2982 19.4492 18.2842 19.4891 18.2667L23.5374 16.5438L23.5832 16.5229C23.9722 16.3285 24.3054 16.0382 24.5513 15.6793C24.7972 15.3205 24.9477 14.905 24.9886 14.4719C25.0296 14.0388 24.9596 13.6024 24.7853 13.2039C24.6111 12.8053 24.3382 12.4577 23.9925 12.1938H23.9883ZM1.66636 14.1667H4.1659V18.3333H1.66636V14.1667ZM22.8531 15.0219L18.8955 16.7073L12.3936 18.3333H5.83226V13.6781L8.18912 11.3219C8.3433 11.1664 8.52683 11.0432 8.72904 10.9593C8.93126 10.8755 9.14812 10.8326 9.36703 10.8333H14.5807C14.9121 10.8333 15.23 10.965 15.4644 11.1995C15.6988 11.4339 15.8304 11.7518 15.8304 12.0833C15.8304 12.4149 15.6988 12.7328 15.4644 12.9672C15.23 13.2016 14.9121 13.3333 14.5807 13.3333H11.6645C11.4436 13.3333 11.2316 13.4211 11.0754 13.5774C10.9191 13.7337 10.8313 13.9457 10.8313 14.1667C10.8313 14.3877 10.9191 14.5996 11.0754 14.7559C11.2316 14.9122 11.4436 15 11.6645 15H14.9973C15.06 14.9998 15.1225 14.9929 15.1837 14.9792L22.1616 13.374L22.1938 13.3656C22.4069 13.3065 22.6342 13.3282 22.8322 13.4266C23.0301 13.5251 23.1847 13.6933 23.2661 13.8988C23.3476 14.1044 23.3501 14.3328 23.2733 14.5401C23.1965 14.7475 23.0457 14.919 22.85 15.0219H22.8531ZM17.0802 7.5C17.2861 7.50023 17.4916 7.48351 17.6947 7.45C17.9231 8.12869 18.3411 8.72777 18.8992 9.1764C19.4572 9.62503 20.1321 9.90446 20.8439 9.98165C21.5557 10.0588 22.2748 9.93055 22.916 9.61196C23.5572 9.29338 24.0939 8.79781 24.4624 8.18386C24.831 7.5699 25.0161 6.86323 24.9958 6.1474C24.9756 5.43156 24.7508 4.73649 24.3481 4.14437C23.9454 3.55225 23.3816 3.08784 22.7234 2.80604C22.0652 2.52424 21.34 2.43684 20.6337 2.55417C20.4137 1.90026 20.0177 1.31972 19.4891 0.876436C18.9605 0.433154 18.3199 0.144316 17.6378 0.0417064C16.9556 -0.0609028 16.2584 0.026695 15.6228 0.29486C14.9873 0.563025 14.438 1.00136 14.0355 1.56163C13.6329 2.1219 13.3927 2.78238 13.3413 3.47039C13.2898 4.1584 13.4292 4.84727 13.7439 5.46118C14.0587 6.07509 14.5367 6.59025 15.1253 6.94997C15.714 7.30969 16.3904 7.50001 17.0802 7.5ZM23.3291 6.25C23.3291 6.66205 23.2069 7.06484 22.978 7.40744C22.7491 7.75004 22.4238 8.01707 22.0432 8.17475C21.6626 8.33243 21.2438 8.37369 20.8397 8.2933C20.4357 8.21292 20.0645 8.0145 19.7732 7.72314C19.4819 7.43178 19.2835 7.06057 19.2032 6.65644C19.1228 6.25231 19.1641 5.83342 19.3217 5.45274C19.4794 5.07206 19.7463 4.74669 20.0889 4.51777C20.4314 4.28885 20.8341 4.16667 21.2461 4.16667C21.7985 4.16667 22.3283 4.38616 22.719 4.77686C23.1096 5.16756 23.3291 5.69747 23.3291 6.25ZM17.0802 1.66667C17.5346 1.6669 17.9765 1.81574 18.3384 2.0905C18.7004 2.36526 18.9626 2.75087 19.085 3.18854C18.6583 3.48885 18.299 3.87494 18.03 4.3221C17.761 4.76927 17.5882 5.26767 17.5228 5.78542C17.3774 5.81685 17.229 5.83291 17.0802 5.83333C16.5278 5.83333 15.998 5.61384 15.6073 5.22314C15.2167 4.83244 14.9973 4.30254 14.9973 3.75C14.9973 3.19747 15.2167 2.66756 15.6073 2.27686C15.998 1.88616 16.5278 1.66667 17.0802 1.66667Z"
                  fill="#3FB6A8"
                />
              </svg>
            </div>
            <div
              class="join-item rounded-lg bg-black bg-opacity-50 px-4 py-3 flex-1"
            >
              <div class="flex justify-between">
                <div class="text-sm mb-1 text-[#71FFB8] uppercase">
                  {{ $t('index.reward') }}
                </div>
                <div class="text-sm" :class="color">
                  ${{ format.tokenValue(walletStore.rewardAmount) }}
                </div>
              </div>
              <div class="text-lg font-semibold text-[#FFFFFF]">
                {{ format.formatToken(walletStore.rewardAmount) }}
              </div>
            </div>
          </div>
          <div class="join border-[0.01rem] border-[#222226] w-full">
            <div class="join-item bg-[#0D110E] flex items-center px-2">
              <svg
                class="overflow-visible"
                width="19"
                height="25"
                viewBox="0 0 19 25"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16.625 22.619V10.7143H2.375V22.619H16.625ZM16.625 8.33333C17.2549 8.33333 17.859 8.58418 18.3044 9.0307C18.7498 9.47721 19 10.0828 19 10.7143V22.619C19 23.2505 18.7498 23.8561 18.3044 24.3026C17.859 24.7491 17.2549 25 16.625 25H2.375C1.74511 25 1.14102 24.7491 0.695621 24.3026C0.250222 23.8561 0 23.2505 0 22.619V10.7143C0 10.0828 0.250222 9.47721 0.695621 9.0307C1.14102 8.58418 1.74511 8.33333 2.375 8.33333H13.0625V5.95238C13.0625 5.00518 12.6872 4.09677 12.0191 3.427C11.351 2.75723 10.4448 2.38095 9.5 2.38095C8.55517 2.38095 7.64903 2.75723 6.98093 3.427C6.31283 4.09677 5.9375 5.00518 5.9375 5.95238H3.5625C3.5625 4.37371 4.18806 2.8597 5.30155 1.74341C6.41505 0.627124 7.92528 0 9.5 0C10.2797 0 11.0518 0.153963 11.7722 0.453098C12.4926 0.752233 13.1471 1.19068 13.6984 1.74341C14.2498 2.29614 14.6871 2.95233 14.9855 3.6745C15.2839 4.39668 15.4375 5.1707 15.4375 5.95238V8.33333H16.625ZM9.5 19.0476C8.87011 19.0476 8.26602 18.7968 7.82062 18.3503C7.37522 17.9037 7.125 17.2981 7.125 16.6667C7.125 16.0352 7.37522 15.4296 7.82062 14.9831C8.26602 14.5366 8.87011 14.2857 9.5 14.2857C10.1299 14.2857 10.734 14.5366 11.1794 14.9831C11.6248 15.4296 11.875 16.0352 11.875 16.6667C11.875 17.2981 11.6248 17.9037 11.1794 18.3503C10.734 18.7968 10.1299 19.0476 9.5 19.0476Z"
                  fill="#3FB6A8"
                />
              </svg>
            </div>
            <div
              class="join-item rounded-lg bg-black bg-opacity-50 px-4 py-3 flex-1"
            >
              <div class="flex justify-between">
                <div class="text-sm mb-1 text-[#71FFB8] uppercase">
                  {{ $t('index.unbonding') }}
                </div>
                <div class="text-sm" :class="color">
                  ${{ format.tokenValue(walletStore.unbondingAmount) }}
                </div>
              </div>
              <div class="text-lg font-semibold text-[#FFFFFF]">
                {{ format.formatToken(walletStore.unbondingAmount) }}
              </div>
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
                            validator_address:
                              item.delegation.validator_address,
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
                            validator_address:
                              item.delegation.validator_address,
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
      <div
        class="border-[0.5rem] border-[#17393D] rounded-lg mt-4 w-2/6 px-10 bg-black bg-opacity-50"
      >
        <h3 class="text-lg font-bold text-[#71FFB8] uppercase mt-4">
          {{ $t('index.price_calculator') }}
        </h3>
        <div class="flex flex-col w-full mt-1">
          <div class="geid h-20 flex-grow card rounded-box place-item-center">
            <div class="w-full">
              <label
                class="btn border-2 rounded-full bg-[#0D0D11] hover:bg-[#0F334E] text-white text-opacity-75"
              >
                <span class="uppercase">{{ coinInfo.symbol }}</span>
              </label>
              <input
              type="number"
              v-model="qty"
              min="0"
              placeholder="Input a number"
              class="grow input input-ghost text-white text-opacity-75 ml-4 focus:bg-[#0F334E] focus:border-2 focus:border-white focus:text-white focus:text-opacity-75"
              />  
            </div>
          </div>
          <div class="divider">=</div>
          <div class="flex h-20 flex-grow card rounded-box items-center">
            <div class="w-full">
              <label class="btn border-2 rounded-full bg-[#0D0D11] hover:bg-[#0F334E] text-white text-opacity-75">
                <span>USD</span>
              </label>
              <input
                type="number"
                v-model="amount"
                min="0"
                placeholder="Input amount"
                class="grow input input-ghost text-white text-opacity-75 ml-4 focus:bg-[#0F334E] focus:border-2 focus:border-white focus:text-white focus:text-opacity-75"
              />
            </div>
          </div>
        </div>
      </div>
      <!-- <div class="border-[0.5rem] border-[#17393D] rounded-lg mt-4 w-2/6 px-10 bg-black bg-opacity-50">
        <h3 class="text-lg font-bold text-[#71FFB8] uppercase mt-4">
          {{ $t('index.price_calculator') }}
        </h3>
        <div class="flex flex-col w-full mt-1">
          <div class="grid h-20 flex-grow card rounded-box place-items-center">
            <div class="w-full">
              <label class="btn border-2 rounded-full bg-[#0D0D11] hover:bg-[#0F334E] text-white text-opacity-75">
                <span class="uppercase">{{ coinInfo.symbol }}</span>
              </label>
              <input
                type="number"
                v-model="qty"
                min="0"
                placeholder="Input a number"
                class="grow input input-ghost text-white text-opacity-75 ml-4 focus:bg-[#0F334E] focus:border-2 focus:border-white focus:text-white focus:text-opacity-75"
              />
            </div>
          </div>
          <div class="divider">=</div>
          <div class="grid h-20 flex-grow card rounded-box place-items-center">
            <div class="w-full">
              <label class="btn border-2 rounded-full bg-[#0D0D11] hover:bg-[#0F334E] text-white text-opacity-75">
                <span>USD</span>
              </label>
              <input
                type="number"
                v-model="amount"
                min="0"
                placeholder="Input amount"
                class="grow input input-ghost text-white text-opacity-75 ml-4 focus:bg-[#0F334E] focus:border-2 focus:border-white focus:text-white focus:text-opacity-75"
              />
            </div>
          </div>
        </div>
      </div> -->
    </div>

    <!--Down-->
    <div
      v-if="coinInfo && coinInfo.name"
      class="bg-black bg-opacity-50 shadow border-[0.5rem] border-[#1C1C21] rounded-lg mt-4 flex flex-col"
    >
      <div class="px-4 h-1/5">
        <div class="py-5">
          <div class="flex flex-row justify-between">
            <div class="flex flex-row items-center">
              <div class="text-xl font-semibold text-[#71FFB8] uppercase">
                {{ coinInfo.name }}
              </div>
              <div class="flex flex-wrap ml-20">
                <a
                  v-for="(item, index) of comLinks"
                  :key="index"
                  :href="item.href"
                  class="bg-transparent border-none px-2 flex items-center"
                >
                  <Icon class="text-[#686868]" :icon="item?.icon" />
                  <span
                    class="link link-hover ml-1 text-sm uppercase text-[#54829F]"
                    >{{ item?.name }}</span
                  >
                </a>
              </div>
            </div>
            <div class="tabs tabs-boxed bg-transparent">
              <a
                class="tab text-xs mr-2 text-[#FFFFFF] uppercase bg-[#131315] rounded-full w-[10rem]"
                :class="{
                  'tab-active bg-[#0D1A24]': kind === 'price',
                }"
                @click="changeChart('price')"
              >
                Price
              </a>
              <a
                class="tab text-xs text-[#FFFFFF] uppercase bg-[#131315] rounded-full w-[10rem]"
                :class="{
                  'tab-active bg-[#0D1A24]': kind === 'volume',
                }"
                @click="changeChart('volume')"
              >
                Volume
              </a>
            </div>
          </div>
          <div class="text-xs mt-2 text-[#686868] mb-4">
            {{ $t('index.rank') }}:
            <div
              class="badge text-xs badge-error bg-[#33583B] dark:bg-[#33583B] text-green-400"
            >
              #{{ coinInfo.market_cap_rank }}
            </div>
          </div>
          <div class="flex w-full">
            <div class="w-1/5 flex flex-col justify-center">
              <div class="dropdown dropdown-hover w-full hover:z-30">
                <label>
                  <div
                    class="bg-black bg-opacity-50 border-[0.01rem] border-[#686868] flex items-center justify-between px-4 py-2 cursor-pointer rounded"
                  >
                    <div>
                      <div class="text-[#FFFFFF] text-sm">
                        {{ shortName(ticker?.base, ticker?.coin_id) }}/{{
                          shortName(ticker?.target, ticker?.target_coin_id)
                        }}
                      </div>
                      <div class="text-xl font-semibold text-[#FFFFFF]">
                        ${{ ticker?.converted_last?.usd }}
                      </div>
                      <div class="text-sm" :class="store.priceColor">
                        {{ store.priceChange }}%
                      </div>
                    </div>
                    <div class="font-semibold text-[#686868] mb-10">
                      {{ ticker?.market?.name || '' }}
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
                <!-- <label class="btn btn-[#323232] !px-1 my-5 mr-2" for="calculator">
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
                </label> -->

                <input type="checkbox" id="calculator" class="modal-toggle" />
                <a
                  class="my-5 border-none bg-[#0A2B0C] btn grow hover:bg-[#0D4410]"
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
            <div class="mb-5 bg-transparent flex-1">
              <ApexCharts
                type="area"
                height="230"
                :options="chartConfig"
                :series="series"
              />
            </div>
          </div>
        </div>
      </div>
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
      copied: false,
    };
  },
  methods: {
    copyText() {
      //@ts-ignore
      const text = this.$refs.textToCopy.innerText;
      navigator.clipboard.writeText(text).then(() => {
        this.copied = true;
        setTimeout(() => {
          this.copied = false;
        }, 3000);
      });
    },
  },
};
</script>

<!-- <div class="rounded-full bg-[#0D110E]">
  
</div> -->
