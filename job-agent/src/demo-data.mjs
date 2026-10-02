// npm run demo-data — fills data/applications.json with sample rows to preview the dashboard.
import fs from "node:fs";
import { TRACKER_FILE } from "./tracker.mjs";

if (fs.existsSync(TRACKER_FILE) && !process.argv.includes("--force")) {
  console.log("data/applications.json already exists; pass --force to overwrite it with demo data.");
  process.exit(0);
}
const companies = ["Ziffity", "Codilar", "Embitel", "Webkul", "Ranosys", "Tata CLiQ", "Myntra", "Wipro", "Kensium", "Infosys", "Cybage", "Bounteous", "Publicis Sapient", "Nykaa", "Lenskart", "Accenture", "Capgemini", "Rapidops"];
const titles = ["Magento Developer", "Senior Magento Developer", "Adobe Commerce Developer", "Magento 2 Backend Developer", "PHP Developer (Magento)", "E-commerce Developer", "Lead Magento Developer"];
const statuses = ["applied", "applied", "applied", "applied", "interview", "rejected", "needs_attention", "external", "shortlisted", "skipped", "offer"];
const rows = [];
for (let i = 0; i < 46; i++) {
  const platform = i % 3 === 0 ? "naukri" : "linkedin";
  const days = Math.floor(Math.random() * 21);
  const at = new Date(Date.now() - days * 864e5 - Math.random() * 864e5).toISOString();
  const status = statuses[i % statuses.length];
  const score = status === "skipped" ? 40 + Math.floor(Math.random() * 25) : 70 + Math.floor(Math.random() * 28);
  rows.push({
    id: `${platform}:demo${i}`, platform, jobId: `demo${i}`,
    title: titles[i % titles.length], company: companies[(i * 7) % companies.length],
    location: ["Bengaluru", "Remote", "Hyderabad", "Pune"][i % 4],
    url: platform === "naukri" ? "https://www.naukri.com/" : "https://www.linkedin.com/jobs/",
    foundAt: at, updatedAt: at, appliedAt: ["applied", "interview", "rejected", "offer"].includes(status) ? at : undefined,
    status, matchScore: score,
    matchReasons: ["7 yrs Magento 1 & 2", "Custom module + REST API work", "Payment gateway integrations"],
    missingSkills: score < 80 ? ["Hyvä themes", "GraphQL"] : [],
    notes: "", history: [{ at, status, note: "demo" }],
  });
}
fs.writeFileSync(TRACKER_FILE, JSON.stringify(rows, null, 2));
console.log(`Wrote ${rows.length} demo rows. Delete data/applications.json before real use.`);
