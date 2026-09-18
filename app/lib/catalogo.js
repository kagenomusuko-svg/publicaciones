export const BASE_PATH = '/publicaciones';

export const publicaciones = [
  {
    id: 'afrodita-areia-volumen-II',
    slug: 'afrodita-areia',
    volumeSlug: 'volumen-II',
    title: 'Afrodita Areia',
    subtitle: 'Ágape',
    volume: 'Volumen II',
    author: 'Miguel Hilario Olvera Aguilar',
    year: 2026,
    doi: '10.5281/zenodo.19601149',
    description:
      'Una ontología de las formas que adopta la voluntad al orientarse hacia la alteridad: Eros, Deimos, Anteros, Fobos, Potós y Harmonía.',
    cover: `${BASE_PATH}/libros/afrodita-areia/portada-volumen-II.png`,
    pdf: `${BASE_PATH}/libros/afrodita-areia/volumen-II.pdf`,
    href: '/libros/afrodita-areia/volumen-II',
  },
  {
    id: 'afrodita-areia-volumen-I',
    slug: 'afrodita-areia',
    volumeSlug: 'volumen-I',
    title: 'Afrodita Areia',
    subtitle: 'Sobre la pasión',
    volume: 'Volumen I',
    author: 'Miguel Hilario Olvera Aguilar',
    year: 2026,
    description:
      'Una ontología materialista de la determinación que piensa la pasión como fuerza anterior al sujeto consciente y recorre su desarrollo desde el caos hasta el ego.',
    cover: `${BASE_PATH}/libros/afrodita-areia/portada.png`,
    pdf: `${BASE_PATH}/libros/afrodita-areia/volumen-I.pdf`,
    href: '/libros/afrodita-areia/volumen-I',
  },
];

export function getPublicacion(slug, volumeSlug) {
  return publicaciones.find(
    (publicacion) =>
      publicacion.slug === slug && publicacion.volumeSlug === volumeSlug
  );
}
