import './globals.css';

export const metadata = {
  title: 'Publicaciones | Meriadock',
  description: 'Libros y publicaciones de Meriadock',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
