export const BASE_PATH = '/publicaciones';

export const publicaciones = [
  {
    id: 'afrodita-areia-volumen-IV',
    slug: 'afrodita-areia',
    volumeSlug: 'volumen-IV',
    title: 'Afrodita Areia',
    subtitle: 'Areópago',
    volume: 'Volumen IV',
    author: 'Miguel Hilario Olvera Aguilar',
    year: 2026,
    doi: '10.5281/zenodo.19601192',
    description:
      'Una ontología de la imputación causal, la jerarquía entre diseño y ejecución y el daño que el dolo deja sin autor visible.',
    cover: `${BASE_PATH}/libros/afrodita-areia/portada-volumen-IV.png`,
    pdf: `${BASE_PATH}/libros/afrodita-areia/volumen-IV.pdf`,
    href: '/libros/afrodita-areia/volumen-IV',
  },
  {
    id: 'afrodita-areia-volumen-III',
    slug: 'afrodita-areia',
    volumeSlug: 'volumen-III',
    title: 'Afrodita Areia',
    subtitle: 'Damasén',
    volume: 'Volumen III',
    author: 'Miguel Hilario Olvera Aguilar',
    year: 2026,
    doi: '10.5281/zenodo.19596275',
    description:
      'Una ontología del límite de la autodeterminación causal: Damasén y Peribea como figuras del Aego, del vínculo colapsado y de su escala colectiva.',
    cover: `${BASE_PATH}/libros/afrodita-areia/portada-volumen-III.png`,
    pdf: `${BASE_PATH}/libros/afrodita-areia/volumen-III.pdf`,
    href: '/libros/afrodita-areia/volumen-III',
  },
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

