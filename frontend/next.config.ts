import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    FLASK_BACKEND_URL: process.env.FLASK_BACKEND_URL || 'http://localhost:5000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:5000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
