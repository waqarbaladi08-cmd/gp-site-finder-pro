import { parseCSV } from "../shared/import.mjs";

export function cellText(cell) {
  const v = cell?.value;
  if (v == null) return "";
  if (typeof v !== "object") return String(v);
  if (v.hyperlink) {
    if (/^(https?:|mailto:|tel:)/i.test(v.hyperlink))
      return /^https?:/i.test(v.hyperlink) && !/@/.test(v.text || "") ? v.hyperlink : `${v.text || ""} ${v.hyperlink}`.trim();
  }
  return String(v.text ?? (v.richText ? v.richText.map((x) => x.text).join("") : v.result ?? ""));
}

export async function readWorkbook(file) {
  if (file.size > 20 * 1024 * 1024) throw new Error("Please use a file smaller than 20 MB.");
  if (/\.(csv|tsv)$/i.test(file.name)) {
    const rows = parseCSV(await file.text(), /\.tsv$/i.test(file.name) ? "\t" : ",");
    if (rows.length > 50000) throw new Error("Split files with more than 50,000 rows into smaller files.");
    return [{ name: "Sheet", rows }];
  }
  if (!/\.xlsx$/i.test(file.name)) throw new Error("Use XLSX, CSV or TSV. Save older XLS files as XLSX first.");
  const { default: ExcelJS } = await import("exceljs");
  const wb = new ExcelJS.Workbook();
  await wb.xlsx.load(await file.arrayBuffer());
  return wb.worksheets.map((sheet) => {
    if (sheet.rowCount > 50000 || sheet.columnCount > 200) throw new Error("Use sheets with up to 50,000 rows and 200 columns.");
    const rows = [];
    sheet.eachRow({ includeEmpty: true }, (row) => rows.push(Array.from({ length: sheet.columnCount }, (_, i) => cellText(row.getCell(i + 1)))));
    return { name: sheet.name, rows };
  });
}
