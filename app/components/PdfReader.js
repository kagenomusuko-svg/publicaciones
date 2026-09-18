'use client';

import { useEffect, useRef, useState } from 'react';

function PdfPage({ pdf, pageNumber, scale, aspectRatio }) {
  const pageRef = useRef(null);
  const canvasRef = useRef(null);
  const [status, setStatus] = useState('Cargando…');

  useEffect(() => {
    let cancelled = false;
    let observer;

    async function renderPage() {
      try {
        setStatus('Cargando…');
        const page = await pdf.getPage(pageNumber);
        if (cancelled) return;

        const viewport = page.getViewport({ scale });
        const deviceScale = window.devicePixelRatio || 1;
        const canvas = canvasRef.current;
        const context = canvas?.getContext('2d');

        if (!canvas || !context) return;

        canvas.width = Math.floor(viewport.width * deviceScale);
        canvas.height = Math.floor(viewport.height * deviceScale);
        canvas.style.width = `${viewport.width}px`;
        canvas.style.height = `${viewport.height}px`;

        await page.render({
          canvasContext: context,
          viewport,
          transform: deviceScale !== 1
            ? [deviceScale, 0, 0, deviceScale, 0, 0]
            : null,
        }).promise;

        if (!cancelled) setStatus('');
      } catch (renderError) {
        if (!cancelled) setStatus('No se pudo mostrar esta página.');
      }
    }

    const element = pageRef.current;
    if (!element) return undefined;

    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(
        (entries) => {
          if (entries.some((entry) => entry.isIntersecting)) {
            observer.disconnect();
            renderPage();
          }
        },
        { rootMargin: '900px 0px' }
      );
      observer.observe(element);
    } else {
      renderPage();
    }

    return () => {
      cancelled = true;
      observer?.disconnect();
    };
  }, [pdf, pageNumber, scale]);

  return (
    <figure
      ref={pageRef}
      className="pdf-reader-page"
      style={{ aspectRatio }}
    >
      {status && <span className="pdf-reader-page-status">{status}</span>}
      <canvas
        ref={canvasRef}
        aria-label={`Página ${pageNumber}`}
      />
      <figcaption>Página {pageNumber}</figcaption>
    </figure>
  );
}

export default function PdfReader({ src, title }) {
  const loadingTaskRef = useRef(null);
  const [pdf, setPdf] = useState(null);
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.15);
  const [aspectRatio, setAspectRatio] = useState('0.707 / 1');
  const [status, setStatus] = useState('Cargando lector…');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadDocument() {
      setStatus('Cargando PDF…');
      setError('');
      setPdf(null);
      setNumPages(0);

      try {
        const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
        pdfjs.GlobalWorkerOptions.workerSrc =
          'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs';

        const loadingTask = pdfjs.getDocument({ url: src });
        loadingTaskRef.current = loadingTask;
        const loadedPdf = await loadingTask.promise;

        if (cancelled) {
          await loadedPdf.destroy();
          return;
        }

        const firstPage = await loadedPdf.getPage(1);
        const firstViewport = firstPage.getViewport({ scale: 1 });
        firstPage.cleanup();

        setAspectRatio(`${firstViewport.width} / ${firstViewport.height}`);
        setPdf(loadedPdf);
        setNumPages(loadedPdf.numPages);
        setStatus('');
      } catch (loadError) {
        if (!cancelled) {
          setStatus('');
          setError('No se pudo cargar el lector interno.');
        }
      }
    }

    loadDocument();

    return () => {
      cancelled = true;
      loadingTaskRef.current?.destroy();
      loadingTaskRef.current = null;
      pdf?.destroy();
    };
  }, [src]);

  return (
    <div className="pdf-reader" aria-label={title}>
      <div className="pdf-reader-toolbar">
        <span>{numPages ? `${numPages} páginas` : 'Cargando páginas…'}</span>
        <span className="pdf-reader-toolbar-hint">Desplázate para leer</span>
        <span className="pdf-reader-toolbar-spacer" />
        <button
          type="button"
          onClick={() => setScale((current) => Math.max(0.8, current - 0.15))}
          aria-label="Reducir zoom"
        >
          −
        </button>
        <span>{Math.round(scale * 100)}%</span>
        <button
          type="button"
          onClick={() => setScale((current) => Math.min(2, current + 0.15))}
          aria-label="Aumentar zoom"
        >
          +
        </button>
      </div>

      <div className="pdf-reader-canvas-wrap">
        {status && <p className="pdf-reader-status">{status}</p>}
        {error && (
          <p className="pdf-reader-error">
            {error}{' '}
            <a href={src} target="_blank" rel="noreferrer">
              Abrir PDF directamente
            </a>
          </p>
        )}

        {pdf && (
          <div className="pdf-reader-document">
            {Array.from({ length: numPages }, (_, index) => (
              <PdfPage
                key={index + 1}
                pdf={pdf}
                pageNumber={index + 1}
                scale={scale}
                aspectRatio={aspectRatio}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
