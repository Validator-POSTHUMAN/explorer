<script setup lang="ts">
import { useTxDialog } from '@/stores';

const props = defineProps({
    address: { type: String },
});

const dialog = useTxDialog();

const btns = [
    {
        name: 'account.btn_unbond',
        id: 'unbond',
    },
    {
        name: 'account.btn_withdraw',
        id: 'withdraw_commission',
    },
    {
        name: 'account.btn_redelegate',
        id: 'redelegate',
    },
    {
        name: 'account.btn_delegate',
        id: 'delegate',
    },
];
</script>

<template>
    <div class="flex flex-col flex-wrap justify-center md:flex-row gap-5">
        <label v-for="item in btns" :for="item.id" class="w-44 btn-outline border-button-text text-header-text cursor-pointer"
        :class="{'bg-addition/20 hover:bg-addition/20 hover:text-header-text cursor-not-allowed': !address?.length}"
        @click="item?.id && address?.length &&
            dialog.open(item?.id, {
                validator_address: address,
            })">
            {{ $t(item.name) }}
        </label>
    </div>
</template>