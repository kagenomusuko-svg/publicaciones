import Link from 'next/link';
import PdfReader from '../../../components/PdfReader';
import { getPublicacion, publicaciones } from '../../../lib/catalogo';

export function generateStaticParams() {
  return publicaciones.map((publicacion) => ({
    slug: publicacion.slug,
    volumeSlug: publicacion.volumeSlug,
  }));
}

export default async function LibroPage({ params }) {
  const resolvedParams = await params;
  const publicacion = getPublicacion(
    resolvedParams.slug,
    resolvedParams.volumeSlug
  );

  if (!publicacion) {
    return (
      <main className="publicaciones-page">
        <h1>Publicación no encontrada</h1>
        <Link href="/libros">Volver a libros</Link>
      </main>
    );
  }

  return (
    <main className="publication-reader-page">
      <nav className="publication-reader-breadcrumb" aria-label="Ruta">
        <Link href="/">Publicaciones</Link>
        <span>›</span>
        <Link href="/libros">Libros</Link>
        <span>›</span>
        <span>{publicacion.title}</span>
      </nav>

      <div className="publication-reader-layout">
        <aside className="publication-reader-header">
          <div className="publication-reader-cover-wrap">
            <img
              src={publicacion.cover}
              alt={`Portada de ${publicacion.title}: ${publicacion.subtitle}`}
              className="publication-reader-cover"
            />
          </div>

          <div className="publication-reader-meta">
            <span className="publication-reader-volume">{publicacion.volume}</span>
            <h1>{publicacion.title}</h1>
            <h2>{publicacion.subtitle}</h2>
            <p className="publication-reader-author">{publicacion.author}</p>
            <p className="publication-reader-year">{publicacion.year}</p>
            {publicacion.doi && (
              <p className="publication-reader-doi">
                DOI:{' '}
                <a
                  href={`https://doi.org/${publicacion.doi}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {publicacion.doi}
                </a>
              </p>
            )}
            <p className="publication-reader-description">{publicacion.description}</p>
            <a
              href={publicacion.pdf}
              target="_blank"
              rel="noreferrer"
              className="publication-reader-direct"
            >
              Abrir PDF directamente ↗
            </a>
          </div>
        </aside>

        <section className="publication-reader-viewer" aria-label="Lector PDF">
          <PdfReader
            src={publicacion.pdf}
            title={`Lectura de ${publicacion.title}: ${publicacion.subtitle}`}
          />
          <p className="publication-reader-fallback">
            Si tu dispositivo no muestra el lector aquí,
            <a href={publicacion.pdf}>ábrelo directamente</a>.
          </p>
        </section>
      </div>
    </main>
  );
}
