# 📦 CSV to PostgreSQL ETL Pipeline

A beginner-friendly **Data Engineering** project that loads CSV data into a PostgreSQL database using Python.
Built to learn the core pillars of data engineering: **Linux**, **Cron Jobs**, **Python**, and **SQL**.

---

## 📚 What You Will Learn

| Topic | Concepts Covered |
|---|---|
| 🐧 Linux Basics | File system navigation, permissions, shell scripts |
| ⏰ Cron Jobs | Scheduling Python scripts to run automatically |
| 🐍 Python | pandas, psycopg2, dotenv, logging, modular code |
| 🗄️ SQL | DDL (CREATE TABLE), DML (INSERT), views, constraints |
| 🔄 ETL | Extract → Transform → Load pipeline pattern |

---

## 🗂️ Project Structure

```
csv-to-postgres-etl/
│
├── data/
│   └── sales.csv               # Sample input CSV file
│
├── config/
│   └── .env.example            # Template for environment variables
│
├── sql/
│   └── schema.sql              # Database schema (tables + views)
│
├── scripts/
│   ├── logger.py               # Logging utility (file + console)
│   └── db.py                   # PostgreSQL connection helper
│
├── logs/                       # Auto-created; ETL log files stored here
│
├── etl_pipeline.py             # 🚀 Main ETL script (Extract → Transform → Load)
├── setup_cron.sh               # Shell script to register cron job
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- **Python 3.9+**
- **PostgreSQL 13+**
- **pip** (Python package manager)

### Check versions

```bash
python3 --version
psql --version
pip --version
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/csv-to-postgres-etl.git
cd csv-to-postgres-etl
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=etl_db
DB_USER=postgres
DB_PASSWORD=your_password_here

CSV_FILE_PATH=data/sales.csv
LOG_DIR=logs
LOG_LEVEL=INFO
```

### 5. Set up the database

Open psql and create the database:

```bash
psql -U postgres
```

```sql
CREATE DATABASE etl_db;
\c etl_db
```

Then run the schema:

```bash
psql -U postgres -d etl_db -f sql/schema.sql
```

### 6. Run the ETL pipeline

```bash
python3 etl_pipeline.py
```

**Expected output:**

```
2024-01-15 02:00:00 | INFO     | main      | ============================================================
2024-01-15 02:00:00 | INFO     | main      | ETL PIPELINE STARTED  |  run_id=a1b2c3d4
2024-01-15 02:00:00 | INFO     | extract   | [EXTRACT] Reading file: data/sales.csv
2024-01-15 02:00:00 | INFO     | extract   | [EXTRACT] Rows extracted: 10
2024-01-15 02:00:00 | INFO     | transform | [TRANSFORM] Rows after transform: 10
2024-01-15 02:00:00 | INFO     | load      | [LOAD] Loaded: 10 | Failed: 0
2024-01-15 02:00:00 | INFO     | main      | ETL PIPELINE FINISHED | status=SUCCESS
```

---

## 🗄️ Database Tables

### `sales` — Main data table

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto-increment primary key |
| `order_id` | INTEGER UNIQUE | Original order ID from CSV |
| `customer_name` | VARCHAR(100) | Customer full name |
| `product` | VARCHAR(100) | Product name |
| `quantity` | INTEGER | Units ordered |
| `price` | NUMERIC(10,2) | Unit price |
| `order_date` | DATE | Date of order |
| `status` | VARCHAR(20) | completed / pending / cancelled |
| `loaded_at` | TIMESTAMP | When the row was inserted |

### `etl_logs` — Audit table

| Column | Type | Description |
|---|---|---|
| `run_id` | VARCHAR(50) | Unique ID per pipeline run |
| `run_at` | TIMESTAMP | When the run started |
| `file_name` | VARCHAR(255) | Source CSV filename |
| `rows_extracted` | INTEGER | Rows read from CSV |
| `rows_transformed` | INTEGER | Rows after cleaning |
| `rows_loaded` | INTEGER | Rows inserted into DB |
| `rows_failed` | INTEGER | Rows that failed |
| `status` | VARCHAR(20) | SUCCESS / FAILED / PARTIAL |
| `error_message` | TEXT | Error details if any |

### Query the data

```sql
-- View all sales
SELECT * FROM sales;

