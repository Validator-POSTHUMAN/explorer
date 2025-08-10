<script setup lang="ts">
import { parseCoins } from '@cosmjs/stargate';
import {
  useBankStore,
  useBlockchain,
  useDistributionStore,
  useFormatter,
  useMintStore,
  useStakingStore,
  useTxDialog,
} from '@/stores';
import { onMounted, computed, ref, watch } from 'vue';
import { Icon } from '@iconify/vue';
import CommissionRate from '@/components/ValidatorCommissionRate.vue';
import {
  consensusPubkeyToHexAddress,
  operatorAddressToAccount,
  pubKeyToValcons,
} from '@/libs';
import {
  PageRequest,
  type Coin,
  type Delegation,
  type PaginatedDelegations,
  type PaginatedTxs,
  type Validator,
} from '@/types';
import PaginationBar from '@/components/PaginationBar.vue';
import { fromBase64, toBase64 } from '@cosmjs/encoding';
import { stringToUint8Array, uint8ArrayToString } from '@/libs/utils';
import CircleProgressComponent from '@/components/CircleProgressComponent.vue';
import defaultAvatar from '@/assets/images/redesign/defaultAvatar.png';
import ActionsPanel from '@/components/ActionsPanel.vue';
import BackButton from '@/components/BackButton.vue';

const props = defineProps(['validator', 'chain']);

const staking = useStakingStore();
const blockchain = useBlockchain();
const format = useFormatter();
const dialog = useTxDialog();
const page = new PageRequest();

const validator: string = props.validator;

const v = ref({} as Validator);
const cache = JSON.parse(localStorage.getItem('avatars') || '{}');
const avatars = ref(cache || {});
const identity = ref('');
const rewards = ref([] as Coin[] | undefined);
const commission = ref([] as Coin[] | undefined);
const delegations = ref({} as PaginatedDelegations);
const addresses = ref(
  {} as {
    account: string;
    operAddress: string;
    hex: string;
    valCons: string;
  }
);
const selfBonded = ref({} as Delegation);

addresses.value.account = operatorAddressToAccount(validator);
// load self bond
staking
  .fetchValidatorDelegation(validator, addresses.value.account)
  .then((x) => {
    if (x) {
      selfBonded.value = x.delegation_response;
    }
  });

const txs = ref({} as PaginatedTxs);

blockchain.rpc.getTxsBySender(addresses.value.account).then((x) => {
  txs.value = x;
});

const apr = computed(() => {
  const rate = Number(v.value.commission?.commission_rates.rate || 0);
  const inflation = useMintStore().inflation;
  const communityTax = Number(useDistributionStore().params.community_tax);
  const bondedRatio =
    Number(staking.pool.bonded_tokens) / Number(useBankStore().supply.amount);

  return format.percent(
    ((1 - communityTax) * (1 - rate) * Number(inflation)) / bondedRatio
  );
});

const selfRate = computed(() => {
  if (selfBonded.value.balance?.amount) {
    return format.calculatePercent(
      selfBonded.value.balance.amount,
      v.value.tokens
    );
  }
  return '-';
});

