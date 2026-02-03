import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { ComparacionTecnologias } from '@/services/api';

const FONT_SIZE_NORMAL = 10;
const FONT_SIZE_SMALL = 9;
const FONT_SIZE_TITLE = 16;
const FONT_SIZE_HEADING = 12;
const MARGIN = 20;
const LINE_HEIGHT = 6;

function addSectionTitle(doc: jsPDF, title: string, y: number): number {
  doc.setFontSize(FONT_SIZE_HEADING);
  doc.setFont('helvetica', 'bold');
  doc.text(title, MARGIN, y);
  return y + LINE_HEIGHT + 2;
}

function addParagraph(doc: jsPDF, text: string, y: number, maxWidth: number): number {
  doc.setFontSize(FONT_SIZE_NORMAL);
  doc.setFont('helvetica', 'normal');
  const lines = doc.splitTextToSize(text, maxWidth);
  doc.text(lines, MARGIN, y);
  return y + lines.length * LINE_HEIGHT + 4;
}

function addBulletList(doc: jsPDF, items: string[], y: number, maxWidth: number): number {
  doc.setFontSize(FONT_SIZE_SMALL);
  doc.setFont('helvetica', 'normal');
  let currentY = y;
  for (const item of items) {
    const lines = doc.splitTextToSize(`• ${item}`, maxWidth - 6);
    doc.text(lines, MARGIN + 4, currentY);
    currentY += lines.length * (LINE_HEIGHT - 1) + 2;
  }
  return currentY + 4;
}

export function exportComparacionToPdf(
  techA: string,
  techB: string,
  comparison: ComparacionTecnologias
): void {
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = doc.internal.pageSize.getWidth();
  const maxWidth = pageWidth - MARGIN * 2;
  let y = MARGIN;

  // Título
  doc.setFontSize(FONT_SIZE_TITLE);
  doc.setFont('helvetica', 'bold');
  doc.text('DevRadar Ecuador - Informe de Comparación', MARGIN, y);
  y += LINE_HEIGHT + 4;

  doc.setFontSize(FONT_SIZE_NORMAL);
  doc.setFont('helvetica', 'normal');
  doc.text(`${techA} vs ${techB}`, MARGIN, y);
  y += LINE_HEIGHT + 8;

  const a = comparison.tecnologia_a;
  const b = comparison.tecnologia_b;

  // Resumen por tecnología
  y = addSectionTitle(doc, 'Resumen por tecnología', y);
  y = addParagraph(
    doc,
    `${a.nombre}: ${a.vacantes_activas} vacantes activas, salario promedio $${Math.round(a.salario_promedio).toLocaleString()}/mes, cuota de mercado ${a.cuota_mercado}%.`,
    y,
    maxWidth
  );
  y = addParagraph(
    doc,
    `${b.nombre}: ${b.vacantes_activas} vacantes activas, salario promedio $${Math.round(b.salario_promedio).toLocaleString()}/mes, cuota de mercado ${b.cuota_mercado}%.`,
    y,
    maxWidth
  );
  y += 4;

  // Tabla comparativa
  y = addSectionTitle(doc, 'Comparativa', y);
  autoTable(doc, {
    startY: y,
    head: [['', a.nombre, b.nombre]],
    body: [
      ['Vacantes activas', String(a.vacantes_activas), String(b.vacantes_activas)],
      ['Salario promedio ($/mes)', String(Math.round(a.salario_promedio)), String(Math.round(b.salario_promedio))],
      ['Cuota de mercado (%)', `${a.cuota_mercado}%`, `${b.cuota_mercado}%`],
    ],
    margin: { left: MARGIN },
    theme: 'grid',
    headStyles: { fillColor: [59, 130, 246] },
  });
  y = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 10;

  // Tendencia histórica (tabla)
  if (comparison.tendencia_historica?.length) {
    y = addSectionTitle(doc, 'Tendencia (referencia)', y);
    autoTable(doc, {
      startY: y,
      head: [['Mes', techA, techB]],
      body: comparison.tendencia_historica.map((t) => [t.mes, String(t.valor_a), String(t.valor_b)]),
      margin: { left: MARGIN },
      theme: 'grid',
      headStyles: { fillColor: [100, 116, 139] },
    });
    y = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 10;
  }

  // Conclusiones y veredicto
  const c = comparison.conclusion;
  if (c.veredicto_final) {
    if (y > 250) { doc.addPage(); y = MARGIN; }
    y = addSectionTitle(doc, 'Veredicto final', y);
    y = addParagraph(doc, c.veredicto_final, y, maxWidth);
  }

  if (c.resumen_a || c.resumen_b) {
    if (y > 240) { doc.addPage(); y = MARGIN; }
    y = addSectionTitle(doc, 'Conclusiones', y);
    if (c.resumen_a) y = addParagraph(doc, `${a.nombre}: ${c.resumen_a}`, y, maxWidth);
    if (c.resumen_b) y = addParagraph(doc, `${b.nombre}: ${c.resumen_b}`, y, maxWidth);
    if (c.resumen_neutral) y = addParagraph(doc, `Neutral: ${c.resumen_neutral}`, y, maxWidth);
  }

  if (c.cosas_buenas_a?.length || c.cosas_buenas_b?.length) {
    if (y > 220) { doc.addPage(); y = MARGIN; }
    y = addSectionTitle(doc, 'Puntos fuertes', y);
    if (c.cosas_buenas_a?.length) {
      doc.setFont('helvetica', 'bold');
      doc.text(`${a.nombre}:`, MARGIN, y);
      y += LINE_HEIGHT;
      y = addBulletList(doc, c.cosas_buenas_a, y, maxWidth);
    }
    if (c.cosas_buenas_b?.length) {
      doc.setFont('helvetica', 'bold');
      doc.text(`${b.nombre}:`, MARGIN, y);
      y += LINE_HEIGHT;
      y = addBulletList(doc, c.cosas_buenas_b, y, maxWidth);
    }
  }

  // Pie
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(FONT_SIZE_SMALL);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `DevRadar Ecuador - Página ${i} de ${totalPages}`,
      pageWidth / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: 'center' }
    );
  }

  const fileName = `DevRadar-Comparacion-${techA}-vs-${techB}.pdf`.replace(/[^a-zA-Z0-9-_.]/g, '_');
  doc.save(fileName);
}
