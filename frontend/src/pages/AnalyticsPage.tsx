import { useVideos } from '@/hooks/useApi'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { BarChart3, Video, CheckCircle2, Clock, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const STATUS_COLORS = {
  completed: 'hsl(142, 76%, 36%)',
  processing: 'hsl(221, 83%, 53%)',
  pending: 'hsl(240, 5%, 65%)',
  failed: 'hsl(0, 84%, 60%)',
}

export function AnalyticsPage() {
  const { data: videos, isLoading } = useVideos()

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h2>
          <p className="text-muted-foreground mt-2">System usage and statistics</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const totalVideos = videos?.length || 0
  const completedVideos = videos?.filter(v => v.status === 'completed').length || 0
  const processingVideos = videos?.filter(v => v.status === 'processing').length || 0
  const failedVideos = videos?.filter(v => v.status === 'failed').length || 0

  const totalDuration = videos?.reduce((acc, v) => acc + (v.duration || 0), 0) || 0
  const totalHours = Math.floor(totalDuration / 3600)
  const totalMinutes = Math.floor((totalDuration % 3600) / 60)

  const statusData = [
    { name: 'Completed', value: completedVideos, color: STATUS_COLORS.completed },
    { name: 'Processing', value: processingVideos, color: STATUS_COLORS.processing },
    { name: 'Failed', value: failedVideos, color: STATUS_COLORS.failed },
  ].filter(item => item.value > 0)

  const recentVideos = videos
    ?.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 7)
    .reverse()

  const videosPerDay = recentVideos?.reduce((acc, video) => {
    const date = new Date(video.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const existing = acc.find(item => item.date === date)
    if (existing) {
      existing.count += 1
    } else {
      acc.push({ date, count: 1 })
    }
    return acc
  }, [] as { date: string; count: number }[]) || []

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-8 w-8 text-primary" />
          Analytics Dashboard
        </h2>
        <p className="text-muted-foreground mt-2">System usage and statistics</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Videos
            </CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalVideos}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {completedVideos} ready to search
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Completed
            </CardTitle>
            <CheckCircle2 className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{completedVideos}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalVideos > 0 ? Math.round((completedVideos / totalVideos) * 100) : 0}% success rate
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Processing
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{processingVideos}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Currently in progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Duration
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalHours > 0 ? `${totalHours}h ${totalMinutes}m` : `${totalMinutes}m`}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Indexed content
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Video Ingestion Trend</CardTitle>
            <CardDescription>Videos added over the last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            {videosPerDay.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={videosPerDay}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '6px',
                    }}
                  />
                  <Bar dataKey="count" fill="hsl(142, 76%, 36%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                No data available yet
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Distribution</CardTitle>
            <CardDescription>Current video processing status</CardDescription>
          </CardHeader>
          <CardContent>
            {statusData.length > 0 ? (
              <div className="flex items-center justify-center">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '6px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                No videos to display
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {totalVideos === 0 && (
        <Card>
          <CardContent className="pt-12 pb-12 flex flex-col items-center justify-center text-center space-y-4">
            <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center">
              <BarChart3 className="h-8 w-8 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">No analytics data yet</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Start by adding videos in the Ingest tab to see analytics
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
