<template>
  <div class="overflow-x-auto">
    <table class="table table-xs table-zebra w-full">
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key" 
              @click="sort(column.key)"
              :class="{ 'cursor-pointer hover:bg-base-200': column.sortable }">
            <div class="flex items-center gap-1">
              {{ column.label }}
              <span v-if="column.sortable" class="text-xs opacity-50">
                <span v-if="sortKey === column.key">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
                <span v-else>↕</span>
              </span>
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in sortedData" :key="index">
          <td v-for="column in columns" :key="column.key">
            <slot :name="`cell-${column.key}`" :item="item" :value="getValue(item, column.key)">
              {{ getValue(item, column.key) }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
  }
})

const sortKey = ref('')
const sortOrder = ref('asc')

const sort = (key) => {
  const column = props.columns.find(col => col.key === key)
  if (!column?.sortable) return
  
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const getValue = (item, key) => {
  return key.split('.').reduce((obj, k) => obj?.[k], item)
}

const sortedData = computed(() => {
  if (!sortKey.value) return props.data
  
  const column = props.columns.find(col => col.key === sortKey.value)
  if (!column?.sortable) return props.data
  
  return [...props.data].sort((a, b) => {
    let aVal = getValue(a, sortKey.value)
    let bVal = getValue(b, sortKey.value)
    
    // Handle numeric values
    if (column.type === 'number') {
      aVal = parseFloat(aVal) || 0
      bVal = parseFloat(bVal) || 0
    }
    
    // Handle string values
    if (typeof aVal === 'string') aVal = aVal.toLowerCase()
    if (typeof bVal === 'string') bVal = bVal.toLowerCase()
    
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})
</script>
