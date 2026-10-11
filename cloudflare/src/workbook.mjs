import { parseCSV } from "../shared/import.mjs";
import { extractContacts } from "../shared/contacts.mjs";

function valueText(value) {
  if (value == null) return "";
  if (typeof value !== "object") return String(value);
  if (value.richText) return value.richText.map((part) => valueText(part.text)).join("");
  return valueText(value.text ?? value.result);
}

function hyperlinkText(label, target) {
  const found = extractContacts([label]);
  // A label can contain the only phone number, including nested rich text.
  // Ordinary website labels still resolve to a clean URL for row matching.
  if (/^https?:/i.test(target) && !found.email && !found.phone && !found.whatsapp) return target;
  return `${label} ${target}`.trim();
}

export function cellText(cell) {
  const v = cell?.value;
  if (v == null) return "";
  if (typeof v !== "object") {
    if (typeof v === "number" && Number.isSafeInteger(v) && v >= 0 && /^0{7,15}$/.test(cell.numFmt || ""))
      return String(v).padStart(cell.numFmt.length, "0");
    return String(v);
  }
  if (v.formula) {
    const parts = v.formula.match(/^(?:_xlfn\.)?HYPERLINK\(\s*"((?:[^"\n]|"")+)"\s*[,;]\s*(?:"((?:[^"\n]|"")*)")?/i);
    const link = parts?.[1]?.replace(/""/g, '"');
    if (link && /^(https?:|mailto:|tel:)/i.test(link))
      return hyperlinkText(valueText(v.result) || parts?.[2]?.replace(/""/g, '"') || "", link);
  }
  if (v.hyperlink) {
    if (/^(https?:|mailto:|tel:)/i.test(v.hyperlink))
      return hyperlinkText(valueText(v.text), v.hyperlink);
  }
  return valueText(v);
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
