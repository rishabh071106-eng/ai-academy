# Cloud track — the same lab on Amazon Web Services (and Snowflake on AWS)

Three exercises, in the order a data team at a bank would actually meet them.
Every one uses the CSV files produced by `python3 export_csv.py` (folder `csv/`).
All three fit inside the AWS Free Tier or a Snowflake trial; **delete resources when you finish** (last section).

> Why AWS when the job is at a custodian? Snowflake, the platform named in your prep material, runs *on*
> AWS, Azure or GCP. S3 buckets are the universal drop-box for files between banks and vendors.
> RDS is the managed Postgres you will meet behind internal tools. Confirm on Day 1 which cloud your team
> is approved to deploy to; the skills transfer regardless.

---

## Exercise 1 — Amazon RDS for PostgreSQL (a managed database you connect to like the local one)

**Time: ~25 minutes. Cost: free tier (db.t3.micro / db.t4g.micro, 20 GB).**

1. Sign in to the AWS console → search **RDS** → **Create database**.
2. Choose **Standard create** → Engine **PostgreSQL** (version 16.x) → Templates: **Free tier**.
3. Settings: DB instance identifier `custody-lab`, master username `lab`, master password: choose one (write it down; never commit it).
4. Instance: `db.t3.micro` (or `db.t4g.micro`). Storage: 20 GB gp3, disable autoscaling.
5. Connectivity: **Public access → Yes** (lab only — never for real bank data). VPC security group → **Create new**, name `custody-lab-sg`.
6. Additional configuration: Initial database name `custody_lab`. Uncheck automated backups and Performance Insights to keep it free. **Create database** (takes 5–10 min).
7. When status = *Available*, open the instance → **Connectivity & security** → copy the **Endpoint** (looks like `custody-lab.xxxxxxxx.ap-south-1.rds.amazonaws.com`).
8. Click the security group `custody-lab-sg` → **Inbound rules → Edit** → Add rule: Type **PostgreSQL**, Port 5432, Source **My IP** → Save.
9. Load the lab from your laptop (psql comes with the PostgreSQL install; DBeaver can also run the files with *Execute script*):
   ```bash
   export PGPASSWORD='<your password>'
   psql -h <endpoint> -U lab -d custody_lab -f schema.sql
   psql -h <endpoint> -U lab -d custody_lab -f seed.sql
   psql -h <endpoint> -U lab -d custody_lab -c "SELECT COUNT(*) FROM fact_positions;"   # expect 90
   ```
10. DBeaver → New connection → PostgreSQL → Host = endpoint, Port 5432, Database `custody_lab`, User `lab`, Password. **SSL tab → Use SSL** (RDS enforces it). Test connection → Finish.
11. Python: `PGHOST=<endpoint> PGPASSWORD='<pw>' python3 connect.py`
12. Run the 13 queries from `queries.sql` in DBeaver's SQL editor. They are identical to the local run — that is the point: **the client of a database never cares where the database lives.**

What to notice, as a product leader: the endpoint, the security-group rule and the SSL flag are the three things that break most "can't connect" tickets. Access control happened *outside* the database (the security group) before any username was checked — banks layer network, identity and data-level entitlements exactly like this.

---

## Exercise 2 — S3 + Athena (query files in a bucket with SQL, no server at all)

**Time: ~20 minutes. Cost: cents (Athena bills USD 5 per TB scanned; the lab is < 1 MB).**

This is the "data lake" pattern from your Day 18 chapter: raw files land in object storage, a serverless engine queries them in place.

1. `python3 export_csv.py` (creates `csv/*.csv`).
2. Console → **S3 → Create bucket**. Name must be globally unique, e.g. `custody-lab-<yourname>-2026`. Region: pick one and use the same region for Athena. Keep *Block all public access* ON. Create.
3. Upload the whole `csv/` folder into the bucket root (drag and drop in the console keeps the sub-folders). Athena and Snowflake read **folders**, not files, so you end up with:
   ```
   s3://custody-lab-<yourname>-2026/positions/fact_positions.csv
   s3://custody-lab-<yourname>-2026/trades/fact_trades.csv
   s3://custody-lab-<yourname>-2026/accounts/dim_account.csv
   s3://custody-lab-<yourname>-2026/securities/dim_security.csv
   ... (clients, dates, funds, transactions, corporate_actions, nav)
   ```
   (Or from a terminal with the AWS CLI: `aws s3 sync csv/ s3://custody-lab-<yourname>-2026/`)
4. Console → **Athena** → Query editor. First visit: *Settings → Manage → Query result location* → `s3://custody-lab-<yourname>-2026/athena-results/` → Save.
5. Open `aws/athena.sql`, replace `<bucket>` with your bucket name, run the four `CREATE EXTERNAL TABLE` statements one at a time, then the queries at the bottom.
6. Look at *Data scanned* under each result — that number **is** the bill. Then convert positions to Parquet with the `CTAS` statement at the end of the file and rerun: scanned bytes fall by ~10×. This is the conversation behind "why is our lake bill growing?".

---

## Exercise 3 — Snowflake trial on AWS, loading from your S3 bucket

**Time: ~30 minutes. Cost: free 30-day trial with USD 400 of credits.**

This is the closest thing to the platform your prep chapters describe (Alpha Data Platform-style cloud data, Secure Data Sharing, separate compute warehouses).

1. Go to signup.snowflake.com → Standard edition → Cloud provider **AWS** → the same region as your bucket. Activate from the email.
2. In Snowsight, open a new **SQL worksheet** and run `aws/snowflake.sql` section by section:
   - creates a tiny warehouse (`XSMALL`, auto-suspend 60 s — the cost-governance habit from Day 18),
   - creates database `CUSTODY_LAB` and the same tables,
   - loads the data — **Option A** pastes `seed.sql` (simplest), **Option B** stages the CSVs from S3 with `COPY INTO` (the real-world pattern),
   - runs the 13 queries (Snowflake accepts them unchanged; Q11 can also use Snowflake's `QUALIFY`),
   - creates a **secure view** row-filtered per client and shows Time Travel and zero-copy clone in one line each.
3. For Option B you need an IAM user with read access to the bucket: Console → **IAM → Users → Create user** `snowflake-reader` → *Attach policies directly* → `AmazonS3ReadOnlyAccess` → create → **Security credentials → Create access key** (use case: *Third-party service*). Paste the key id and secret into the `CREATE STAGE` statement. Delete the key when done.

---

## Clean up (do this — idle resources are the classic first cloud bill)

- RDS → select `custody-lab` → Actions → **Delete** (untick final snapshot, tick acknowledge).
- S3 → empty the bucket → delete the bucket.
- Athena → drop the tables (`DROP TABLE positions;` etc.). Tables only hold metadata; the data was in S3.
- IAM → delete the `snowflake-reader` access key and user.
- Snowflake → `DROP WAREHOUSE LAB_WH;` or just let the trial expire.
