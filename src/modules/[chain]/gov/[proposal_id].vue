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
import Countdown from '@/components/Countdown.vue';
import PaginationBar from '@/components/PaginationBar.vue';
import { fromBech32, toHex } from '@cosmjs/encoding';
import { Icon } from '@iconify/vue';
import AddressWithCopy from '@/components/AddressWithCopy.vue';
import IconEmojiHappy from '@/components/icons/IconEmojiHappy.vue';
import IconStatus from '@/components/icons/IconStatus.vue';
import IconRevoting from '@/components/icons/IconRevoting.vue';
import IconTimeLeft from '@/components/icons/IconTimeLeft.vue';


const props = defineProps(['proposal_id', 'chain']);
const proposal = ref({} as GovProposal);
const format = useFormatter();
const store = useGovStore();
const dialog = useTxDialog();
const stakingStore = useStakingStore();
const chainStore = useBlockchain();

store.fetchProposal(props.proposal_id).then((res) => {
  const proposalDetail = reactive(res.proposal);
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
          };
        }
      })
    })
  }
});

const color = computed(() => {
  if (proposal.value.status === 'PROPOSAL_STATUS_PASSED') {
    return 'success';
  } else if (proposal.value.status === 'PROPOSAL_STATUS_REJECTED') {
    return 'error';
  }
  return '';
});
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
    return (height - current) * 6 * 1000;
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
    // { name: 'Turnout', value: turnout.value, class: 'bg-info' },
    {
      name: 'YES',
      value: yes.value,
      class: 'bg-proposal-status-approved',
      borderColor: 'border-proposal-status-approved hover:border-proposal-status-approved hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-approved',
      icon: 'tabler:check',
    },
    {
      name: 'NO',
      value: no.value,
      class: 'bg-proposal-status-rejected',
      borderColor: 'border-proposal-status-rejected hover:border-proposal-status-rejected hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-rejected',
      icon: 'ic:round-close',
    },
    {
      name: 'No with veto',
      value: veto.value,
      class: 'bg-proposal-status-veto',
      borderColor: 'border-proposal-status-veto hover:border-proposal-status-veto hover:text-white hover:bg-button-hover',
      textColor: 'text-status-text-veto',
    },
    {
      name: 'Abstain',
      value: abstain.value,
      class: 'bg-addition',
      borderColor: 'border-addition hover:border-addition hover:text-white hover:bg-button-hover',
      textColor: 'text-addition',
      icon: 'akar-icons:dot-grid',
    },
  ];
});

function showValidatorName(voter: string) {
  const { data } = fromBech32(voter);
  const hex = toHex(data);
  const v = stakingStore.validators.find(
    (x) => toHex(fromBech32(x.operator_address).data) === hex
  );
  return v ? v.description.moniker : voter;
}

function pageload(p: number) {
  pageRequest.value.setPage(p);
  store.fetchProposalVotes(props.proposal_id, pageRequest.value).then((x) => {
    votes.value = x.votes;
    pageResponse.value = x.pagination;
  });
}

function metaItem(metadata: string | undefined): { title: string; summary: string } {
  return metadata ? JSON.parse(metadata) : { title: '', summary: '' }
}

const statusData = computed(() => (
  [
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
      // <!-- FIXME: hardcode -->
      value: 'Enable',
      label: 'Revoting',
      icon: IconRevoting,
    },
    {
      value: format.toDay(proposal.value?.voting_end_time, 'from'),
      label: 'Time left',
      icon: IconTimeLeft,
    },
  ]
));

watch(() => total.value, newVal => console.log(stakingStore))

// <!-- FIXME: hardcode -->
const votingData = computed(() => ([{
  label: 'staking.voting_power',
  // как подсчитать voting power - это % соотношения:
  // Total Stake Валидатора stakingStore.totalPower ??????? / Total bonded tokens (сколько всего токенов застейкано в сети stakingStore.pool.bonded_tokens) = Voting Power валидатора
  value: format.calculatePercent(stakingStore.totalPower, stakingStore.pool.bonded_tokens)
},
{
  label: 'staking.btn_vote',
  // ??????
  value: 'None',
}]));

// onMounted(() => {
//   stakingStore.fetchValidator(validator).then((res) => {
//       v.value = res.validator;
//       identity.value = res.validator?.description?.identity || '';
//       if (identity.value && !avatars.value[identity.value]) loadAvatar(identity.value);

