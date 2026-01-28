import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Upload, Library, Search, BarChart3 } from 'lucide-react'
import { IngestPage } from '@/pages/IngestPage'
import { LibraryPage } from '@/pages/LibraryPage'
import { SearchPage } from '@/pages/SearchPage'
import { AnalyticsPage } from '@/pages/AnalyticsPage'

export function MainTabs() {
  return (
    <Tabs defaultValue="ingest" className="w-full">
      <TabsList className="grid w-full max-w-2xl mx-auto grid-cols-4 mb-8">
        <TabsTrigger value="ingest" className="flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Ingest
        </TabsTrigger>
        <TabsTrigger value="library" className="flex items-center gap-2">
          <Library className="h-4 w-4" />
          Library
        </TabsTrigger>
        <TabsTrigger value="search" className="flex items-center gap-2">
          <Search className="h-4 w-4" />
          Search
        </TabsTrigger>
        <TabsTrigger value="analytics" className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Analytics
        </TabsTrigger>
      </TabsList>

      <TabsContent value="ingest">
        <IngestPage />
      </TabsContent>

      <TabsContent value="library">
        <LibraryPage />
      </TabsContent>

      <TabsContent value="search">
        <SearchPage />
      </TabsContent>

      <TabsContent value="analytics">
        <AnalyticsPage />
      </TabsContent>
    </Tabs>
  )
}
