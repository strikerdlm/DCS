#!/usr/bin/env node
/** Run from the private Starflight workspace. The plan and receipts contain local data. */
import { createHash } from "node:crypto";
import { mkdir, readFile, rename, unlink, writeFile } from "node:fs/promises";
import { basename, dirname, resolve } from "node:path";
import { execFileSync } from "node:child_process";

const destination = "https://api.cloud.llamaindex.ai";
const version = "2026-10-16";
const tier = "agentic";
const rate = 10;

type Entry = {
  report_id: string;
  file: string;
  source_sha256: string;
  slice_sha256: string;
  physical_pages: number[];
  rights_evidence: string;
  subject_data_clearance: boolean;
};

type Plan = {
  credit_ceiling: number;
  verified_free_credits: number;
  quota_evidence: string;
  pdfinfo: string;
  entries: Entry[];
};

type Receipt = {
  phase: string;
  fileId?: string;
  jobId?: string;
  lastStatus?: string;
};

const hash = (data: Buffer | string) => createHash("sha256").update(data).digest("hex");

async function existing(path: string): Promise<Receipt | undefined> {
  try { return JSON.parse(await readFile(path, "utf8")); }
  catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

async function main() {
  const [mode, planPath, outputPath, reportId] = process.argv.slice(2);
  if (!["--dry-run", "--start-approved", "--poll"].includes(mode) || !planPath || !outputPath) {
    throw new Error("Usage: parse.ts --dry-run|--start-approved|--poll PLAN PRIVATE_OUTPUT [REPORT_ID]");
  }
  const plan: Plan = JSON.parse((await readFile(planPath, "utf8")).replace(/^\uFEFF/, ""));
  if (!Array.isArray(plan.entries) || !plan.entries.length || plan.entries.length > 3) {
    throw new Error("Supply one reviewed batch of up to three exact slices");
  }
  const entries = [];
  const ids = new Set<string>();
  let plannedPages = 0;
  for (const entry of plan.entries) {
    const pages = entry.physical_pages;
    if (!/^[A-Za-z0-9_.-]{1,100}$/.test(entry.report_id) || ids.has(entry.report_id) ||
        !pages.length || pages.some((n, i) => !Number.isInteger(n) || n < 1 || (i > 0 && n <= pages[i - 1])) ||
        !/^[a-f0-9]{64}$/.test(entry.source_sha256) || !/^[a-f0-9]{64}$/.test(entry.slice_sha256)) {
      throw new Error("Invalid or duplicate review manifest entry");
    }
    ids.add(entry.report_id);
    const path = resolve(dirname(planPath), entry.file);
    const bytes = await readFile(path);
    if (!path.toLowerCase().endsWith(".pdf") || bytes.length > 5_000_000 ||
        bytes.subarray(0, 5).toString() !== "%PDF-" || hash(bytes) !== entry.slice_sha256) {
      throw new Error("Staged PDF size, type or checksum differs from the reviewed copy");
    }
    const info = execFileSync(plan.pdfinfo, [path], { encoding: "utf8", timeout: 10000 });
    if (Number(info.match(/^Pages:\s+(\d+)/m)?.[1]) !== pages.length) {
      throw new Error("The approved page map and upload slice differ in page count");
    }
    plannedPages += pages.length;
    const key = hash(JSON.stringify([entry.slice_sha256, tier, version]));
    entries.push({ entry, path, bytes, key });
  }
  const plannedCredits = plannedPages * rate;
  const cleared = plan.entries.every(e => Boolean(e.rights_evidence?.trim()) && e.subject_data_clearance === true);
  const quotaOK = Number.isInteger(plan.credit_ceiling) && Number.isInteger(plan.verified_free_credits) &&
    plannedCredits <= plan.credit_ceiling && plannedCredits <= plan.verified_free_credits &&
    Boolean(plan.quota_evidence?.trim());
  if (plannedPages > 10 || plan.credit_ceiling > 100) throw new Error("Pilot batch exceeds the 10-page cap");
  if (mode === "--dry-run") {
    console.log(JSON.stringify({ destination, tier, version, plannedPages, plannedCredits, cleared, quotaOK,
      reports: entries.map(({ entry, key, bytes }) => ({ id: entry.report_id, key, bytes: bytes.length })) }));
    return;
  }
  const selected = entries.find(x => x.entry.report_id === reportId);
  if (!selected || !process.env.LLAMA_CLOUD_API_KEY) throw new Error("Expected one approved report and configured key");
  if (mode === "--start-approved" && (!cleared || !quotaOK)) {
    throw new Error("Document the right to use hosted processing, source privacy checks and verified free credits");
  }
  const directory = resolve(outputPath, selected.key);
  await mkdir(directory, { recursive: true });
  const lock = resolve(directory, "active.lock");
  await writeFile(lock, "Single worker\n", { flag: "wx" });
  const receiptPath = resolve(directory, "receipt.json");
  let receipt = await existing(receiptPath);
  async function checkpoint(next: Receipt) {
    const temp = resolve(directory, "receipt.tmp");
    await writeFile(temp, JSON.stringify({ ...next, parser: "LlamaParse", version, tier, destination,
      source_sha256: selected!.entry.source_sha256, slice_sha256: selected!.entry.slice_sha256, physical_pages: selected!.entry.physical_pages }, null, 2));
    await rename(temp, receiptPath);
    receipt = next;
  }
  try {
    const { default: LlamaCloud } = await import("@llamaindex/llama-cloud");
    const client = new LlamaCloud({ baseURL: destination, maxRetries: 0, timeout: 60_000 });
    if (mode === "--start-approved") {
      if (receipt) throw new Error("A prior submission is recorded. Poll a known job ID or reconcile the uncertain outcome.");
      await checkpoint({ phase: "upload_submitted_id_pending" });
      const file = await client.files.create({
        file: new File([new Uint8Array(selected.bytes)], basename(selected.path), { type: "application/pdf" }),
        purpose: "parse",
      });
      await checkpoint({ phase: "job_submitted_id_pending", fileId: file.id });
      const job = await client.parsing.create({ file_id: file.id, tier, version,
        output_options: { markdown: { tables: { output_tables_as_markdown: true } } } });
      await checkpoint({ phase: "pollable", fileId: file.id, jobId: job.id, lastStatus: job.status });
      console.log(JSON.stringify({ jobId: job.id, status: job.status }));
      return;
    }
    if (!receipt?.jobId) throw new Error("A known job ID is required. Check the receipt and provider before resubmitting.");
    const result = await client.parsing.get(receipt.jobId, { expand: ["markdown_full", "items"] });
    const status = result.job.status;
    if (status === "COMPLETED") {
      const markdown = result.markdown_full;
      if (!markdown?.trim()) throw new Error("Completed job did not return Markdown");
      await saveOutput(resolve(directory, "parsed.md"), markdown);
      if (result.items) await saveOutput(resolve(directory, "page-items.json"), JSON.stringify(result.items, null, 2));
    }
    await checkpoint({ ...receipt, phase: status === "COMPLETED" ? "parsed_pending_review" : "pollable", lastStatus: status });
    console.log(JSON.stringify({ jobId: result.job.id, status }));
  } finally {
    await unlink(lock);
  }
}

async function saveOutput(path: string, content: string) {
  try {
    const previous = await readFile(path, "utf8");
    if (previous !== content) throw new Error("Retrieved output differs from the existing receipt");
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
    await writeFile(path, content, { flag: "wx" });
  }
}

main().catch((error: Error & { status?: number }) => {
  console.error(error.status ? "Provider error status " + error.status : error.message);
  process.exitCode = 1;
});
