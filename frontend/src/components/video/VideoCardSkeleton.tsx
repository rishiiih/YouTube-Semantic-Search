import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export function VideoCardSkeleton() {
  return (
    <Card>
      <div className="p-6 space-y-4">
        <div className="space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <div className="flex gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-4 w-32" />
      </div>
    </Card>
  )
}
