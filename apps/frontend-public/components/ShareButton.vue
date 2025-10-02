<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="btn btn-ghost btn-sm gap-2">
      <Icon name="heroicons:share" class="w-4 h-4" />
      <span class="hidden sm:inline">Share</span>
    </label>
    <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
      <!-- WhatsApp -->
      <li>
        <a :href="whatsappUrl" target="_blank" class="flex items-center gap-3">
          <Icon name="logos:whatsapp-icon" class="w-5 h-5" />
          WhatsApp
        </a>
      </li>
      
      <!-- Telegram -->
      <li>
        <a :href="telegramUrl" target="_blank" class="flex items-center gap-3">
          <Icon name="logos:telegram" class="w-5 h-5" />
          Telegram
        </a>
      </li>
      
      <!-- Email -->
      <li>
        <a :href="emailUrl" class="flex items-center gap-3">
          <Icon name="heroicons:envelope" class="w-5 h-5" />
          E-Mail
        </a>
      </li>
      
      <!-- Twitter/X -->
      <li>
        <a :href="twitterUrl" target="_blank" class="flex items-center gap-3">
          <Icon name="logos:twitter" class="w-5 h-5" />
          Twitter/X
        </a>
      </li>
      
      <!-- Facebook -->
      <li>
        <a :href="facebookUrl" target="_blank" class="flex items-center gap-3">
          <Icon name="logos:facebook" class="w-5 h-5" />
          Facebook
        </a>
      </li>
      
      <!-- LinkedIn -->
      <li>
        <a :href="linkedinUrl" target="_blank" class="flex items-center gap-3">
          <Icon name="logos:linkedin-icon" class="w-5 h-5" />
          LinkedIn
        </a>
      </li>
      
      <div class="divider my-1"></div>
      
      <!-- Copy Link -->
      <li>
        <button @click="copyToClipboard" class="flex items-center gap-3">
          <Icon name="heroicons:clipboard-document" class="w-5 h-5" />
          {{ copied ? 'Copied!' : 'Copy Link' }}
        </button>
      </li>
      
      <!-- Print -->
      <li>
        <button @click="printPage" class="flex items-center gap-3">
          <Icon name="heroicons:printer" class="w-5 h-5" />
          Print
        </button>
      </li>
      
      <!-- Export Options -->
      <li v-if="showExport">
        <details>
          <summary class="flex items-center gap-3">
            <Icon name="heroicons:arrow-down-tray" class="w-5 h-5" />
            Export
          </summary>
          <ul class="p-2">
            <li><button @click="exportData('csv')" class="w-full text-left">CSV</button></li>
            <li><button @click="exportData('json')" class="w-full text-left">JSON</button></li>
            <li><button @click="exportData('pdf')" class="w-full text-left">PDF</button></li>
          </ul>
        </details>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  url: {
    type: String,
    default: ''
  },
  hashtags: {
    type: Array,
    default: () => []
  },
  showExport: {
    type: Boolean,
    default: false
  },
  exportData: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['export'])

const copied = ref(false)

// Get current URL if not provided
const currentUrl = computed(() => {
  if (props.url) return props.url
  if (process.client) {
    return window.location.href
  }
  return ''
})

// Encode text for URLs
const encodeText = (text) => encodeURIComponent(text)

// Share URLs
const whatsappUrl = computed(() => {
  const text = `${props.title}${props.description ? '\n\n' + props.description : ''}\n\n${currentUrl.value}`
  return `https://wa.me/?text=${encodeText(text)}`
})

const telegramUrl = computed(() => {
  const text = `${props.title}${props.description ? '\n\n' + props.description : ''}`
  return `https://t.me/share/url?url=${encodeText(currentUrl.value)}&text=${encodeText(text)}`
})

const emailUrl = computed(() => {
  const subject = `Basketball Stats: ${props.title}`
  const body = `${props.description ? props.description + '\n\n' : ''}Check out this basketball data:\n${currentUrl.value}`
  return `mailto:?subject=${encodeText(subject)}&body=${encodeText(body)}`
})

const twitterUrl = computed(() => {
  const text = `${props.title}${props.hashtags.length ? ' ' + props.hashtags.map(tag => '#' + tag).join(' ') : ''}`
  return `https://twitter.com/intent/tweet?text=${encodeText(text)}&url=${encodeText(currentUrl.value)}`
})

const facebookUrl = computed(() => {
  return `https://www.facebook.com/sharer/sharer.php?u=${encodeText(currentUrl.value)}`
})

const linkedinUrl = computed(() => {
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeText(currentUrl.value)}`
})

// Copy to clipboard
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(currentUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy: ', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = currentUrl.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

// Print page
const printPage = () => {
  window.print()
}

// Export data
const handleExport = (format) => {
  if (props.exportData && typeof props.exportData === 'function') {
    props.exportData(format)
  } else {
    emit('export', format)
  }
}
</script>
