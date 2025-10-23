'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'
import { Toaster } from '@/components/ui/toaster'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-900">
        <QueryClientProvider client={queryClient}>
          <div className="min-h-screen">
            {children}
          </div>
          <Toaster />
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </body>
    </html>
  )
}
