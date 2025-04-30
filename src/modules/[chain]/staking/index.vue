<script lang="ts" setup>
import {
  useBaseStore,
  useBlockchain,
  useFormatter,
  useMintStore,
  useStakingStore,
  useTxDialog,
} from '@/stores';
import { computed } from '@vue/reactivity';
import { onMounted, ref } from 'vue';
import { Icon } from '@iconify/vue';
import type { Key, SlashingParam, Validator } from '@/types';
import { formatSeconds } from '@/libs/utils';
import IconTrendUp from '@/components/icons/IconTrendUp.vue';
import IconLock from '@/components/icons/IconLock.vue';
import IconHardSlashing from '@/components/icons/IconHardSlashing.vue';
import IconSoftSlashing from '@/components/icons/IconSoftSlashing.vue';
import IconAPR from '@/components/icons/IconAPR.vue';
import defaultAvatar from '@/assets/images/redesign/defaultAvatar.png';
import dayjs from 'dayjs';
import CircleProgressComponent from '@/components/CircleProgressComponent.vue';

const staking = useStakingStore();
const base = useBaseStore();
const format = useFormatter();
const dialog = useTxDialog();
const chainStore = useBlockchain();
const mintStore = useMintStore();

const cache = JSON.parse(localStorage.getItem('avatars') || '{}');
const avatars = ref(cache || {});
const latest = ref({} as Record<string, number>);
const yesterday = ref({} as Record<string, number>);
const tab = ref('active');
const unbondList = ref([] as Validator[]);
const slashing = ref({} as SlashingParam);

onMounted(() => {
  staking.fetchUnbondingValdiators().then((res) => {
    unbondList.value = res.concat(unbondList.value);
  });
  staking.fetchInacitveValdiators().then((res) => {
    unbondList.value = unbondList.value.concat(res);
  });
  chainStore.rpc.getSlashingParams().then((res) => {
    slashing.value = res.params;
  });
});

async function fetchChange() {
  let page = 0;

  let height = Number(base.latest?.block?.header?.height || 0);
  if (height > 14400) {
    height -= 14400;
  } else {
    height = 1;
  }
  // voting power in 24h ago
  while (page < staking.validators.length && height > 0) {
    await base.fetchValidatorByHeight(height, page).then((x) => {
      x.validators.forEach((v) => {
        yesterday.value[v.pub_key.key] = Number(v.voting_power);
      });
    });
    page += 100;
  }

  page = 0;
  // voting power for now
  while (page < staking.validators.length) {
    await base.fetchLatestValidators(page).then((x) => {
      x.validators.forEach((v) => {
        latest.value[v.pub_key.key] = Number(v.voting_power);
      });
    });
    page += 100;
  }
}

const changes = computed(() => {
  const changes = {} as Record<string, number>;
  Object.keys(latest.value).forEach((k) => {
    const l = latest.value[k] || 0;
    const y = yesterday.value[k] || 0;
    changes[k] = l - y;
  });
  return changes;
});

const change24 = (key: Key) => {
  const txt = key.key;
  // const n: number = latest.value[txt];
  // const o: number = yesterday.value[txt];
  // // console.log( txt, n, o)
  // return n > 0 && o > 0 ? n - o : 0;
  return changes.value[txt];
};

const change24Text = (key?: Key) => {
  if (!key) return '';
  const v = change24(key);
  return v && v !== 0 ? format.showChanges(v) : '';
};

const change24Color = (key?: Key) => {
  if (!key) return '';
  const v = change24(key);
  if (v > 0) return 'text-green-text';
  if (v < 0) return 'text-red-text';
};

const calculateRank = function (position: number) {
  let sum = 0;
  for (let i = 0; i < position; i++) {
    sum += Number(staking.validators[i]?.delegator_shares);
  }
  const percent = sum / staking.totalPower;

  switch (true) {
    case tab.value === 'active' && percent < 0.33:
      return 'error';
    case tab.value === 'active' && percent < 0.67:
      return 'warning';
    default:
      return 'primary';
  }
};

const calculateBg = function (rank: string) {
  switch (true) {
    case rank === 'error':
      return 'bg-[#33583B]';
    case rank === 'warning':
      return 'bg-[#334358]';
    default:
      return 'bg-primary';
  }
};

