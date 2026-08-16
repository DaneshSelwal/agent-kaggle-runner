import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import tempfile
from pathlib import Path

def detect_accelerator(notebook_path: str) -> str:
    """Read the notebook and detect if GPU/TPU is needed."""
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read {notebook_path} to detect accelerator: {e}")
        return "cpu"

    dl_keywords = [
        "torch.cuda", "import torch", "import torchvision", 
        "import tensorflow", "import keras", "import jax",
        "to('cuda')", ".cuda()", "tf.config"
    ]
    
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            for kw in dl_keywords:
                if kw in source:
                    print(f"Auto-detected deep learning hint '{kw}'. Using GPU.")
                    return "gpu"
                    
    print("No deep learning hints detected. Using CPU.")
    return "cpu"

def run_command(cmd, capture_output=True, check=True):
    """Run a shell command, returning its stdout/stderr or raising informative errors."""
    try:
        res = subprocess.run(cmd, capture_output=capture_output, text=True, check=check)
        return res.stdout
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr if e.stderr else e.stdout
        if err_msg:
            err_msg = err_msg.lower()
            if "unauthorized" in err_msg or "could not find kaggle.json" in err_msg:
                print("Error: Kaggle authentication failed. Make sure ~/.kaggle/kaggle.json exists or KAGGLE_API_TOKEN is set.")
            elif "quota" in err_msg:
                print("Error: Kaggle API quota exceeded or GPU hours depleted.")
            elif "dataset not found" in err_msg or "404" in err_msg:
                print("Error: One or more datasets were not found. Check the slugs.")
            else:
                print(f"Error running command {' '.join(cmd)}:\n{e.stderr or e.stdout}")
        else:
            print(f"Error running command {' '.join(cmd)}. Exit code {e.returncode}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run a Jupyter Notebook on Kaggle.")
    parser.add_argument("--notebook", required=True, help="Path to the .ipynb file")
    parser.add_argument("--dataset", action="append", default=[], help="Dataset slug(s) to attach (e.g. username/dataset)")
    parser.add_argument("--target", required=True, help="Target kernel slug (e.g. username/kernel-slug)")
    parser.add_argument("--accelerator", choices=["auto", "cpu", "gpu", "tpu"], default="auto", help="Hardware accelerator to use")
    parser.add_argument("--title", help="Title for the Kaggle Kernel")
    parser.add_argument("--output-dir", default="./results", help="Directory to save kernel outputs")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds for polling")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without hitting the Kaggle API")
    
    args = parser.parse_args()

    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"Error: Notebook {notebook_path} does not exist.")
        sys.exit(1)

    # 1. Determine accelerator
    accelerator = args.accelerator
    if accelerator == "auto":
        accelerator = detect_accelerator(args.notebook)

    enable_gpu = "true" if accelerator == "gpu" else "false"
    enable_tpu = "true" if accelerator == "tpu" else "false"
    
    title = args.title if args.title else args.target.split("/")[-1].replace("-", " ").title()

    # 2. Build metadata
    metadata = {
        "id": args.target,
        "title": title,
        "code_file": notebook_path.name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": "true",
        "enable_gpu": enable_gpu,
        "enable_tpu": enable_tpu,
        "enable_internet": "true",
        "dataset_sources": args.dataset,
        "competition_sources": [],
        "kernel_sources": [],
        "model_sources": []
    }

    if args.dry_run:
        print("--- DRY RUN ---")
        print("Generated Metadata:")
        print(json.dumps(metadata, indent=2))
        print(f"Would push kernel and poll for up to {args.timeout} seconds.")
        print(f"Would download results to {args.output_dir}")
        return

    # 3. Create a temporary staging directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Copy notebook to tmpdir
        shutil.copy2(notebook_path, tmp_path / notebook_path.name)
        
        # Write metadata
        with open(tmp_path / "kernel-metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Pushing kernel '{args.target}' to Kaggle...")
        # 4. Push Kernel
        run_command(["kaggle", "kernels", "push", "-p", str(tmp_path)])
        
    print("Push successful. Polling status...")
    
    # 5. Poll Status
    start_time = time.time()
    poll_interval = 10
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > args.timeout:
            print(f"Error: Kernel run timed out after {args.timeout} seconds.")
            sys.exit(1)

        # e.g., 'Kernel user/slug has status "running"' or just check stdout
        status_output = run_command(["kaggle", "kernels", "status", args.target])
        status_lower = status_output.lower()
        
        if "complete" in status_lower:
            print("Kernel run COMPLETE.")
            break
        elif "error" in status_lower or "failed" in status_lower:
            print(f"Error: Kernel run failed. Status output: {status_output.strip()}")
            sys.exit(1)
        elif "running" in status_lower:
            print("Status: running...")
        elif "queued" in status_lower:
            print("Status: queued...")
        else:
            print(f"Status output: {status_output.strip()}")
            
        time.sleep(poll_interval)
        # Sane backoff, max 30s
        poll_interval = min(poll_interval + 5, 30)

    # 6. Download Outputs
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading outputs to {out_path.resolve()}...")
    run_command(["kaggle", "kernels", "output", args.target, "-p", str(out_path)])
    print("Done! 🎉")

if __name__ == "__main__":
    main()
