/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  basePath: '/publicaciones',
  async rewrites() {
    return [
      {
        source: '/libros/afrodita-areia/volumen-I.pdf',
        destination:
          'https://raw.githubusercontent.com/kagenomusuko-svg/publicaciones/main/sobre-la-pasion/build/afrodita-areia-vol-i-sobre-la-pasion.pdf',
      },
      {
        source: '/libros/afrodita-areia/portada.png',
        destination:
          'https://raw.githubusercontent.com/kagenomusuko-svg/publicaciones/main/sobre-la-pasion/Portada%20Vol%20I%20red.png',
      },
    ];
  },
};

module.exports = nextConfig;
