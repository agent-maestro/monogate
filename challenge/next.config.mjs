/** @type {import('next').NextConfig} */
const nextConfig = {
  // monogate is ESM-only — tell Next.js to transpile it for server components
  transpilePackages: ["monogate"],
};

export default nextConfig;
