<template>
  <div class="landing">
    <div class="hero">
      <div class="container">
        <h1 class="title">{{ title }}</h1>
        <div class="greeting">{{ greeting }}</div>
        <p class="subtitle">{{ subtitle }}</p>
        
        <div class="features">
          <div v-for="feature in features" :key="feature.title" class="feature">
            <h3>{{ feature.icon }} {{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
        
        <div class="cta">
          <a v-for="link in ctaLinks" :key="link.text" :href="link.url" class="btn" target="_blank">
            {{ link.text }}
          </a>
        </div>
        
        <div class="status-section">
          <h3>Development Status</h3>
          <div class="status-grid">
            <div v-for="app in apps" :key="app.name" class="status-card">
              <h4>{{ app.name }}</h4>
              <div :class="['status', app.status]">{{ app.statusText }}</div>
              <p>{{ app.description }}</p>
              <div class="tech-stack">
                <span v-for="tech in app.technologies" :key="tech" class="tech-tag">
                  {{ tech }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      title: 'TruLedgr',
      greeting: 'Bonjour!',
      subtitle: 'Your comprehensive personal finance application suite',
      features: [
        {
          icon: '📱',
          title: 'Multi-Platform',
          description: 'Web, iOS, macOS, and Android applications'
        },
        {
          icon: '📊',
          title: 'Monthly Focus',
          description: 'Built around monthly financial cycles and reporting'
        },
        {
          icon: '🏦',
          title: 'Complete Suite',
          description: 'From daily transactions to estate and tax planning'
        },
        {
          icon: '🔒',
          title: 'Secure',
          description: 'OAuth2 authentication with multiple providers'
        }
      ],
      ctaLinks: [
        {
          text: 'Launch Web App',
          url: 'http://localhost:3000'
        },
        {
          text: 'API Documentation',
          url: 'http://localhost:8000/docs'
        },
        {
          text: 'Project Documentation',
          url: 'http://localhost:8001'
        }
      ],
      apps: [
        {
          name: 'FastAPI Backend',
          status: 'ready',
          statusText: '✅ Ready',
          description: 'Core API with "Bonjour" endpoint',
          technologies: ['FastAPI', 'Python', 'Poetry']
        },
        {
          name: 'Vue.js Web App',
          status: 'ready',
          statusText: '✅ Ready',
          description: 'Responsive web interface with API testing',
          technologies: ['Vue 3', 'Vite', 'JavaScript']
        },
        {
          name: 'iOS/macOS App',
          status: 'ready',
          statusText: '✅ Ready',
          description: 'Native Apple Multiplatform application',
          technologies: ['SwiftUI', 'Swift Package Manager']
        },
        {
          name: 'Android App',
          status: 'ready',
          statusText: '✅ Ready',
          description: 'Modern Android app with Material Design 3',
          technologies: ['Jetpack Compose', 'Kotlin', 'Material 3']
        },
        {
          name: 'Documentation',
          status: 'ready',
          statusText: '✅ Ready',
          description: 'Comprehensive project documentation',
          technologies: ['MkDocs', 'Material Theme']
        }
      ]
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.landing {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.container {
  text-align: center;
  max-width: 1200px;
  padding: 2rem;
  width: 100%;
}

.title {
  font-size: 4rem;
  margin-bottom: 1rem;
  font-weight: 300;
}

.greeting {
  font-size: 2.5rem;
  margin-bottom: 2rem;
  color: #fff;
  font-weight: 500;
}

.subtitle {
  font-size: 1.5rem;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.feature {
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 15px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease, background 0.3s ease;
}

.feature:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.feature h3 {
  margin-bottom: 1rem;
  color: #fff;
  font-size: 1.2rem;
}

.feature p {
  opacity: 0.9;
  line-height: 1.6;
}

.cta {
  margin-bottom: 4rem;
}

.btn {
  display: inline-block;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  margin: 0.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.status-section {
  background: rgba(255, 255, 255, 0.1);
  padding: 3rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-section h3 {
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #fff;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.status-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: left;
}

.status-card h4 {
  margin-bottom: 0.5rem;
  color: #fff;
  font-size: 1.1rem;
}

.status {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1rem;
  display: inline-block;
}

.status.ready {
  background: rgba(40, 167, 69, 0.3);
  color: #28a745;
  border: 1px solid rgba(40, 167, 69, 0.5);
}

.status-card p {
  opacity: 0.9;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-tag {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .title {
    font-size: 2.5rem;
  }
  
  .greeting {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
  
  .container {
    padding: 1rem;
  }
  
  .status-section {
    padding: 2rem;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>