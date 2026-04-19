/** @type {import('next').NextConfig} */
const nextConfig = {
  // monogate is ESM-only — tell Next.js to transpile it for server components
  transpilePackages: ["monogate"],
  async redirects() {
    return [
      {
        source: "/games",
        destination: "https://monogames.vercel.app",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
