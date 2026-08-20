import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: "https://baba-sika.onrender.com/api/:path*",
      },
    ];
  },
};

export default nextConfig;
