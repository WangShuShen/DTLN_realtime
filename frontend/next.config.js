/** @type {import('next').NextConfig} */
const nextConfig = {
    env: {
        WEBSOCKET_SERVER_URL: process.env.WEBSOCKET_SERVER_URL,
      },
}

module.exports = nextConfig
