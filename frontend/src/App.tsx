import { useEffect } from 'react'
import { Header } from '@/components/layout/Header'
import { MainTabs } from '@/components/layout/MainTabs'
import { useThemeStore } from '@/store/themeStore'

function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    // Initialize theme on mount
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container py-8">
        <MainTabs />
      </main>
    </div>
  )
}

export default App
