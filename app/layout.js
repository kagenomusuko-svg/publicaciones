export const metadata = {
  title: 'Publicaciones',
  description: 'Repositorio de publicaciones de Meriadock',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
