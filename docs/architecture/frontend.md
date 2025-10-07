# Frontend Architecture

## Vue.js Web Application

The web frontend is built with Vue.js 3 using the Composition API and Vite for fast development and building.

## Technology Stack

- **Vue.js 3**: Modern reactive framework with Composition API
- **Vite**: Fast build tool and development server
- **TypeScript**: Type safety (planned)
- **Vue Router**: Client-side routing (planned)
- **Pinia**: State management (planned)

## Project Structure

```
truledgr_dashboard/
├── src/
│   ├── components/         # Reusable Vue components
│   ├── views/             # Page-level components
│   ├── stores/            # Pinia stores for state management
│   ├── services/          # API service functions
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.vue            # Root component
│   └── main.js            # Application entry point
├── public/                # Static assets
├── index.html             # HTML template
├── vite.config.js         # Vite configuration
└── package.json           # Dependencies and scripts
```

## Key Features

### Responsive Design
- Mobile-first approach
- Responsive breakpoints for tablet and desktop
- Touch-friendly interface elements

### API Integration
- Centralized API service layer
- Error handling and loading states
- Automatic retry for failed requests

### Monthly Cycle Focus
- Dashboard centered on current month
- Monthly report generation
- Recurring transaction management

## Development

```bash
cd truledgr_vue
npm install
npm run dev
```

The development server runs on `http://localhost:3000` with hot module replacement.

## Build Process

```bash
npm run build    # Production build
npm run preview  # Preview production build
```

## Styling

- CSS3 with modern features
- CSS Grid and Flexbox for layouts
- CSS Custom Properties for theming
- Responsive design patterns

## State Management

- Local component state with `ref()` and `reactive()`
- Pinia stores for global state (planned)
- API state management with composables