-- Check ETL run history
SELECT run_id, run_at, rows_loaded, status FROM etl_logs ORDER BY run_at DESC;

-- Revenue summary by status
SELECT * FROM sales_summary;
```

---

## 📄 Log Files

Logs are saved to the `logs/` folder automatically.

```
logs/
└── etl_2024-01-15.log    # One file per day
```

**Log format:**

```
2024-01-15 02:00:01 | INFO     | extract   | [EXTRACT] Rows extracted: 10
2024-01-15 02:00:01 | WARNING  | transform | [TRANSFORM] Dropped 1 rows with missing fields.
2024-01-15 02:00:02 | INFO     | load      | [LOAD] Loaded: 9 | Failed: 0
```

---

## ⏰ Schedule with Cron Job

Automate the pipeline to run every day at 2:00 AM.

### Quick setup (using the script)

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

### Manual setup

```bash
crontab -e
```

Add this line:

```
# Run ETL pipeline every day at 2:00 AM
0 2 * * * cd /full/path/to/csv-to-postgres-etl && python3 etl_pipeline.py >> logs/cron.log 2>&1
```

### Useful cron expressions

```
* * * * *        → Every minute
0 * * * *        → Every hour
0 2 * * *        → Every day at 2 AM
0 2 * * 1        → Every Monday at 2 AM
0 2 1 * *        → 1st of every month at 2 AM
```

### Verify cron is registered

```bash
crontab -l
```

---

## 🐧 Linux Commands Reference

Useful commands for this project:

```bash
# Navigate
cd csv-to-postgres-etl        # Enter project directory
ls -la                         # List all files with permissions
pwd                            # Print current directory

# File permissions
chmod +x setup_cron.sh         # Make script executable
ls -l setup_cron.sh            # Check permissions

# View logs in real time
tail -f logs/etl_2024-01-15.log

# Search inside logs
grep "ERROR" logs/etl_2024-01-15.log

# Check running Python processes
ps aux | grep python3

# Check cron service status (Linux)
systemctl status cron

# Connect to PostgreSQL
psql -U postgres -d etl_db
```

---

## 🔄 ETL Pipeline Flow

```
┌─────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   EXTRACT   │    │    TRANSFORM     │    │       LOAD         │
│             │    │                  │    │                    │
│  Read CSV   │───▶│  Strip spaces    │───▶│  INSERT into       │
│  file with  │    │  Parse dates     │    │  PostgreSQL        │
│  pandas     │    │  Drop nulls      │    │  ON CONFLICT       │
│             │    │  Validate status │    │  DO NOTHING        │
│             │    │  Remove dupes    │    │                    │
└─────────────┘    └──────────────────┘    └────────────────────┘
       │                    │                        │
       └────────────────────┴────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   ETL LOGS     │
                    │                │
                    │  File logs     │
                    │  DB audit log  │
                    └────────────────┘
```

---

## 🧪 Testing the Pipeline

### Test with a bad row

Add a row with missing data to `data/sales.csv`:

```
1099,,Laptop,1,50000.00,2024-01-25,completed
```

Re-run the pipeline — the row will be dropped and logged as a warning.

### Test duplicate handling

Add a row with an existing `order_id`. It will be silently skipped (`ON CONFLICT DO NOTHING`).

---

## 🤝 Contributing

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📖 Further Learning

- [psycopg2 docs](https://www.psycopg.org/docs/)
- [pandas docs](https://pandas.pydata.org/docs/)
- [PostgreSQL tutorial](https://www.postgresqltutorial.com/)
- [Crontab guru](https://crontab.guru/) — cron expression helper
- [Linux command cheatsheet](https://linuxcommand.org/)

---

## 📝 License

MIT License — free to use and modify.
