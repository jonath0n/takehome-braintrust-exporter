#!/usr/bin/env python3
import os, sys, argparse
from pathlib import Path

import pandas as pd
import braintrust
from braintrust_api import Braintrust as APIClient

# Helpers
def sanitize(s):
    return ''.join(c for c in s if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')[:100]

def mkdirs(base):
    exp_d = base / 'CSV' / 'Experiments'
    ds_d = base / 'CSV' / 'Datasets'
    exp_d.mkdir(parents=True, exist_ok=True)
    ds_d.mkdir(parents=True, exist_ok=True)
    return exp_d, ds_d

def dictify(o):
    if isinstance(o, dict):
        return o
    if hasattr(o, 'model_dump'):
        return o.model_dump()
    if hasattr(o, 'dict'):
        return o.dict()
    return o.__dict__

def select_proj(cli):
    projects = list(cli.projects.list())
    if not projects:
        sys.exit('No projects available')
    for idx, p in enumerate(projects, 1):
        print(f"{idx}: {p.name} ({p.id})")
    choice = int(input('Choose project: ')) - 1
    return projects[choice].id, projects[choice].name

# Main
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output-dir', default='.')
    p.add_argument('--api-url', default=os.getenv('BRAINTRUST_API_URL'))
    args = p.parse_args()

    key = os.getenv('BRAINTRUST_API_KEY') or sys.exit('Missing API key')
    base = Path(args.output_dir)
    exp_d, ds_d = mkdirs(base)

    client = APIClient(api_key=key, base_url=args.api_url)
    pid, proj_name = select_proj(client)

    # Experiments
    ex_rows = []
    for e in client.experiments.list(project_id=pid):
        print(f"Processing experiment: {e.name} ({e.id[:8]})")
        md = dictify(client.experiments.retrieve(e.id))
        sm = dictify(client.experiments.summarize(e.id))
        try:
            sdk = braintrust.init(project=proj_name, experiment=e.name, open=True)
            evs = [dictify(ev) for ev in sdk.fetch()]
        except Exception as err:
            print(f"Warning: failed to fetch experiment events for {e.name}: {err}")
            evs = [dictify(ev) for ev in sdk.fetch()]
        except Exception:
            evs = []
        if evs:
            pd.json_normalize(evs).to_csv(
                exp_d / f"{sanitize(e.name)}_{e.id[:8]}.csv", index=False
            )
        row = {'experiment_id': e.id, 'experiment_name': e.name}
        row.update(pd.json_normalize(md).iloc[0].to_dict())
        row.update(pd.json_normalize(sm).iloc[0].to_dict())
        ex_rows.append(row)
    pd.DataFrame(ex_rows).to_csv(exp_d / 'all_experiments.csv', index=False)

    # Datasets
    ds_rows = []
    for d in client.datasets.list(project_id=pid):
        print(f"Processing dataset: {d.name} ({d.id[:8]})")
        md = dictify(client.datasets.retrieve(d.id))
        resp = client.datasets.fetch(d.id)
        evs = [dictify(ev) for ev in (getattr(resp, 'events', []) or [])]
        if evs:
            pd.json_normalize(evs).to_csv(
                ds_d / f"{sanitize(d.name)}_{d.id[:8]}.csv", index=False
            )
        row = {'dataset_id': d.id, 'dataset_name': d.name}
        row.update(pd.json_normalize(md).iloc[0].to_dict())
        ds_rows.append(row)
    pd.DataFrame(ds_rows).to_csv(ds_d / 'all_datasets.csv', index=False)

    print(f"Done → Experiments: {exp_d}, Datasets: {ds_d}")

if __name__ == '__main__':
    main()