//       const prefix = valoperToPrefix(v.value.operator_address) || '<Invalid>';
//       addresses.value.hex = consensusPubkeyToHexAddress(
//         v.value.consensus_pubkey
//       );
//       addresses.value.valCons = pubKeyToValcons(
//         v.value.consensus_pubkey,
//         prefix
//       );
//     });
// })

</script>

<template>
  <div class="md:px-4">
    <h2 class="flex flex-col items-center md:!justify-between md:!flex-row mb-2">
      <p class="truncate w-full header-20-medium-aa text-header-text tracking-wide uppercase">
        {{ `#${proposal_id}. ${proposal.title || proposal.content?.title || metaItem(proposal?.metadata)?.title}` }}
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
        <div class=" bg-black/70 thick-border-block p-5">

          <div class="text-button-text mb-9">
            <p class="uppercase header-20-medium-aa mb-5">{{ $t('gov.status') }}</p>
            <div class="w-full border-y border-addition py-4 px-2.5 flex flex-col gap-2.5">
              <div v-for="item in statusData" class="grid grid-cols-5 gap-3" :key="item.label">
                <p class="col-span-2 header-16 tracking-wide flex gap-2.5">
                  <!-- <Icon class="text-addition/50" icon="ic:round-close" width="24" height="24" /> -->
                  <component class="text-addition/50" :is="item.icon" />

                  <span>{{ item.label }}</span>
                </p>
                <div class="col-span-3 body-text-16 text-white truncate">
                  <AddressWithCopy v-if="item.isAddress" :address="item.value" icon styles="body-text-16 text-white"
                    :size="16" />
                  <span v-else>{{ item.value }}</span>
                </div>
              </div>
            </div>

            <div class="w-full border-b border-addition py-4 px-2.5 flex flex-col gap-2.5">
              <div v-for="item in votingData" class="grid grid-cols-5 gap-3">
                <p class="col-span-2 header-16 tracking-wide leading-5">{{ $t(item.label) }}</p>
                <p class="col-span-3 body-text-16 text-white">{{ item.value }}</p>
              </div>
            </div>
          </div>

          <div class=" rounded shadow">
            <!-- <h2 class="card-title mb-1">{{ $t('gov.tally') }}</h2> -->
            <div class="grid grid-cols-2 items-center gap-2.5 mb-1 header-16-medium tracking-wide"
              v-for="(item, index) of processList" :key="index">
              <label class="btn-outline px-7 py-4 text-white truncate justify-between" :class="item.borderColor">
                <span>{{ item.name }}</span>
                <Icon v-if="item.icon" :icon="item.icon" width="18" height="18" />
              </label>
              <div>
                <p class="text-center flex items-center justify-center" :class="item.textColor">
                  {{ item.value }}
                </p>
                <div class="h-3 w-full relative rounded-full overflow-hidden">
                  <div class="absolute inset-x-0 inset-y-0 bg-addition  w-full opacity-20"></div>
                  <div class="absolute inset-x-0 inset-y-0 rounded-sm" :class="`${item.class}`" :style="`width: ${item.value === '-' || item.value === 'NaN%' ? '0%' : item.value
                    }`"></div>

                </div>
              </div>
            </div>
            <label for="vote" class="btn-outline py-4 mb-7" @click="dialog.open('vote', { proposal_id })">{{
              $t('gov.change_vote') }}</label>

            <!-- <div class="mt-6 grid grid-cols-2">
              <label for="vote" class="btn btn-primary float-right btn-sm mx-1"
                @click="dialog.open('vote', { proposal_id })">{{ $t('gov.btn_vote') }}</label>
              <label for="deposit" class="btn btn-primary float-right btn-sm mx-1"
                @click="dialog.open('deposit', { proposal_id })">{{ $t('gov.btn_deposit') }}</label>
            </div> -->
          </div>

          <!-- timeline -->
          <!-- <div class="px-4 pt-3 pb-5 rounded shadow lg:!!col-span-2">
            <h2 class="card-title">{{ $t('gov.timeline') }}</h2>

            <div class="px-1">
              <div class="flex items-center mb-4 mt-2">
                <div class="w-2 h-2 rounded-full bg-error mr-3"></div>
                <div class="text-base flex-1 text-main">
                  {{ $t('gov.submit_at') }}: {{ format.toDay(proposal.submit_time) }}
                </div>
                <div class="text-sm">{{ shortTime(proposal.submit_time) }}</div>
              </div>
              <div class="flex items-center mb-4">
                <div class="w-2 h-2 rounded-full bg-primary mr-3"></div>
                <div class="text-base flex-1 text-main">
                  {{ $t('gov.deposited_at') }}:
                  {{
                    format.toDay(
                      proposal.status === 'PROPOSAL_STATUS_DEPOSIT_PERIOD'
                        ? proposal.deposit_end_time
                        : proposal.voting_start_time
                    )
                  }}
                </div>
                <div class="text-sm">
                  {{
                    shortTime(
                      proposal.status === 'PROPOSAL_STATUS_DEPOSIT_PERIOD'
                        ? proposal.deposit_end_time
                        : proposal.voting_start_time
                    )
                  }}
                </div>
              </div>
              <div class="mb-4">
                <div class="flex items-center">
                  <div class="w-2 h-2 rounded-full bg-proposal-status-approved mr-3"></div>
                  <div class="text-base flex-1 text-main">
                    {{ $t('gov.vote_start_from') }} {{ format.toDay(proposal.voting_start_time) }}
                  </div>
                  <div class="text-sm">
                    {{ shortTime(proposal.voting_start_time) }}
                  </div>
                </div>
                <div class="pl-5 text-sm mt-2">
                  <Countdown :time="votingCountdown" />
                </div>
              </div>
              <div>
                <div class="flex items-center mb-1">
                  <div class="w-2 h-2 rounded-full bg-success mr-3"></div>
                  <div class="text-base flex-1 text-main">
                    {{ $t('gov.vote_end') }} {{ format.toDay(proposal.voting_end_time) }}
                  </div>
                  <div class="text-sm">
                    {{ shortTime(proposal.voting_end_time) }}
                  </div>
                </div>
                <div class="pl-5 text-sm">
                  {{ $t('gov.current_status') }}: {{ $t(`gov.proposal_statuses.${proposal.status}`) }}
                </div>
              </div>

              <div class="mt-4" v-if="
                proposal?.content?.['@type']?.endsWith('SoftwareUpgradeProposal')
              ">
                <div class="flex items-center">
                  <div class="w-2 h-2 rounded-full bg-warning mr-3"></div>
                  <div class="text-base flex-1 text-main">
                    {{ $t('gov.upgrade_plan') }}:
                    <span v-if="Number(proposal.content?.plan?.height || '0') > 0">
                      (EST)</span>
                    <span v-else>{{
                      format.toDay(proposal.content?.plan?.time)
                    }}</span>
                  </div>
                  <div class="text-sm">
                    {{ shortTime(proposal.voting_end_time) }}
                  </div>
                </div>
                <div class="pl-5 text-sm mt-2">
                  <Countdown :time="upgradeCountdown" />
                </div>
              </div>
            </div>
          </div> -->
        </div>
      </div>

      <!-- text -->
      <div
        class="w-full pt-3 pb-4 rounded mb-4 shadow overflow-auto thick-border-block bg-black/70 px-2 scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin"
        :style="{ height: 'calc(100vh - 180px)' }">

        <div class="">
          <ObjectElement :value="proposal.content" />
        </div>
        <div v-if="proposal.summary && !proposal.content?.description || metaItem(proposal?.metadata)?.summary">
          <MdEditor :model-value="format.multiLine(proposal.summary || metaItem(proposal?.metadata)?.summary)"
            previewOnly class="md-editor-recover"></MdEditor>
        </div>
      </div>
    </div>

    <!-- <div class="px-4 pt-3 pb-4 rounded mb-4 shadow">
      <h2 class="card-title">{{ $t('gov.votes') }}</h2>
      <div class="overflow-x-auto">
        <table class="table w-full table-zebra">
          <tbody>
            <tr v-for="(item, index) of votes" :key="index">
              <td class="py-2 text-sm">{{ showValidatorName(item.voter) }}</td>
              <td v-if="item.option" class="py-2 text-sm" :class="{
                'text-proposal-status-approved': item.option === 'VOTE_OPTION_YES',
                'text-gray-400': item.option === 'VOTE_OPTION_ABSTAIN',
              }">
                {{ String(item.option).replace('VOTE_OPTION_', '') }}
              </td>
              <td v-if="item.options" class="py-2 text-sm">
                {{item.options.map(x =>
                  `${x.option.replace('VOTE_OPTION_', '')}:${format.percent(x.weight)}`).join(', ')}}
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationBar :limit="pageRequest.limit" :total="pageResponse.total" :callback="pageload" />
      </div>
    </div> -->
  </div>
</template>
