<template>
  <div class="landing">
    <header class="hero">
      <div>
        <h1>TruLedgr</h1>
        <p class="tag">Secure, simple ledger & accounting for teams</p>
        <div class="cta">
          <a href="#get-started" class="btn primary">Get started</a>
          <a href="#docs" class="btn">Documentation</a>
        </div>
      </div>
      <img src="/hero-illustration.svg" alt="TruLedgr illustration" />
    </header>

    <section id="features" class="features">
      <div class="feature">
        <h3>Easy integration</h3>
        <p>Drop in APIs and SDKs for your backend and frontend.</p>
      </div>
      <div class="feature">
        <h3>Secure by design</h3>
        <p>Modern auth, encryption, and audit trails.</p>
      </div>
      <div class="feature">
        <h3>Cross-platform</h3>
        <p>Web, iOS, and Android support from the same API.</p>
      </div>
    </section>

    <section id="get-started" class="get-started">
      <h2>Quick start</h2>
      <pre><code>curl -s https://api.truledgr.local/health</code></pre>
      <p class="note">See the full setup in the documentation site.</p>
    </section>

    <footer class="site-footer">
      <small>© 2025 McGuire Technology</small>
    </footer>
  </div>
</template>

<script setup lang="ts">
// No runtime logic needed for the static landing sample.
</script>

<style scoped>
.landing { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; color:#0f172a; max-width:1100px; margin:0 auto; padding:24px }
.hero { display:flex; align-items:center; justify-content:space-between; gap:24px; padding:32px 0 }
.hero h1 { font-size:42px; margin:0 }
.tag { color:#334155 }
.cta { margin-top:12px }
.btn { display:inline-block; padding:10px 14px; border-radius:8px; text-decoration:none; border:1px solid #e2e8f0; color:inherit; margin-right:8px }
.primary { background:#0ea5a0; color:white; border: none }
.features { display:flex; gap:16px; margin-top:20px }
.feature { flex:1; background:#fff; padding:18px; border-radius:8px; box-shadow:0 1px 3px rgba(2,6,23,0.06) }
.get-started { margin-top:22px }
.site-footer { margin-top:36px; text-align:center; color:#475569 }
.note { color:#64748b }
pre { background:#f8fafc; padding:12px; border-radius:8px }
</style>
