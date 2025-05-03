<script lang="ts" setup>
import {
  useBlockchain,
  useFormatter,
  useStakingStore,
  useTxDialog,
} from '@/stores';
import { select } from '@/components/dynamic/index';
import type { PaginatedProposals } from '@/types';
import ProposalProcess from './ProposalProcess.vue';
import type { PropType } from 'vue';
import { computed, ref } from 'vue';
const dialog = useTxDialog();
defineProps({
  proposals: { type: Object as PropType<PaginatedProposals> },
});

const format = useFormatter();
const staking = useStakingStore();
const chain = useBlockchain();
function showType(v: string) {
  if (v) {
    return v.substring(v.lastIndexOf('.') + 1);
  }
  return v;
}

const statusMap: Record<string, string> = {
  PROPOSAL_STATUS_VOTING_PERIOD: 'VOTING',
  PROPOSAL_STATUS_PASSED: 'PASSED',
  PROPOSAL_STATUS_REJECTED: 'REJECTED',
};
const voterStatusMap: Record<string, string> = {
  VOTE_OPTION_NO_WITH_VETO: '',
  VOTE_OPTION_YES: 'success',
  VOTE_OPTION_NO: 'error',
  VOTE_OPTION_ABSTAIN: 'warning',
};

const proposalInfo = ref();

