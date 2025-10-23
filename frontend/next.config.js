/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://elca-mothership-api.onrender.com',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://elca-mothership-api.onrender.com',
    NEXT_PUBLIC_I18N_ENABLED: process.env.NEXT_PUBLIC_I18N_ENABLED || 'true',
    NEXT_PUBLIC_ACCESSIBILITY_MODE: process.env.NEXT_PUBLIC_ACCESSIBILITY_MODE || 'true',
    NEXT_PUBLIC_DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE || 'true'
  }
}

module.exports = nextConfig