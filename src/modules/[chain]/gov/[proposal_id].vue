<script lang="ts" setup>
import { computed } from '@vue/reactivity';
import MdEditor from 'md-editor-v3';
import ObjectElement from '@/components/dynamic/ObjectElement.vue';
import {
  useBaseStore,
  useBlockchain,
  useFormatter,
  useGovStore,
  useStakingStore,
  useTxDialog,
} from '@/stores';
import {
  PageRequest,
  type GovProposal,
  type GovVote,
  type PaginatedProposalDeposit,
  type Pagination,
} from '@/types';
import { ref, reactive, watch, onMounted } from 'vue';
import { fromBech32, toHex } from '@cosmjs/encoding';
import { Icon } from '@iconify/vue';
import AddressWithCopy from '@/components/AddressWithCopy.vue';
import IconEmojiHappy from '@/components/icons/IconEmojiHappy.vue';
import IconStatus from '@/components/icons/IconStatus.vue';
import IconTimeLeft from '@/components/icons/IconTimeLeft.vue';

const props = defineProps(['proposal_id', 'chain']);
const proposal = ref({} as GovProposal);
const format = useFormatter();
const store = useGovStore();
const dialog = useTxDialog();
const stakingStore = useStakingStore();
const chainStore = useBlockchain();

store.fetchProposal(props.proposal_id).then((res) => {
  let proposalDetail = reactive(res.proposal);
  // when status under the voting, final_tally_result are no data, should request fetchTally
  if (res.proposal?.status === 'PROPOSAL_STATUS_VOTING_PERIOD') {
    store.fetchTally(props.proposal_id).then((tallRes) => {
      proposalDetail.final_tally_result = tallRes?.tally;
    });
  }
  proposal.value = proposalDetail;
  // load origin params if the proposal is param change
  if (proposalDetail.content?.changes) {
    proposalDetail.content?.changes.forEach((item) => {
      chainStore.rpc.getParams(item.subspace, item.key).then((res) => {
        if (proposal.value.content && res.param) {
          if (proposal.value.content.current) {
            proposal.value.content.current.push(res.param);
          } else {
            proposal.value.content.current = [res.param];
          }
        }
      });
    });
  }

  const msgType = proposalDetail.content?.['@type'] || '';
  if (msgType.endsWith('MsgUpdateParams')) {
    if (msgType.indexOf('staking') > -1) {
      chainStore.rpc.getStakingParams().then((res) => {
        addCurrentParams(res);
      });
    } else if (msgType.indexOf('gov') > -1) {
      chainStore.rpc.getGovParamsVoting().then((res) => {
        addCurrentParams(res);
      });
    } else if (msgType.indexOf('distribution') > -1) {
      chainStore.rpc.getDistributionParams().then((res) => {
        addCurrentParams(res);
      });
    } else if (msgType.indexOf('slashing') > -1) {
      chainStore.rpc.getSlashingParams().then((res) => {
        addCurrentParams(res);
      });
    }
  }
});

function addCurrentParams(res: any) {
  if (proposal.value.content && res.params) {
    proposal.value.content.params = [proposal.value.content?.params];
    proposal.value.content.current = [res.params];
  }
}

const status = computed(() => {
  if (proposal.value.status) {
    return proposal.value.status.replace('PROPOSAL_STATUS_', '');
  }
  return '';
});

const deposit = ref({} as PaginatedProposalDeposit);
store.fetchProposalDeposits(props.proposal_id).then((x) => (deposit.value = x));

const votes = ref({} as GovVote[]);
const pageRequest = ref(new PageRequest());
const pageResponse = ref({} as Pagination);

store.fetchProposalVotes(props.proposal_id).then((x) => {
  votes.value = x.votes;
  pageResponse.value = x.pagination;
});

function shortTime(v: string) {
  if (v) {
    return format.toDay(v, 'from');
  }
  return '';
}

const votingCountdown = computed((): number => {
  const now = new Date();
  const end = new Date(proposal.value.voting_end_time);
  return end.getTime() - now.getTime();
});

const upgradeCountdown = computed((): number => {
  const height = Number(proposal.value.content?.plan?.height || 0);
  if (height > 0) {
    const base = useBaseStore();
    const current = Number(base.latest?.block?.header?.height || 0);
    return (
      (height - current) * Number((base.blocktime / 1000).toFixed()) * 1000
    );
  }
  const now = new Date();
  const end = new Date(proposal.value.content?.plan?.time || '');
  return end.getTime() - now.getTime();
});

