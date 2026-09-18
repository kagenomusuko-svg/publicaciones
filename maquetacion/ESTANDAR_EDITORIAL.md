# Estándar editorial de libros — Publicaciones Meriadock

Este repositorio adopta como plantilla maestra para libros la maquetación consolidada en **Afrodita Areia I: Sobre la pasión**.

## Formato base

- Tamaño de corte: **6 × 9 pulgadas** — 152,4 × 228,6 mm.
- Tipografía principal: **EB Garamond**.
- Cuerpo principal: **11,3 pt**.
- Interlineado: **1,33**.
- Texto: justificado.
- Color principal: `#262626`.
- Verde institucional: `#1E4C45`.
- Gris secundario: `#666666`.

## Caja y márgenes

- Superior: **19 mm**.
- Inferior: **19 mm**.
- Interior: **20 mm**.
- Exterior: **16,5 mm**.
- La página legal puede usar una caja ligeramente más cerrada: 22 / 16,5 / 22 / 20 mm.

## Identidad visual

Se conservan como rasgos del sistema editorial:

- sello institucional en encabezados;
- encabezado `AFRODITA AREIA · [volumen]` o equivalente de la obra/serie;
- título abreviado de la obra en el encabezado opuesto;
- filete fino gris bajo encabezados;
- filete fino gris sobre pies;
- folios discretos;
- preliminares en números romanos mayúsculos;
- cuerpo en números arábigos;
- filete verde corto y centrado bajo el título de capítulo;
- citas con barra vertical verde;
- aperturas de parte con sello, serie, filete y composición centrada;
- portadilla institucional con sello;
- separación entre párrafos como en la maqueta de referencia, sin introducir sangrías por defecto.

## Jerarquía

- Apertura de capítulo: número/denominación discreta + título destacado + filete verde + epígrafe.
- `h1`: 17 pt en texto general.
- `h2`: 14 pt.
- `h3`: 11,5 pt y verde institucional.
- Título principal de capítulo: 24 pt.
- Cuerpo: 11,3 pt.
- Notas y elementos secundarios pueden reducirse cuando la legibilidad lo justifique, sin romper el sistema visual.

## Principio de uso

**No se persigue un número de páginas.** La extensión resulta del contenido y de esta configuración editorial.

Este estándar debe ser el punto de partida de todos los libros del repositorio. Cada obra puede variar portada, contraportada, nombre de serie, títulos y activos propios, pero no debe rediseñarse la maqueta interior salvo que exista una razón editorial específica.

## Referencia autoritativa

La implementación de referencia es:

`sobre-la-pasion/maquetacion/build_full.py`

El CSS reutilizable se conserva en:

`maquetacion/estilo-libro-6x9.css`
