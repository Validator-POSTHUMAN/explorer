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
import { onMounted, ref, } from 'vue';
import type { Coin, Key, SigningInfo, SlashingParam, Validator } from '@/types';
import { formatSeconds } from '@/libs/utils';
import IconTrendUp from '@/components/icons/IconTrendUp.vue';
import IconLock from '@/components/icons/IconLock.vue';
import IconHardSlashing from '@/components/icons/IconHardSlashing.vue';
import IconSoftSlashing from '@/components/icons/IconSoftSlashing.vue';
import IconAPR from '@/components/icons/IconAPR.vue';
import defaultAvatar from '@/assets/images/redesign/defaultAvatar.png';
import dayjs from 'dayjs';
import CircleProgressComponent from '@/components/CircleProgressComponent.vue';
import { valconsToBase64 } from '@/libs';
import { useIndexModule } from '../indexStore';
import SortButton from '@/layouts/components/SortButton.vue';

const staking = useStakingStore();
const base = useBaseStore();
const format = useFormatter();
const dialog = useTxDialog();
const chainStore = useBlockchain();
const mintStore = useMintStore();
const store = useIndexModule();

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
};

const slashingParam = ref({} as SlashingParam);
const signingInfo = ref({} as Record<string, SigningInfo>);

const list = computed(() => {
  const window = Number(slashingParam.value.signed_blocks_window || 0);

  if (tab.value === 'active') {
    return staking.validators.map((x, i) => {
      const hexAddress = staking.findRotatedHexAddress(x.consensus_pubkey);
      const signing = signingInfo.value[hexAddress];
      return {
        v: x,
        rank: calculateRank(i),
        logo: logo(x.description.identity),
        uptime:
          signing && window > 0
            ? (window - Number(signing.missed_blocks_counter)) / window
            : undefined,
      }
    });
  } else if (tab.value === 'featured') {
    const endpoint = chainStore.current?.endpoints?.rest?.map(
      (x) => x.provider
    );
    if (endpoint) {
      endpoint.push('ping');
      return staking.validators
        .filter((x) => isFeatured(endpoint, x.description))
        .map((x, i) => {
          const hexAddress = staking.findRotatedHexAddress(x.consensus_pubkey);
          const signing = signingInfo.value[hexAddress];
          return {
            v: x,
            rank: 'primary',
            logo: logo(x.description.identity),
            uptime:
              signing && window > 0
                ? (window - Number(signing.missed_blocks_counter)) / window
                : undefined,
          }
        });
    }
    return [];
  }
  return unbondList.value.map((x, i) => {
    const hexAddress = staking.findRotatedHexAddress(x.consensus_pubkey);
    const signing = signingInfo.value[hexAddress];
    return {
      v: x,
      rank: 'primary',
      logo: logo(x.description.identity),
      uptime:
        signing && window > 0
          ? (window - Number(signing.missed_blocks_counter)) / window
          : undefined,
    }
  });
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

function updateTotalSigningInfo() {
  chainStore.rpc.getSlashingSigningInfos().then((x) => {
    x.info?.forEach((i) => {
      signingInfo.value[valconsToBase64(i.address)] = i;
    });
  });
}

onMounted(() => {
  updateTotalSigningInfo();

  chainStore.rpc.getSlashingParams().then((x) => {
    slashingParam.value = x.params;
  });
});

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
const supply = computed(() => store.stats.find(item => item.title === 'Supply')?.stats);
const bonded_tokens = computed(() => store.stats.find(item => item.title === "Bonded Tokens")?.stats);
const apr = computed(() => (Number(mintStore.inflation) * 100 * Number(supply.value?.replace(/,/g, ''))) / Number(bonded_tokens.value?.replace(/,/g, '')));

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
      numValue: apr.value,
      formattedValue: format.percent(apr.value / 100),
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

const returnAmounItem = (amount: Coin | Coin[] | undefined) => {
  if (!amount) return;
  if (Array.isArray(amount)) {
    return amount[0]
  } else {
    return amount
  }
};

const calcAmount = (amount: Coin | Coin[] | undefined, type: 'value' | 'token') => {
  if (!amount) return '-';
  return format.formatToken(returnAmounItem(amount), true, '0,0.[000000]').split(' ')[type === 'value' ? 0 : 1]
};

const listForTable = computed(() => list.value.map((item, key) => ({
  id: key + 1,
  rank: item.rank,
  validator: {
    logo: item.logo || defaultAvatar,
    name: item.v.description?.moniker,
    address: item.v.description?.website || item.v.description?.identity || '-',
    operator_address: item.v.operator_address,
    description: { ...item.v.description },
    jailed: item.v.jailed,
  },
  uptime: item.uptime,

  voting_power_value: parseInt(item.v.tokens).toString(),
  voting_power: {
    value: calcAmount({
      amount: parseInt(item.v.tokens).toString(),
      denom: staking.params.bond_denom,
    }, 'value'),
    token: calcAmount({
      amount: parseInt(item.v.tokens).toString(),
      denom: staking.params.bond_denom,
    }, 'token'),
    percent: format.calculatePercent(
      item.v.delegator_shares,
      staking.totalPower
    )
  },

  changes: item.v.consensus_pubkey,
  commission_value: item.v.commission?.commission_rates?.rate,
  commission: format.formatCommissionRate(
    item.v.commission?.commission_rates?.rate
  ),

})));

const sortTrByField = ref<string>('');
const sortDirection = ref<'asc' | 'desc'>('asc');

const sortedList = computed(() => {
  if (sortTrByField.value === '') return listForTable.value;

  return [...listForTable.value].sort((a, b) => {
    const varA = (a as any)[sortTrByField.value] ?? 0;
    const varB = (b as any)[sortTrByField.value] ?? 0;

    if (sortDirection.value === 'asc') {
      return varA - varB;
    } else {
      return varB - varA;
    }
  });
});

const toggleSortDirection = (field: string) => {
  if (sortTrByField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortTrByField.value = field;
    sortDirection.value = 'asc';
  }
};

</script>

<template>
  <div class="flex flex-col xl:flex-row gap-5 md:px-4">
    <!-- widgets -->
    <div class="md:sticky top-0">

      <div
        class="grid grid-cols-2 md:flex flex-col items-center md:items-start gap-3 md:gap-7 thick-border-block px-2 py-5">
        <div class="w-full md:w-auto flex items-center" v-for="widget in widgetsInfo" :key="widget.name">
          <CircleProgressComponent class="hidden md:block" :value="widget.numValue">
            <component :is="widget.icon" />
          </CircleProgressComponent>

          <div class="w-full thin-border-block items-center md:items-start md:-ml-5 md:pl-8">
            <CircleProgressComponent class="md:hidden mb-3" :value="widget.numValue" :size="50">
              <component :is="widget.icon" width="24" height="24" />
            </CircleProgressComponent>
            <p class="header-14-medium-aa text-header-text tracking-wide truncate uppercase">{{ $t(widget.name) }}</p>
            <p class="header-20-medium text-white tracking-wide truncate">{{ widget.formattedValue }}</p>
          </div>
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
      </div>

      <div class="pt-3 pb-4">
        <div class="overflow-x-auto">
          <div
            class="overflow-auto thick-border-block px-2 scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin"
            :style="{ height: 'calc(100vh - 200px)' }">
            <table class="table bg-black/20 staking-table">
              <thead class=" bg-black sticky top-0 z-10">
                <tr class="text-header-text body-text-14">
                  <td scope="col" class="w-15 relative flex items-center gap-1">
                    {{ $t('staking.rank') }}
                    <SortButton @click="() => toggleSortDirection('id')" />
                  </td>
                  <td scope="col" id="avatar">
                  </td>
                  <td scope="col" class="max-w-[300px]">
                    {{ $t('staking.validator') }}
                  </td>
                  <td scope="col" class="flex justify-end items-center gap-1">
                    {{ $t('staking.uptime') }}
                    <SortButton @click="() => toggleSortDirection('uptime')" />
                  </td>
                  <td scope="col" class="text-right">
                    <div class="flex gap-1 items-center justify-end">
                      {{ $t('staking.voting_power') }}
                      <SortButton @click="() => toggleSortDirection('voting_power_value')" />
                    </div>
                  </td>
                  <td scope="col" class="text-right">
                    {{ $t('staking.24h_changes') }}
                  </td>
                  <td scope="col" class="flex justify-end items-center gap-1">
                    {{ $t('staking.commission') }}
                    <SortButton @click="() => toggleSortDirection('commission_value')" />
                  </td>
                  <td scope="col" class="text-right">
                    <span class="pr-5">
                      {{ $t('staking.operation') }}
                    </span>
                  </td>
                </tr>
              </thead>
              <tbody class="">
                <tr v-for="{ id, changes, commission, rank, uptime, validator, voting_power } in sortedList"
                  :key="validator.operator_address" class="mx-2 border-addition">
                  <!-- 👉 rank -->
                  <td>
                    <div class="body-text-14 text-button-text truncate relative px-2 py-1 rounded-full w-fit"
                      :class="`text-${calculateText(rank)}`">
                      {{ `#${id}` }}
                    </div>
                  </td>
                  <!-- 👉 Avatar -->
                  <td class="!px-0">
                    <div class="flex items-center overflow-hidden">
                      <div class="avatar relative w-10 h-10 rounded-full">
                        <div class="w-10 h-10 rounded-full bg-gray-400 absolute opacity-10"></div>
                        <div class="w-10 h-10 rounded-full">
                          <img :src="validator.logo" class="object-contain" />
                        </div>
                      </div>
                    </div>
                  </td>
                  <!-- 👉 Validator -->
                  <td>
                    <div class="max-w-[300px] flex items-center overflow-hidden">
                      <div class="flex flex-col">
                        <span class="max-w-[300px] text-button-text header-16-medium uppercase dark:invert truncate">
                          <RouterLink class="block truncate" :to="{
                            name: 'chain-staking-validator',
                            params: {
                              validator: validator.operator_address,
                            },
                          }">
                            {{ validator.description?.moniker }}
                          </RouterLink>
                        </span>
                        <span class="body-text-14 text-white truncate">{{
                          validator.description?.website || validator.description?.identity || '-'
                        }}</span>
                      </div>
                    </div>
                  </td>
                  <!-- 👉 Uptime -->
                  <td class="!px-0">
                    <div class="text-right text-green-text body-text-16">{{ format.percent(uptime) }}</div>
                  </td>
                  <!-- 👉 Voting Power -->
                  <td class="text-right">
                    <div class="flex flex-col">
                      <h6 class="header-14-medium-aa tracking-wide whitespace-nowrap text-white">
                        <span>{{
                          voting_power.value
                        }}</span>
                        <span class="text-header-text header-14-medium-aa">{{
                          ` [${voting_power.token}]`
                        }}</span>
                      </h6>
                      <span class="body-text-14 text-white">{{
                        voting_power.percent
                      }}</span>
                    </div>
                  </td>
                  <!-- 👉 24h Changes -->
                  <td class="text-right body-text-14" :class="change24Color(changes)">
                    {{ change24Text(changes) }}
                  </td>
                  <!-- 👉 commission -->
                  <td class="text-right body-text-14 text-white">
                    {{
                      commission
                    }}
                  </td>
                  <!-- 👉 operation -->
                  <td class="text-right">
                    <div class="flex justify-end">
                      <div v-if="validator.jailed"
                        class="w-36 btn-outline border-red-text text-red-text hover:bg-red-text/20 hover:border-red-text hover:text-red-text">
                        {{ $t('staking.unstake') }}
                      </div>
                      <label v-else for="delegate" class="w-36 btn-outline border-button-text" @click="
                        dialog.open('delegate', {
                          validator_address: validator.operator_address,
                        })
                        ">{{ $t('staking.stake') }}</label>
                    </div>

                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
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