const total = computed(() => {
  const tally = proposal.value.final_tally_result;
  let sum = 0;
  if (tally) {
    sum += Number(tally.abstain || 0);
    sum += Number(tally.yes || 0);
    sum += Number(tally.no || 0);
    sum += Number(tally.no_with_veto || 0);
  }
  return sum;
});

const turnout = computed(() => {
  if (total.value > 0) {
    const bonded = stakingStore.pool?.bonded_tokens || '1';
    return format.percent(total.value / Number(bonded));
  }
  return 0;
});

const yes = computed(() => {
  if (total.value > 0) {
    const yes = proposal.value?.final_tally_result?.yes || 0;
    return format.percent(Number(yes) / total.value);
  }
  return 0;
});

const no = computed(() => {
  if (total.value > 0) {
    const value = proposal.value?.final_tally_result?.no || 0;
    return format.percent(Number(value) / total.value);
  }
  return 0;
});

const veto = computed(() => {
  if (total.value > 0) {
    const value = proposal.value?.final_tally_result?.no_with_veto || 0;
    return format.percent(Number(value) / total.value);
  }
  return 0;
});

const abstain = computed(() => {
  if (total.value > 0) {
    const value = proposal.value?.final_tally_result?.abstain || 0;
    return format.percent(Number(value) / total.value);
  }
  return 0;
});
const processList = computed(() => {
  return [
    {
      name: 'YES',
      value: yes.value,
      class: 'bg-proposal-status-approved',
      borderColor:
        'border-proposal-status-approved hover:border-proposal-status-approved hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-approved',
      icon: 'tabler:check',
    },
    {
      name: 'NO',
      value: no.value,
      class: 'bg-proposal-status-rejected',
      borderColor:
        'border-proposal-status-rejected hover:border-proposal-status-rejected hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-rejected',
      icon: 'ic:round-close',
    },
    {
      name: 'No with veto',
      value: veto.value,
      class: 'bg-proposal-status-veto',
      borderColor:
        'border-proposal-status-veto hover:border-proposal-status-veto hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-veto',
    },
    {
      name: 'Abstain',
      value: abstain.value,
      class: 'bg-addition',
      borderColor:
        'border-addition hover:border-addition hover:text-white hover:bg-button-hover',
      textColor: 'text-addition',
      icon: 'akar-icons:dot-grid',
    },
  ];
});

function showValidatorName(voter: string) {
  try {
    const { data } = fromBech32(voter);
    const hex = toHex(data);
    const v = stakingStore.validators.find(
      (x) => toHex(fromBech32(x.operator_address).data) === hex
    );
    return v ? v.description.moniker : voter;
  } catch (e) {
    return voter;
  }
}

function pageload(p: number) {
  pageRequest.value.setPage(p);
  store.fetchProposalVotes(props.proposal_id, pageRequest.value).then((x) => {
    votes.value = x.votes;
    pageResponse.value = x.pagination;
  });
}

function metaItem(metadata: string | undefined): {
  title: string;
  summary: string;
} {
  return metadata ? JSON.parse(metadata) : { title: '', summary: '' };
}

const statusData = computed(() => [
  {
    isAddress: true,
    value: proposal.value?.proposer,
    label: 'Creator',
    icon: IconEmojiHappy,
  },
  {
    value: status.value,
    label: 'Status',
    icon: IconStatus,
  },
  {
    value: format.toDay(proposal.value?.voting_end_time, 'from'),
    label: 'Time left',
    icon: IconTimeLeft,
  },
]);

const votingData = computed(() => [
  {
    label: 'staking.voting_power',
    // Total Stake Validator / Total bonded tokens (stakingStore.pool.bonded_tokens) = Voting Power Validator
    value: format.calculatePercent(
      stakingStore.pool.bonded_tokens,
      stakingStore.totalPower
    ),
  },
  {
    label: 'staking.btn_vote',
    value:
      votes.value.find((item) => item.voter === proposal.value?.proposer)
        ?.option ?? 'None',
  },
]);
</script>

