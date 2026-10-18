# Runbook: Database Backups & Point-in-Time Restore (Layer 3e)

## 1. Backup Policy & Schedule

| Parameter | Production Policy |
|---|---|
| **Frequency** | Automated daily at 02:00 UTC; manual snapshot before every schema migration |
| **Retention Policy** | 7 daily backups, 4 weekly backups, 12 monthly backups (Grandfather-Father-Son rotation) |
| **Storage Destination** | Railway Volume / Cloudflare R2 encrypted bucket (`/backups/cropconnect_YYYYMMDD_HHMMSS.sql.gz`) |
| **Compression & Encryption** | gzip compression (`-9`); encrypted using AES-256 via storage bucket policies |
| **Tested Restore Frequency** | Verified weekly into a separate sandbox database |

---

## 2. Taking an On-Demand Backup

To take a manual backup before deploying migrations or critical fixes:

```bash
# In Railway production container or local machine with DB connection variables:
bash cropconnect-backend/scripts/backup_db.sh
```

Or via direct mysqldump:
```bash
mysqldump \
  -h "$MYSQL_HOST" \
  -P "$MYSQL_PORT" \
  -u "$MYSQL_USER" \
  -p"$MYSQL_PASSWORD" \
  --single-transaction \
  --quick \
  --routines \
  --triggers \
  "$MYSQL_DATABASE" | gzip > "/backups/cropconnect_manual_$(date +%Y%m%d_%H%M%S).sql.gz"
```

Verify archive creation and size:
```bash
ls -lh /backups/
```

---

## 3. Step-by-Step Point-in-Time Restore Instructions

> [!WARNING]
> Restoring a backup into production overwrites live data. Always execute a fresh manual backup of the current state before initiating any restore.

### Step 1: Quarantine & Put System in Maintenance Mode
1. In Vercel, set maintenance header or pause incoming frontend traffic if necessary.
2. In Railway, confirm no writes are occurring to the target database.

### Step 2: Select the Target Backup Archive
List available backup snapshots:
```bash
ls -lt /backups/cropconnect_*.sql.gz
```
Identify the snapshot corresponding to the recovery objective timestamp.

### Step 3: Test Restore into Isolated Sandbox Database First
Before touching production, execute the restore verification script to confirm archive integrity:
```bash
python cropconnect-backend/scripts/test_restore_db.py /backups/cropconnect_TARGET.sql.gz
```

### Step 4: Execute Production Restore
```bash
# 1. Unzip and pipe the SQL dump directly into MySQL
gunzip < /backups/cropconnect_TARGET.sql.gz | \
  mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"
```

### Step 5: Post-Restore Verification
1. Run database migrations to ensure schema aligns with the running codebase version:
   ```bash
   python cropconnect-backend/migrate_db.py
   ```
2. Verify system health via HTTP check:
   ```bash
   curl -s https://cropconnect01-production.up.railway.app/api/health
   # Expected: {"status":"ok","db":"ok"}
   ```
3. Log in with a demo account and verify that recent sensor telemetry and pump states render accurately.
