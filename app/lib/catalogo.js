export const BASE_PATH = '/publicaciones';

export const publicaciones = [
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
