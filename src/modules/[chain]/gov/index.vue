<script lang="ts" setup>
import { useGovStore } from '@/stores';
import ProposalListItem from '@/components/ProposalListItem.vue';
import { ref, onMounted } from 'vue';
import PaginationBar from '@/components/PaginationBar.vue';
import { PageRequest } from '@/types';

const tab = ref('2');
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
}

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
]
</script>
<template>
    <div class="flex flex-col">
        <div class="tabs tabs-boxed bg-transparent mb-8 text-center w-full gap-2.5">
            <a v-for="item in tabs" class="btn-fill w-full md:w-36" :class="{ 'bg-button-v2': tab === item.value }"
                @click="changeTab(item.value as '1' | '2' | '3' | '4')">{{ $t(item.name) }}</a>
        </div>
        <ProposalListItem :proposals="store?.proposals[tab]" />
        <PaginationBar :total="store?.proposals[tab]?.pagination?.total" :limit="pageRequest.limit" :callback="page" />
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