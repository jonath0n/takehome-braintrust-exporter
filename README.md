# Braintrust Exporter

Command-line tool to export Braintrust experiments and datasets to CSV.

---

## Requirements
- Python 3.9+
- [Braintrust API Key](https://docs.braintrust.dev)
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Setup

### Clone the Repository
```bash
git clone <repository_url>
```

### Environment Variables
Set the required environment variables in your shell or create a `.env` file:

```env
BRAINTRUST_API_KEY=your_api_key
BRAINTRUST_API_URL=https://api.braintrust.com  # Optional, can also be set via --api-url
```

### Usage
Run the script to export data:
```bash
python braintrust_exporter.py --output-dir ./output
```

**Arguments:**
- `--output-dir` (optional): Destination folder for exported CSVs. Defaults to the current directory.
- `--api-url` (optional): Braintrust API URL. Defaults to the `BRAINTRUST_API_URL` environment variable.

The script will prompt you to select a project and then export the following:

- **CSV/Experiments**
- **CSV/Datasets**

### Output
The script creates a structured output with the following organization:
- Individual CSV files for each experiment in `CSV/Experiments/` directory
- Individual CSV files for each dataset in `CSV/Datasets/` directory  
- Aggregated files: `CSV/Experiments/all_experiments.csv` and `CSV/Datasets/all_datasets.csv`

### Notes
- Environment variables can be set in your shell or via a `.env` file (not committed to version control).
- The script requires interactive input to choose a project from your available Braintrust projects.
- API key is required via the `BRAINTRUST_API_KEY` environment variable.