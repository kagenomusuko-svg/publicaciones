'use client';

import { useEffect, useRef, useState } from 'react';

export default function PdfReader({ src, title }) {
  const canvasRef = useRef(null);
  const pdfRef = useRef(null);
  const loadingTaskRef = useRef(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [numPages, setNumPages] = useState(0);
  const [scale, setScale] = useState(1.15);
  const [status, setStatus] = useState('Cargando lector…');
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadDocument() {
      setStatus('Cargando PDF…');
      setError('');
      setNumPages(0);
      setPageNumber(1);

      try {
        const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
        pdfjs.GlobalWorkerOptions.workerSrc =
          'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs';
        const loadingTask = pdfjs.getDocument({ url: src });
        loadingTaskRef.current = loadingTask;

        const pdf = await loadingTask.promise;
        if (cancelled) {
          await pdf.destroy();
          return;
        }

        pdfRef.current = pdf;
        setNumPages(pdf.numPages);
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
      pdfRef.current?.destroy();
      pdfRef.current = null;
    };
  }, [src]);

  useEffect(() => {
    let cancelled = false;

    async function renderPage() {
      const pdf = pdfRef.current;
      const canvas = canvasRef.current;

      if (!pdf || !canvas || !numPages) return;

      try {
        setStatus('Preparando página…');
        const page = await pdf.getPage(pageNumber);
        if (cancelled) return;

        const viewport = page.getViewport({ scale });
        const deviceScale = window.devicePixelRatio || 1;
        const context = canvas.getContext('2d');

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
        if (!cancelled) setError('No se pudo mostrar esta página.');
      }
    }

    renderPage();

    return () => {
      cancelled = true;
    };
  }, [numPages, pageNumber, scale]);

  function previousPage() {
    setPageNumber((current) => Math.max(1, current - 1));
  }

  function nextPage() {
    setPageNumber((current) => Math.min(numPages, current + 1));
  }

  return (
    <div className="pdf-reader" aria-label={title}>
      <div className="pdf-reader-toolbar">
        <button type="button" onClick={previousPage} disabled={pageNumber <= 1}>
          ‹
        </button>
        <span>
          Página {numPages ? pageNumber : '—'} de {numPages || '—'}
        </span>
        <button type="button" onClick={nextPage} disabled={!numPages || pageNumber >= numPages}>
          ›
        </button>
        <span className="pdf-reader-toolbar-spacer" />
        <button type="button" onClick={() => setScale((current) => Math.max(0.8, current - 0.15))}>
          −
        </button>
        <span>{Math.round(scale * 100)}%</span>
        <button type="button" onClick={() => setScale((current) => Math.min(2, current + 0.15))}>
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
        <canvas ref={canvasRef} aria-label={`Página de ${title}`} />
      </div>
    </div>
  );
}
