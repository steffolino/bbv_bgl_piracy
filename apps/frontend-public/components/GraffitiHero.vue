<template>
  <div class="hero min-h-[60vh] bg-gradient-to-br from-primary via-accent to-neutral flex flex-col items-center justify-center relative overflow-hidden graffiti-hero">
    <!-- Animated Logo -->
    <div class="relative z-10">
      <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="animate-bounce drop-shadow-2xl">
        <circle cx="60" cy="60" r="56" stroke="#C9A227" stroke-width="8" fill="#111111" />
        <text x="50%" y="50%" text-anchor="middle" dy=".35em" font-size="48" font-family="Impact, Arial Black, sans-serif" fill="#C53030" stroke="#F5F3E7" stroke-width="2">BBV</text>
      </svg>
    </div>
    <!-- Graffiti Title -->
    <h1 class="text-5xl md:text-7xl font-extrabold text-white graffiti-text mt-6 mb-2 animate-text-pop">BGL Basketball Portal</h1>
    <p class="text-xl md:text-2xl text-base-100 opacity-80 graffiti-subtitle mb-8 animate-fade-in">Real stats. Real teams. Real street.</p>
    <!-- Animated spray effect -->
    <div class="absolute left-0 top-0 w-full h-full pointer-events-none z-0">
      <svg width="100%" height="100%" viewBox="0 0 1200 400" fill="none" xmlns="http://www.w3.org/2000/svg" class="graffiti-spray">
        <ellipse cx="600" cy="200" rx="500" ry="80" fill="#C53030" fill-opacity="0.08">
          <animate attributeName="rx" values="500;520;500" dur="2s" repeatCount="indefinite" />
        </ellipse>
        <ellipse cx="600" cy="220" rx="400" ry="60" fill="#2563EB" fill-opacity="0.06">
          <animate attributeName="rx" values="400;420;400" dur="2s" repeatCount="indefinite" />
        </ellipse>
      </svg>
    </div>
  </div>
</template>

<script setup>
// No script needed for static hero
</script>

<style scoped>
.graffiti-hero {
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border-radius: 2rem;
  margin-bottom: 2rem;
}
.graffiti-text {
  text-shadow: 2px 4px 0 #C9A227, 0 2px 8px #111111;
  letter-spacing: 0.05em;
}
.graffiti-subtitle {
  text-shadow: 0 2px 8px #C53030;
}
.animate-text-pop {
  animation: text-pop 0.8s cubic-bezier(.68,-0.55,.27,1.55) both;
}
@keyframes text-pop {
  0% { transform: scale(0.7); opacity: 0; }
  80% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); }
}
.animate-fade-in {
  animation: fade-in 1.2s ease-in both;
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
