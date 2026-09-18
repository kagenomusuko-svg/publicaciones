import Link from 'next/link';
import { BASE_PATH } from './lib/catalogo';

export default function Home() {
  return (
    <main className="publicaciones-page">
      <header className="publicaciones-hero">
        <p className="eyebrow">Meriadock · Isla editorial</p>
        <h1>Publicaciones</h1>
        <p>
          Libros, investigaciones y obras de pensamiento desarrolladas en
          Meriadock.
        </p>
      </header>
      <p>
        <Link className="libro-action" href={`${BASE_PATH}/libros`}>
          Explorar libros →
        </Link>
      </p>
    </main>
  );
}
