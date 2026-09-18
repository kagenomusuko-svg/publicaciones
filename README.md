# publicaciones

Repositorio editorial de publicaciones.

## Estándar de maquetación para libros

La plantilla maestra vigente es el formato **6 × 9 pulgadas** consolidado en *Afrodita Areia I: Sobre la pasión*.

Documentación:
- `maquetacion/ESTANDAR_EDITORIAL.md`
- `maquetacion/estilo-libro-6x9.css`

Salvo decisión editorial expresa, los libros nuevos deben partir de este estándar.

## Catálogo web

Cada libro publicado debe incluir un archivo `publicacion.json` en la raíz de su carpeta editorial.

Ese manifiesto identifica, como mínimo:

- título;
- subtítulo;
- volumen, cuando corresponda;
- autor;
- año;
- descripción breve;
- portada;
- PDF definitivo.

El workflow `.github/workflows/catalogo-publicaciones.yml` recopila automáticamente todos esos manifiestos y genera `catalogo.json`.

El sitio institucional `kagenomusuko-svg/meriadock-site` consume ese catálogo para construir el carrusel **Publicaciones** de la página de inicio. Por tanto, una nueva publicación correctamente catalogada se incorpora al slider sin editar manualmente la home.
