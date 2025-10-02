<template>
  <dialog ref="cardModal" class="modal">
    <div class="modal-box max-w-md">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">🏀 Basketball Card</h3>
        <button @click="closeModal" class="btn btn-sm btn-ghost">✕</button>
      </div>
      
      <div class="flex justify-center mb-4">
        <BasketballCard :player="player" :card-width="280" :card-height="390" />
      </div>
      
      <div class="modal-action">
        <button @click="downloadCard" class="btn btn-primary">
          📥 Download PNG
        </button>
        <button @click="shareCard" class="btn btn-secondary">
          🔗 Share
        </button>
        <button @click="closeModal" class="btn">Close</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>

<script setup>
import { ref, defineExpose } from 'vue'

const props = defineProps({
  player: {
    type: Object,
    required: true
  }
})

const cardModal = ref(null)

const showModal = () => {
  cardModal.value?.showModal()
}

const closeModal = () => {
  cardModal.value?.close()
}

const downloadCard = async () => {
  try {
    const { default: html2canvas } = await import('html2canvas')
    
    const cardElement = document.querySelector('.basketball-card')
    if (!cardElement) {
      console.error('Card element not found')
      return
    }
    
    const canvas = await html2canvas(cardElement, {
      backgroundColor: '#ffffff',
      scale: 3, // High quality
      useCORS: true,
      allowTaint: true,
      logging: false
    })
    
    canvas.toBlob((blob) => {
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${props.player.name?.replace(/\s+/g, '_') || 'basketball_player'}_card.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }, 'image/png', 0.95)
    
  } catch (error) {
    console.error('Error generating card:', error)
    alert('Failed to generate card. Please try again.')
  }
}

const shareCard = () => {
  const playerName = props.player.name || 'Basketball Player'
  const team = props.player.team || 'Team'
  const stats = `${props.player.points || 0} Pts, ${props.player.games || 0} G, ${props.player.average?.toFixed(1) || 'N/A'} Avg`
  
  const shareText = `🏀 Check out this Basketball Card!\n\n${playerName} - ${team}\n${stats}\n\nGenerated from BBV BGL Basketball Portal`
  
  if (navigator.share) {
    navigator.share({
      title: `Basketball Card: ${playerName}`,
      text: shareText,
      url: window.location.href
    }).catch(console.error)
  } else {
    // Fallback: Copy to clipboard
    navigator.clipboard.writeText(shareText).then(() => {
      alert('Card info copied to clipboard!')
    }).catch(() => {
      alert('Failed to copy. Please try again.')
    })
  }
}

defineExpose({
  showModal,
  closeModal
})
</script>