const logo = (identity?: string) => {
  if (!identity) return '';
  const url = avatars.value[identity] || '';
  return url.startsWith('http')
    ? url
    : `https://s3.amazonaws.com/keybase_processed_uploads/${url}`;
};

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
        } else throw new Error(`failed to fetch avatar for ${identity}.`);
      })
      .catch((error) => {
        // console.error(error); // uncomment this if you want the user to see if the avatar failed to load.
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

onMounted(() => {
  if (validator) {
    staking.fetchValidator(validator).then((res) => {
      v.value = res.validator;
      identity.value = res.validator?.description?.identity || '';
      if (identity.value && !avatars.value[identity.value])
        loadAvatar(identity.value);

      addresses.value.hex = consensusPubkeyToHexAddress(
        v.value.consensus_pubkey
      );
      addresses.value.valCons = pubKeyToValcons(
        v.value.consensus_pubkey,
        blockchain.current?.bech32ConsensusPrefix || ''
      );
    });
    blockchain.rpc
      .getDistributionValidatorOutstandingRewards(validator)
      .then((res) => {
        rewards.value = res.rewards?.rewards?.sort(
          (a, b) => Number(b.amount) - Number(a.amount)
        );
        res.rewards?.rewards?.forEach((x) => {
          if (x.denom.startsWith('ibc/')) {
            format.fetchDenomTrace(x.denom);
          }
        });
      });
    blockchain.rpc.getDistributionValidatorCommission(validator).then((res) => {
      commission.value = res.commission?.commission?.sort(
        (a, b) => Number(b.amount) - Number(a.amount)
      );
      res.commission?.commission?.forEach((x) => {
        if (x.denom.startsWith('ibc/')) {
          format.fetchDenomTrace(x.denom);
        }
      });
    });

    // Disable delegations due to its bad performance
    // Comment out the following code if you want to enable it
    // pageload(1)
  }
});
let showCopyToast = ref(0);
const copyWebsite = async (url: string) => {
  if (!url) {
    return;
  }
  try {
    await navigator.clipboard.writeText(url);
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
};
const tipMsg = computed(() => {
  return showCopyToast.value === 2
    ? { class: 'error', msg: 'Copy Error!' }
    : { class: 'success', msg: 'Copy Success!' };
});

function pageload(p: number) {
  page.setPage(p);
  page.limit = 10;

  blockchain.rpc
    .getStakingValidatorsDelegations(validator, page)
    .then((res) => {
      delegations.value = res;
    });
}

const events = ref({} as PaginatedTxs);

enum EventType {
  Delegate = 'delegate',
  Unbond = 'unbond',
}

const selectedEventType = ref(EventType.Delegate);

function loadPowerEvents(p: number, type: EventType) {
  selectedEventType.value = type;
  page.setPage(p);
  page.setPageSize(5);
  blockchain.rpc
    .getTxs(
      "?order_by=2&query={type}.validator='{validator}'",
      { type: selectedEventType.value, validator },
      page
    )
    .then((res) => {
      events.value = res;
    });
}

function pagePowerEvents(page: number) {
  loadPowerEvents(page, selectedEventType.value);
}

pagePowerEvents(1);

function mapEvents(
  events: { type: string; attributes: { key: string; value: string }[] }[]
) {
  const attributes = events
    .filter((x) => x.type === selectedEventType.value)
    .filter(
      (x) =>
        x.attributes.findIndex(
          (attr) =>
            attr.value === validator ||
            attr.value === toBase64(stringToUint8Array(validator))
        ) > -1
    )
    .map((x) => {
      // check if attributes need to decode
      const output = {} as { [key: string]: string };

      if (x.attributes.findIndex((a) => a.key === `amount`) > -1) {
        x.attributes.forEach((attr) => {
          output[attr.key] = attr.value;
        });
      } else
        x.attributes.forEach((attr) => {
          output[uint8ArrayToString(fromBase64(attr.key))] = uint8ArrayToString(
            fromBase64(attr.value)
          );
        });
      return output;
    });

  const coinsAsString = attributes.map((x: any) => x.amount).join(',');
  const coins = parseCoins(coinsAsString);

  return coins.map((coin) => format.formatToken(coin)).join(', ');
}

function mapDelegators(messages: any[]) {
  if (!messages) return [];
  return Array.from(
    new Set(messages.map((x) => x.delegator_address || x.grantee))
  );
}

const rate = computed(
  () => Number(v.value.commission?.commission_rates.rate || 0) * 100
);
const change = computed(
  () => Number(v.value.commission?.commission_rates.max_change_rate || 0) * 100
);
const max = computed(
  () => Number(v.value.commission?.commission_rates.max_rate || 1) * 100
);

const rates = computed(() => [
  {},
  {
    name: 'Total Bond',
    value: totalBond.value,
    label: format.formatTokenAmount({
      amount: v.value.tokens,
      denom: staking.params.bond_denom,
    }),
  },
  {
    name: 'Commission Rate',
    value: format.percent(rate.value / 100),
    label: rate.value < max.value ? 'Low commission' : 'Extra High Comission',
    styles: rate.value < max.value ? 'text-green-text' : 'text-red-text',
  },
]);
const airdropStatus = ref('high');
const validatorApr = computed(
  () => (Number(apr.value.replace(/%/g, '')) / 100) * (1 - rate.value / 100)
);
const totalBond = computed(() =>
  format.roundedDisplayPercent(v.value.tokens, staking.pool.bonded_tokens)
);
</script>

<template>
  <div class="flex flex-col items-center md:px-20 pt-6 gap-6">
    <BackButton class="-mt-6 md:mt-0" />

    <div
      class="relative flex flex-col items-center w-full md:max-w-[1130px] thick-border-block p-3 md:p-10 mt-8 mb-20"
    >
      <!-- account-badge -->
      <div
        class="flex flex-col md:flex-row items-center md:items-start md:absolute md:-top-12 md:-left-20"
      >
        <div class="relative thick-border-block rounded-full p-[25px] bg-black">
          <div
            class="absolute top-0 right-0 m-2.5 text-star-yellow rounded-full shadow-[0_0_2px_1px_rgba(238,187,78,0.2)] before:bg-[radial-gradient(circle,rgba(238,187,78,0.5)_30%,transparent_90%)] before:absolute before:w-full before:h-full before:rounded-full"
          >
            <Icon icon="mingcute:star-fill" width="25" height="25" />
          </div>
          <div
            id="logo"
            class="w-20 h-20 md:w-[125px] md:h-[125px] rounded-full"
          >
            <img
              v-if="identity && avatars[identity]"
              v-lazy="logo(identity)"
              class="rounded-full w-20 h-20 md:w-[125px] md:h-[125px] object-contain"
              @error="(e) => loadAvatar(identity)"
            />
            <img
              v-if="!avatars[identity]"
              :src="defaultAvatar"
              class="w-20 h-20 md:w-[125px] md:h-[125px] object-cover"
            />
          </div>
        </div>
        <div>
          <div
            class="md:max-w-[395px] md:thick-border-block p-5 md:-ml-14 md:pl-16 mt-4 mb-4 bg-transparent md:bg-black truncate text-center md:text-start"
          >
            <p
              v-if="airdropStatus === 'high'"
              class="header-16 text-green-text tracking-wide mb-1"
            >
              <!-- FIXME: hardcode -->
              Airdrop High Probability
            </p>

            <p
              v-if="airdropStatus === 'no'"
              class="header-16 text-red-text tracking-wide mb-1"
            >
              <!-- FIXME: hardcode -->
              No airdrop
            </p>

            <p
              v-if="airdropStatus === 'low'"
              class="header-16 text-warning-text tracking-wide mb-1"
            >
              <!-- FIXME: hardcode -->
              Airdrop Low Probability
            </p>

            <p class="uppercase header-36 text-white truncate">
              {{ v.description?.moniker }}
            </p>
          </div>
          <div class="hidden xl:flex gap-2.5 text-addition">
            <div class="bg-addition/30 rounded-full px-3.5 py-1">
              <Icon icon="mdi:web" width="24" height="24" />
            </div>
            <a
              class="self-center"
              :href="v?.description?.website || '#'"
              :class="
                v?.description?.website ? 'cursor-pointer' : 'cursor-default'
              "
            >
              {{ v.description?.website || '-' }}
            </a>
          </div>
        </div>
      </div>

      <div class="">
        <div
          class="grid md:grid-cols-3 gap-x-10 gap-y-12 mb-20 xl:mx-36 mt-20 xl:mt-0"
        >
          <!-- firstLine -->
          <div class="flex gap-2.5 text-addition truncate">
            <div class="xl:hidden flex items-center gap-2.5 text-addition">
              <div class="bg-addition/30 rounded-full px-3.5 py-1">
                <Icon icon="mdi:web" width="24" height="24" />
              </div>
              <a
                class="self-center"
                :href="v?.description?.website || '#'"
                :class="
                  v?.description?.website ? 'cursor-pointer' : 'cursor-default'
                "
              >
                {{ v.description?.website || '-' }}
              </a>
            </div>
          </div>

          <div
            class="flex flex-col gap-1 text-white tracking-wide header-16 md:pl-8"
          >
            <p>Validator APR:</p>
            <p class="text-header-text header-36">
              {{ `${Math.floor(validatorApr * 100)}%` }}
            </p>
            <p class="text-addition body-text-14">
              Get 5% yield after deducting 20% validator fee
            </p>
          </div>

          <!-- FIXME: hardcode -->
          <div
            class="flex flex-col gap-1 text-white tracking-wide header-16 md:pl-8"
          >
            <p>Delegators:</p>
            <p class="text-header-text header-36">6,467</p>
          </div>

          <!-- secondLine -->
          <div
            v-for="item in rates"
            class="flex flex-col items-center justify-end text-white tracking-wide header-16 gap-5"
          >
            <p v-if="item.name">{{ `${$t(item.name)}:` }}</p>

            <CircleProgressComponent
              v-if="item.value"
              class="text-header-text header-36"
              :size="144"
              :value="+item.value"
            >
              {{ item.value }}
            </CircleProgressComponent>

            <p v-if="item.label" :class="item.styles">{{ item.label }}</p>
          </div>
        </div>

        <!-- actions -->
        <ActionsPanel
          v-if="v.operator_address"
          :key="v.operator_address"
          :address="v.operator_address"
        />
      </div>

      <!-- bonus badge -->
      <!-- Bonus -->
      <div
        v-if="airdropStatus === 'high'"
        class="max-w-[300px] mt-10 xl:mt-0 md:w-[300px] md:h-[100px] relative xl:absolute xl:bottom-20 xl:right-0 xl:translate-x-1/2 rounded-full border border-star-yellow bg-black py-2.5 px-12"
      >
        <div
          class="absolute -top-7 -right-4 m-2.5 text-star-yellow rounded-full shadow-[0_0_2px_1px_rgba(238,187,78,0.2)] before:bg-[radial-gradient(circle,rgba(238,187,78,0.5)_30%,transparent_90%)] before:absolute before:w-full before:h-full before:rounded-full"
        >
          <Icon icon="mingcute:star-fill" width="50" height="50" />
        </div>
        <Icon
          icon="mingcute:star-fill"
          class="absolute -top-2.5 right-0.5 text-white"
          width="35"
          height="35"
        />

        <p class="header-20-medium mb-0.5" :class="'text-star-yellow'">Bonus</p>
        <p class="body-text-16 text-white leading-5 line-clamp-2">
          You will get $PHMN for delegating to this validator
        </p>
      </div>

      <!-- Bonus is possible -->
      <div
        v-if="airdropStatus === 'low'"
        class="max-w-80 mt-10 md:mt-0 md:w-80 md:h-[115px] relative xl:absolute xl:bottom-20 xl:right-0 xl:translate-x-1/2 rounded-full border border-star-yellow bg-black py-2.5 px-12"
      >
        <div
          class="absolute -top-7 -right-4 m-2.5 text-star-yellow rounded-full shadow-[0_0_2px_1px_rgba(238,187,78,0.2)] before:bg-[radial-gradient(circle,rgba(238,187,78,0.5)_30%,transparent_90%)] before:absolute before:w-full before:h-full before:rounded-full"
        >
          <Icon icon="mingcute:star-fill" width="50" height="50" />
        </div>
        <Icon
          icon="mingcute:star-fill"
          class="absolute -top-2.5 right-0.5 text-white"
          width="35"
          height="35"
        />

        <p class="header-20-medium mb-0.5" :class="'text-star-yellow'">
          Bonus is possible
        </p>
        <p class="body-text-16 text-white leading-5 line-clamp-3">
          You will get any bonuses for delegating to this validator if you...
        </p>
      </div>

      <!-- NO Bonus -->
      <div
        v-if="airdropStatus === 'no'"
        class="max-w-80 mt-10 md:mt-0 md:w-80 md:h-[100px] relative xl:absolute xl:bottom-20 xl:right-0 xl:translate-x-1/2 rounded-full border border-red-text bg-black py-2.5 px-12"
      >
        <p class="header-20-medium mb-0.5" :class="'text-red-text'">NO Bonus</p>
        <p class="body-text-16 text-white leading-5 line-clamp-2">
          You will not get any bonuses for delegating to this validator
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

<style>
.validatore-table.table :where(th, td) {
  padding: 0.6rem 1rem;
  font-size: 14px;
}
</style>
