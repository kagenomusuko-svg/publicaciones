import Link from 'next/link';
import { BASE_PATH, publicaciones } from '../lib/catalogo';

export default function LibrosPage() {
  return (
    <main className="publicaciones-page">
      <header className="publicaciones-hero">
        <p className="eyebrow">Meriadock · Publicaciones</p>
        <h1>Libros</h1>
        <p>
          Obras de investigación, pensamiento y creación desarrolladas en el
          Centro Multidisciplinario Meriadock.
        </p>
      </header>

      <section className="publicaciones-grid" aria-label="Libros publicados">
        {publicaciones.map((publicacion) => (
          <Link
            key={publicacion.id}
            href={publicacion.href}
            className="libro-card-link"
          >
            <article className="libro-card">
              <div className="libro-cover-wrap">
                <img src={publicacion.cover} alt={`Portada de ${publicacion.title}`} />
              </div>
              <div className="libro-card-content">
                <span className="eyebrow">{publicacion.volume}</span>
                <h2>{publicacion.title}</h2>
                <p className="libro-subtitle">{publicacion.subtitle}</p>
                <p>{publicacion.description}</p>
                <span className="libro-action">Leer publicación →</span>
              </div>
            </article>
          </Link>
        ))}
      </section>

      <p className="publicaciones-back">
        <Link href="/">← Volver a Publicaciones</Link>
      </p>
    </main>
  );
}