<template>
  <div class="md:px-4">
    <h2
      class="flex flex-col items-center md:!justify-between md:!flex-row mb-2"
    >
      <p
        class="truncate w-full header-20-medium-aa text-header-text tracking-wide uppercase"
      >
        {{
          `#${proposal_id}. ${
            proposal.title ||
            proposal.content?.title ||
            metaItem(proposal?.metadata)?.title
          }`
        }}
      </p>
      <div class="text-addition body-text-14 text-end">
        <p>
          {{ proposal?.content && proposal?.content['@type'] }}
        </p>
        <p>
          {{ status }}
        </p>
      </div>
    </h2>

    <div class="flex flex-col md:flex-row gap-5">
      <!-- info -->
      <div class="md:min-w-[420px]">
        <div class="bg-black/70 thick-border-block p-5">
          <div class="text-button-text mb-9">
            <p class="uppercase header-20-medium-aa mb-5">
              {{ $t('gov.status') }}
            </p>
            <div
              class="w-full border-y border-addition py-4 px-2.5 flex flex-col gap-2.5"
            >
              <div
                v-for="item in statusData"
                class="grid grid-cols-5 gap-3"
                :key="item.label"
              >
                <p class="col-span-2 header-16 tracking-wide flex gap-2.5">
                  <!-- <Icon class="text-addition/50" icon="ic:round-close" width="24" height="24" /> -->
                  <component class="text-addition/50" :is="item.icon" />
                  <span>{{ item.label }}</span>
                </p>
                <div class="col-span-3 body-text-16 text-white truncate">
                  <AddressWithCopy
                    v-if="item.isAddress"
                    :address="item.value"
                    icon
                    styles="body-text-16 text-white"
                    :size="16"
                  />
                  <span v-else>{{ item.value }}</span>
                </div>
              </div>
            </div>
            <div
              class="w-full border-b border-addition py-4 px-2.5 flex flex-col gap-2.5"
            >
              <div v-for="item in votingData" class="grid grid-cols-5 gap-3">
                <p class="col-span-2 header-16 tracking-wide leading-5">
                  {{ $t(item.label) }}
                </p>
                <p class="col-span-3 body-text-16 text-white">
                  {{ item.value }}
                </p>
              </div>
            </div>
          </div>

          <div class="rounded shadow">
            <!-- <h2 class="card-title mb-1">{{ $t('gov.tally') }}</h2> -->
            <div
              class="grid grid-cols-2 items-center gap-2.5 mb-1 header-16-medium tracking-wide"
              v-for="(item, index) of processList"
              :key="index"
            >
              <label
                class="btn-outline px-7 py-4 text-white truncate justify-between"
                :class="item.borderColor"
              >
                <span>{{ item.name }}</span>
                <Icon
                  v-if="item.icon"
                  :icon="item.icon"
                  width="18"
                  height="18"
                />
              </label>
              <div>
                <p
                  class="text-center flex items-center justify-center"
                  :class="item.textColor"
                >
                  {{ item.value }}
                </p>
                <div class="h-3 w-full relative rounded-full overflow-hidden">
                  <div
                    class="absolute inset-x-0 inset-y-0 bg-addition w-full opacity-20"
                  ></div>
                  <div
                    class="absolute inset-x-0 inset-y-0 rounded-sm"
                    :class="`${item.class}`"
                    :style="`width: ${
                      item.value === '-' || item.value === 'NaN%'
                        ? '0%'
                        : item.value
                    }`"
                  ></div>
                </div>
              </div>
            </div>
            <label
              for="vote"
              class="btn-outline py-4 mb-7"
              @click="dialog.open('vote', { proposal_id })"
              >{{ $t('gov.change_vote') }}</label
            >
          </div>
        </div>
      </div>

      <!-- text -->
      <div
        class="w-full pt-3 pb-4 rounded mb-4 shadow overflow-auto thick-border-block bg-black/70 px-2 scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin"
        :style="{ height: 'calc(100vh - 180px)' }"
      >
        <div class="">
          <ObjectElement :value="proposal.content" />
        </div>
        <div
          v-if="
            (proposal.summary && !proposal.content?.description) ||
            metaItem(proposal?.metadata)?.summary
          "
        >
          <MdEditor
            :model-value="
              format.multiLine(
                proposal.summary || metaItem(proposal?.metadata)?.summary
              )
            "
            previewOnly
            class="md-editor-recover"
          ></MdEditor>
        </div>
      </div>
    </div>
  </div>
</template>
