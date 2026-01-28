# YouTube Semantic Search - Frontend

Modern React frontend for the YouTube Semantic Search application with Multi-Modal RAG backend.

## Features

- 🎨 Modern UI with Tailwind CSS and shadcn/ui
- 🌙 Dark mode support
- 📱 Fully responsive design
- ⚡ Lightning-fast with Vite
- 🔍 Semantic video search
- 💬 Chat-like Q&A interface
- 📊 Analytics dashboard
- 🎥 Inline YouTube player with timestamp navigation
- ♿ Accessible components

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Navigation
- **Axios** - HTTP client
- **Framer Motion** - Animations
- **Recharts** - Data visualization

## Getting Started

### Prerequisites

- Node.js 18+ or Bun
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:3000`

### Environment Variables

Copy `.env.example` to `.env` and update the values:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── video/       # Video-related components
│   │   ├── chat/        # Chat interface components
│   │   ├── analytics/   # Analytics dashboard components
│   │   └── layout/      # Layout components
│   ├── pages/           # Page components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── store/           # Zustand stores
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   └── lib/             # Library utilities
├── public/              # Static assets
└── index.html           # HTML entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint

## License

MIT
