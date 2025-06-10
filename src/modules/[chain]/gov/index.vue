<script lang="ts" setup>
import { useGovStore } from '@/stores';
import ProposalListItem from '@/components/ProposalListItem.vue';
import { ref, onMounted, watch, computed } from 'vue';
import PaginationBar from '@/components/PaginationBar.vue';
import { PageRequest } from '@/types';

const tab = ref('1');
const store = useGovStore();
const pageRequest = ref(new PageRequest())

onMounted(() => {
    store.fetchProposals('2').then((x) => {
        if (x?.proposals?.length === 0) {
            tab.value = '3';
            store.fetchProposals('3');
        }
        store.fetchProposals('3');
        store.fetchProposals('4');
    });
});

const changeTab = (val: '1' | '2' | '3' | '4') => {
    tab.value = val;
};

function page(p: number) {
    pageRequest.value.setPage(p)
    store.fetchProposals(tab.value, pageRequest.value)
};

const tabs = [
    {
        name: 'gov.all',
        value: '1',
    },
    {
        name: 'gov.voting',
        value: '2',
    },
    {
        name: 'gov.passed',
        value: '3',
    },
    {
        name: 'gov.rejected',
        value: '4',
    },
];

const allProposals = computed(() => ({
    proposals: [
        ...(store.proposals[2]?.proposals || []),
        ...(store.proposals[4]?.proposals || []),
        ...(store.proposals[3]?.proposals || [])
    ],
    pagination: {
        total: (
            (Number(store.proposals[2]?.pagination?.total) || 0) +
            (Number(store.proposals[4]?.pagination?.total) || 0) +
            (Number(store.proposals[3]?.pagination?.total) || 0)
        ).toString()
    }
}));

</script>
<template>
    <div class="flex flex-col md:px-5" >
        <div class="tabs tabs-boxed bg-transparent mt-6 mb-8 text-center w-full gap-2.5">
            <a v-for="item in tabs" class="btn-fill w-full md:w-36" :class="{ 'bg-button-v2': tab === item.value }"
                @click="changeTab(item.value as '1' | '2' | '3' | '4')">{{ $t(item.name) }}</a>
        </div>
        <div class="overflow-auto flex flex-col thick-border-block grow scrollbar-thumb-addition scrollbar-track-transparent scrollbar-thin"
            :style="{ height: 'calc(100vh - 300px)' }">
            <ProposalListItem v-if="tab === '1'" :proposals="allProposals" />

            <ProposalListItem v-else :proposals="store?.proposals[tab]" />
            <PaginationBar :total="store?.proposals[tab]?.pagination?.total" :limit="pageRequest.limit"
                :callback="page" />
        </div>
    </div>
</template>
<route>
  {
    meta: {
      i18n: 'governance',
      order: 2
    }
  }
</route>