function metaItem(metadata: string | undefined): {
  title: string;
  summary: string;
} {
  return metadata ? JSON.parse(metadata) : { title: '', summary: '' };
}
</script>
<template>
  <div class="grow">
    <table class="table-compact w-full table-fixed hidden lg:!table">
      <tbody>
        <tr v-for="(item, index) in proposals?.proposals" :key="index" class="border border-addition/20">
          <td class="px-4 w-20 border-b border-addition/20">
            <label for="proposal-detail-modal" class="tbody-text-14 text-button-text cursor-pointer"
              @click="proposalInfo = item">
              #{{ item?.proposal_id }}</label>
          </td>
          <td class="w-1/3 border-b border-addition/20">
            <div class="max-w-[650px] min-h-[51px]">
              <RouterLink :to="`/${chain.chainName}/gov/${item?.proposal_id}`"
                class="text-button-text header-16-medium dark:invert block hover:text-gray-400 truncate">
                {{
                  item?.content?.title ||
                  item?.title ||
                  metaItem(item?.metadata)?.title
                }}
              </RouterLink>
              <div v-if="item.content"
                class="bg-[#1C1C21] text-сhart-line inline-block rounded-full px-2 py-[1px] addition-text mb-1 mr-1">
                {{ showType(item.content['@type']) }}
              </div>
            </div>
          </td>

          <td class="w-1/6 border-b border-addition/20">
            <div class="pl-4 body-text-16">
              <div class="flex items-center text-addition" :class="{
                '!text-proposal-status-rejected': statusMap?.[item?.status] === 'REJECTED',
                '!text-proposal-status-approved': statusMap?.[item?.status] === 'PASSED',
                '!text-proposal-status-voting': statusMap?.[item?.status] === 'VOTING',
              }
                ">
                <div class="w-2 h-2 rounded-full mr-1 bg-addition" :class="{
                  '!bg-proposal-status-rejected': statusMap?.[item?.status] === 'REJECTED',
                  '!bg-proposal-status-approved': statusMap?.[item?.status] === 'PASSED',
                  '!bg-proposal-status-voting': statusMap?.[item?.status] === 'VOTING',
                }
                  "></div>
                <div class="capitalize">
                  {{ statusMap?.[item?.status].toLowerCase() || item?.status.toLowerCase() }}
                </div>
              </div>
              <div v-if="statusMap?.[item?.status] === 'VOTING'"
                class="truncate col-span-2 md:!col-span-1 dark:text-gray-400 text-right md:!flex md:!justify-start">
                {{ format.toDay(item.voting_end_time, 'from') }}
              </div>
            </div>
          </td>

          <td class="border-b border-addition/20">
            <div class="max-w-[400px]">
              <ProposalProcess :key="item?.status" :pool="staking.pool" :tally="item.final_tally_result"
                :status="statusMap?.[item?.status]" />
            </div>
          </td>

          <td class="border-b border-addition/20">
            <div v-if="statusMap?.[item?.status] === 'VOTING'" class="flex justify-end px-2">
              <label for="vote" class="w-44 btn-outline" @click="
                dialog.open('vote', {
                  proposal_id: item?.proposal_id,
                })
                ">
                <span v-if="item?.voterStatus !== 'VOTE_OPTION_NO_WITH_VETO'">{{
                  item?.voterStatus?.replace('VOTE_OPTION_', '')
                }}</span>

                <span v-else>{{ $t('gov.btn_vote') }}</span>
              </label>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="lg:!hidden">
      <div v-for="(item, index) in proposals?.proposals" :key="index" class="px-4 py-4">
        <div class="text-main text-base mb-1 flex gap-1 justify-between hover:text-gray-400">
          <RouterLink :to="`/${chain.chainName}/gov/${item?.proposal_id}`"
            class="text-button-text header-16-medium dark:invert block truncate">
            {{
              item?.content?.title ||
              item?.title ||
              metaItem(item?.metadata)?.title
            }}</RouterLink>
          <label for="proposal-detail-modal" class="tbody-text-14 text-button-text cursor-pointer"
            @click="proposalInfo = item">
            #{{ item?.proposal_id }}</label>
        </div>

        <div class="grid grid-cols-4 mt-2 mb-2">
          <div class="col-span-2">
            <div v-if="item.content"
              class="bg-[#1C1C21] text-сhart-line inline-block rounded-full px-2 py-[1px] addition-text mb-1 mr-1">
              {{ showType(item.content['@type']) }}
            </div>
          </div>

          <div
            class="truncate text-xs text-gray-500 dark:text-gray-400 flex items-center justify-end col-span-2 md:!col-span-1 text-right">
            {{ format.toDay(item.voting_end_time, 'from') }}
          </div>
        </div>

        <div>
          <ProposalProcess :pool="staking.pool" :tally="item.final_tally_result"></ProposalProcess>
        </div>

        <div class="mt-4" v-if="statusMap?.[item?.status] === 'VOTING'">
          <div class="flex justify-between">
            <!-- <div class="flex items-center" :class="statusMap?.[item?.status] === 'PASSED'
              ? 'text-proposal-status-approved'
              : statusMap?.[item?.status] === 'REJECTED'
                ? 'text-proposal-status-rejected'
                : 'text-addition'
              ">
              <div class="w-1 h-1 rounded-full mr-2" :class="statusMap?.[item?.status] === 'PASSED'
                ? 'bg-proposal-status-approved'
                : statusMap?.[item?.status] === 'REJECTED'
                  ? 'bg-proposal-status-rejected'
                  : 'bg-addition'
                "></div>
              <div class="text-xs flex items-center">
                {{ statusMap?.[item?.status] || item?.status }}
              </div>
            </div> -->

            <div class="pl-4 body-text-16">
              <div class="flex items-center text-addition" :class="{
                '!text-proposal-status-rejected': statusMap?.[item?.status] === 'REJECTED',
                '!text-proposal-status-approved': statusMap?.[item?.status] === 'PASSED',
                '!text-proposal-status-voting': statusMap?.[item?.status] === 'VOTING',
              }
                ">
                <div class="w-1 h-1 rounded-full mr-1 bg-addition" :class="{
                  '!bg-proposal-status-rejected': statusMap?.[item?.status] === 'REJECTED',
                  '!bg-proposal-status-approved': statusMap?.[item?.status] === 'PASSED',
                  '!bg-proposal-status-voting': statusMap?.[item?.status] === 'VOTING',
                }
                  "></div>
                <div class="uppercase">
                  {{ statusMap?.[item?.status].toLowerCase() || item?.status.toLowerCase() }}
                </div>
              </div>
            </div>


            <label for="vote" class="w-20 btn-outline" @click="
              dialog.open('vote', {
                proposal_id: item?.proposal_id,
              })
              ">
              <span v-if="item?.voterStatus !== 'VOTE_OPTION_NO_WITH_VETO'">{{
                item?.voterStatus?.replace('VOTE_OPTION_', '')
              }}</span>

              <span v-else>{{ $t('gov.btn_vote') }}</span></label>
          </div>
        </div>
      </div>
    </div>

    <input type="checkbox" id="proposal-detail-modal" class="modal-toggle" />
    <label for="proposal-detail-modal" class="modal">
      <label class="modal-box !w-11/12 !max-w-5xl" for="">
        <label for="proposal-detail-modal" class="btn btn-sm btn-circle absolute right-2 top-2">✕</label>
        <h3 class="font-bold text-lg">Description</h3>
        <p class="py-4">
          <Component v-if="
            proposalInfo?.content?.description ||
            proposalInfo?.summary ||
            metaItem(proposalInfo?.metadata)?.summary
          " :is="select(
            proposalInfo?.content?.description ||
            proposalInfo?.summary ||
            metaItem(proposalInfo?.metadata)?.summary,
            'horizontal'
          )
            " :value="proposalInfo?.content?.description ||
              proposalInfo?.summary ||
              metaItem(proposalInfo?.metadata)?.summary
              ">
          </Component>
        </p>
      </label>
    </label>
  </div>
</template>
