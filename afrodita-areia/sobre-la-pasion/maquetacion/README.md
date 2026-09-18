# Maquetación — *Afrodita Areia: Sobre la pasión*

Este directorio contiene el maquetador del volumen.

## Criterio visual

- portada y contraportada: se usan las imágenes definitivas del directorio del libro sin regenerarlas;
- portadilla: composición editorial inspirada en la primera página de *HISTOS*, con sello institucional y amplia respiración vertical;
- cuerpo: sistema tipográfico derivado del PDF de *Diálogos Eleatas*;
- tipografía: EB Garamond;
- color institucional: `#1E4C45`;
- cuerpo: 10.5 pt, justificado, interlínea equivalente a 14 pt;
- márgenes A4: 78 pt superior, 58 pt laterales, 62 pt inferior;
- encabezado: sello + `AFRODITA AREIA · I` + `SOBRE LA PASIÓN`;
- pie: editor institucional + folio;
- preliminares: numeración romana;
- cuerpo: numeración arábiga desde el capítulo 1.

El sello se obtiene de la misma fuente utilizada por `dialogos-eleatas/src/lib/seal.ts`: `https://www.meriadock.org.mx/logo.svg`.

## Muestra actual

`build_sample.py` genera una prueba desde portada hasta `09.md` para validar portadilla, legales, epígrafe, índice, preliminares, apertura de parte y primer capítulo antes de extender la maquetación a todo el volumen.

La muestra `01–09` se genera automáticamente en CI para revisión visual antes de extender el diseño al volumen completo.