const calculateText = function (rank: string) {
  switch (true) {
    case rank === 'error':
      return 'tx-status-error';
    case rank === 'warning':
      return 'tx-status-warning';
    default:
      return 'tx-status-success';
  }
};

function isFeatured(
  endpoints: string[],
  who?: { website?: string; moniker: string }
) {
  if (!endpoints || !who) return false;
  return (
    endpoints.findIndex(
      (x) =>
        (who.website &&
          who.website
            ?.substring(0, who.website?.lastIndexOf('.'))
            .endsWith(x)) ||
        who?.moniker?.toLowerCase().search(x.toLowerCase()) > -1
    ) > -1
  );
}

const list = computed(() => {
  if (tab.value === 'active') {
    return staking.validators.map((x, i) => ({
      v: x,
      rank: calculateRank(i),
      logo: logo(x.description.identity),
    }));
  } else if (tab.value === 'featured') {
    const endpoint = chainStore.current?.endpoints?.rest?.map(
      (x) => x.provider
    );
    if (endpoint) {
      endpoint.push('ping');
      return staking.validators
        .filter((x) => isFeatured(endpoint, x.description))
        .map((x, i) => ({
          v: x,
          rank: 'primary',
          logo: logo(x.description.identity),
        }));
    }
    return [];
  }
  return unbondList.value.map((x, i) => ({
    v: x,
    rank: 'primary',
    logo: logo(x.description.identity),
  }));
});

const fetchAvatar = (identity: string) => {
  // fetch avatar from keybase
  return new Promise<void>((resolve) => {
    staking
      .keybase(identity)
      .then((d) => {
        if (Array.isArray(d.them) && d.them.length > 0) {
          const uri = String(d.them[0]?.pictures?.primary?.url).replace(
            'https://s3.amazonaws.com/keybase_processed_uploads/',
            ''
          );

          avatars.value[identity] = uri;
          resolve();
        } else throw new Error(`failed to fetch avatar for ${identity}`);
      })
      .catch((error) => {
        // console.error(error); // uncomment this if you want the user to see which avatars failed to load.
        resolve();
      });
  });
};

const loadAvatar = (identity: string) => {
  // fetches avatar from keybase and stores it in localStorage
  fetchAvatar(identity).then(() => {
    localStorage.setItem('avatars', JSON.stringify(avatars.value));
  });
};

const loadAvatars = () => {
  // fetches all avatars from keybase and stores it in localStorage
  const promises = staking.validators.map((validator) => {
    const identity = validator.description?.identity;

    // Here we also check whether we haven't already fetched the avatar
    if (identity && !avatars.value[identity]) {
      return fetchAvatar(identity);
    } else {
      return Promise.resolve();
    }
  });

  Promise.all(promises).then(() =>
    localStorage.setItem('avatars', JSON.stringify(avatars.value))
  );
};

const logo = (identity?: string) => {
  if (!identity || !avatars.value[identity]) return '';
  const url = avatars.value[identity] || '';
  return url.startsWith('http')
    ? url
    : `https://s3.amazonaws.com/keybase_processed_uploads/${url}`;
};

let height_in_24h = ref(0);
base.$subscribe((_, s) => {
  if (Number(s.earlest.block.header.height) !== height_in_24h.value) {
    height_in_24h.value = Number(s.earlest.block.header.height);
    fetchChange();
  }
});

const getMonthProgressPercent = (day: number) => {
  const now = dayjs();
  const daysInMonth = now.daysInMonth();

  const percent = (day / daysInMonth) * 100;
  return percent.toFixed(2);
}

loadAvatars();

const tabs = [
  {
    name: 'featured',
    value: 'staking.popular',
  },
  {
    name: 'active',
    value: 'staking.active',
  },
  {
    name: 'inactive',
    value: 'staking.inactive',
  },
  {
    name: 'jailed',
    value: 'staking.jailed',
  },
];

