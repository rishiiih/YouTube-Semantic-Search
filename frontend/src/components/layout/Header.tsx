import { Moon, Sun } from 'lucide-react'
import { useThemeStore } from '@/store/themeStore'
import { Button } from '@/components/ui/button'

export function Header() {
  const { theme, toggleTheme } = useThemeStore()

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <span className="text-xl font-bold text-primary-foreground">YT</span>
          </div>
          <div>
            <h1 className="text-xl font-bold">YouTube Semantic Search</h1>
            <p className="text-xs text-muted-foreground">AI-Powered Video Q&A</p>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  )
}