const widgetsInfo = computed(() => (
  [
    {
      name: 'staking.inflation',
      icon: IconTrendUp,
      numValue: +mintStore.inflation * 100,
      formattedValue: format.percent(mintStore.inflation),
    },
    {
      name: 'staking.unbonding_time',
      icon: IconLock,
      numValue: +getMonthProgressPercent(+formatSeconds(staking.params?.unbonding_time).replace(/days/, '')),
      formattedValue: formatSeconds(staking.params?.unbonding_time),
    },
    {
      name: 'staking.apr',
      icon: IconAPR,
      numValue: 11,
      formattedValue: format.percent(0.11),
    },
    {
      name: 'staking.hard_slashing',
      icon: IconHardSlashing,
      numValue: +slashing.value.slash_fraction_double_sign * 100,
      formattedValue: format.percent(slashing.value.slash_fraction_double_sign),
    },
    {
      name: 'staking.soft_slashing',
      icon: IconSoftSlashing,
      numValue: +slashing.value.slash_fraction_downtime * 100,
      formattedValue: format.percent(slashing.value.slash_fraction_downtime),
    },
  ]
));

</script>

<template>
  <div class="flex flex-col md:flex-row gap-5 md:px-4">
    <!-- widgets -->
    <div class="md:sticky top-0">

      <div class="flex flex-col items-center md:items-start gap-7 thick-border-block px-2 py-5">
        <div class="flex items-center" v-for="widget in widgetsInfo" :key="widget.name">
          <CircleProgressComponent :value="widget.numValue">
            <component :is="widget.icon" />
          </CircleProgressComponent>

          <span class="thin-border-block items-start -ml-8 pl-8">
            <div class="header-14-medium-aa text-header-text tracking-wide truncate uppercase">{{ $t(widget.name) }}
            </div>
            <div class="header-20-medium text-white tracking-wide truncate">{{ widget.formattedValue }}</div>
          </span>
        </div>
      </div>
    </div>

    <!-- table -->
    <div class="w-full">
      <div class="flex items-center justify-between py-1">
        <div class="w-full tabs tabs-boxed bg-transparent gap-2.5">
          <a v-for="item in tabs" class="btn-fill w-full md:w-36" :class="{ 'bg-button-v2': tab === item.name }"
            @click="tab = item.name">{{ $t(item.value) }}</a>
        </div>

        <!-- <div class="text-lg font-semibold">
          {{ list.length }}/{{ staking.params.max_validators }}
        </div> -->
      </div>

      <div class="pt-3 pb-4">
        <div
          class="overflow-auto thick-border-block px-2 scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin"
          :style="{ height: 'calc(100vh - 300px)' }">
          <table class="table bg-black/20 staking-table w-full">
            <thead class="bg-black sticky top-0 z-10">
              <tr class="text-header-text body-text-14">
                <td scope="col" class="w-15 relative flex items-center gap-1">
                  {{ $t('staking.rank') }}
                  <div class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </div>
                </td>
                <td scope="col" id="avatar">
                </td>
                <td scope="col" style="width: 300px">
                  {{ $t('staking.validator') }}
                </td>
                <td scope="col" class="flex justify-end items-center gap-1">
                  {{ $t('staking.uptime') }}
                  <div class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </div>
                </td>
                <td scope="col" class="text-right">
                  {{ $t('staking.voting_power') }}
                  <!-- <div class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </div> -->
                </td>
                <td scope="col" class="text-right">
                  {{ $t('staking.24h_changes') }}
                </td>
                <td scope="col" class="flex justify-end items-center gap-1">
                  {{ $t('staking.commission') }}
                  <div class="cursor-pointer">
                    <Icon icon="mynaui:chevron-up-solid" class="text-addition" width="16" height="16" />
                    <Icon icon="mynaui:chevron-down-solid" class="text-addition -mt-2.5" width="16" height="16" />
                  </div>
                </td>
                <td scope="col" class="text-right">
                  <span class="pr-5">
                    {{ $t('staking.operation') }}
                  </span>
                </td>
              </tr>
            </thead>
            <tbody class="">
              <tr v-for="({ v, rank, logo }, i) in list" :key="v.operator_address" class="mx-2 border-addition">
                <!-- 👉 rank -->
                <td>
                  <div class="body-text-14 text-button-text truncate relative px-2 py-1 rounded-full w-fit"
                    :class="`${calculateText(rank)}`">
                    {{ `#${i + 1}` }}
                  </div>
                </td>
                <!-- 👉 Avatar -->
                <td class="!px-0">
                  <div class="flex items-center overflow-hidden">
                    <div class="avatar relative w-10 h-10 rounded-full">
                      <div class="w-10 h-10 rounded-full bg-gray-400 absolute opacity-10"></div>
                      <div class="w-10 h-10 rounded-full">
                        <img :src="logo ? logo : defaultAvatar" class="object-contain" @error="
                          (e) => {
                            const identity = v.description?.identity;
                            if (identity) loadAvatar(identity);
                          }
                        " />
                        <!-- <Icon v-else class="text-[40px]" :icon="`mdi-help-circle-outline`" /> -->
                      </div>
                    </div>
                  </div>
                </td>
                <!-- 👉 Validator -->
                <td>
                  <div class="flex items-center overflow-hidden" style="max-width: 300px">
                    <div class="flex flex-col">
                      <span class="text-button-text header-16-medium uppercase dark:invert truncate"
                        style="max-width: 300px">
                        <RouterLink class="block truncate" :to="{
                          name: 'chain-staking-validator',
                          params: {
                            validator: v.operator_address,
                          },
                        }">
                          {{ v.description?.moniker }}
                        </RouterLink>
                      </span>
                      <span class="body-text-14 text-white truncate">{{
                        v.description?.website || v.description?.identity || '-'
                      }}</span>
                    </div>
                  </div>
                </td>
                <!-- 👉 Uptime -->
                <td class="!px-0">
                  <div class="text-right text-green-text body-text-16">


                    100%???


                  </div>
                </td>
                <!-- 👉 Voting Power -->
                <td class="text-right">
                  <div class="flex flex-col">
                    <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                      <span>{{
                        format.formatToken(
                          {
                            amount: parseInt(v.tokens).toString(),
                            denom: staking.params.bond_denom,
                          },
                          true,
                          '0,0'
                        ).split(' ')[0]
                      }}</span>
                      <span class="text-header-text header-14-medium-aa">{{
                        ` [${format.formatToken(
                          {
                            amount: parseInt(v.tokens).toString(),
                            denom: staking.params.bond_denom,
                          },
                          true,
                          '0,0'
                        ).split(' ')[1]}]`
                      }}</span>
                    </h6>
                    <span class="body-text-14 text-white">{{
                      format.calculatePercent(
                        v.delegator_shares,
                        staking.totalPower
                      )
                    }}</span>
                  </div>
                </td>
                <!-- 👉 24h Changes -->
                <td class="text-right body-text-14" :class="change24Color(v.consensus_pubkey)">
                  {{ change24Text(v.consensus_pubkey) }}
                </td>
                <!-- 👉 commission -->
                <td class="text-right body-text-14 text-white">
                  {{
                    format.formatCommissionRate(
                      v.commission?.commission_rates?.rate
                    )
                  }}
                </td>
                <!-- 👉 operation -->
                <td class="text-center">
                  <div class="flex justify-center">
                    <div v-if="v.jailed"
                      class="w-36 btn-outline border-red-text text-red-text hover:bg-red-text/20 hover:border-red-text hover:text-red-text">
                      {{ $t('staking.unstake') }}
                    </div>
                    <label v-else for="delegate" class="w-36 btn-outline border-button-text" @click="
                      dialog.open('delegate', {
                        validator_address: v.operator_address,
                      })
                      ">{{ $t('staking.stake') }}</label>
                  </div>

                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- <div class="divider"></div>
        <div class="flex flex-row items-center">
          <div class="text-xs truncate relative py-2 px-4 rounded-md w-fit text-error mr-2">
            <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-error"></span>
            {{ $t('staking.top') }} 33%
          </div>
          <div class="text-xs truncate relative py-2 px-4 rounded-md w-fit text-warning">
            <span class="inset-x-0 inset-y-0 opacity-10 absolute bg-warning"></span>
            {{ $t('staking.top') }} 67%
          </div>
          <div class="text-xs hidden md:!block pl-2">
            {{ $t('staking.description') }}
          </div>
        </div> -->
      </div>
    </div>
  </div>
</template>

<route>
  {
    meta: {
      i18n: 'staking',
      order: 3
    }
  }
</route>

<style>
.staking-table.table :where(th, td) {
  padding: 8px 5px;
  background: transparent;
}
</style>
