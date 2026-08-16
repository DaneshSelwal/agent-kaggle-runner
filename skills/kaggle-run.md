---
name: kaggle-run
description: Runs a Jupyter Notebook on Kaggle using the local kaggle_runner/run.py script. Use this to execute computationally heavy machine learning workloads on Kaggle's free GPUs or TPUs.
---

# Kaggle Run Capability

This skill allows you to run Jupyter notebooks on Kaggle's cloud environment, providing access to free GPUs/TPUs and fast internet.

## When to use this skill
- The user hands you a Jupyter notebook and asks you to "run it on Kaggle".
- The task requires GPU or TPU compute that is not available locally.
- The task requires processing Kaggle datasets directly without downloading them locally.

## Instructions
1. **Gather Inputs**:
   - Ask the user for the path to the Jupyter Notebook (`--notebook`).
   - Ask the user for any Kaggle dataset slugs that need to be attached (e.g. `username/dataset`).
   - Ask the user for their preferred target kernel slug (e.g. `username/my-kernel-name`). If not provided, derive it from the notebook name.
   - Ask if they have a preference for the hardware accelerator (`auto`, `gpu`, `tpu`, `cpu`). If not provided, default to `auto`.

2. **Invoke the Runner**:
   - Use `run_command` to execute the Python runner script located at `kaggle_runner/run.py`.
   - Example invocation:
     ```bash
     python kaggle_runner/run.py \
       --notebook path/to/notebook.ipynb \
       --target username/my-kernel-name \
       --dataset username/some-dataset \
       --accelerator auto \
       --output-dir ./results
     ```

3. **Monitor and Handle Errors**:
   - The script will automatically push the notebook, poll for completion, and download outputs.
   - If the script fails, read the output.
     - "Missing auth": Tell the user to set up their `~/.kaggle/kaggle.json` or `KAGGLE_API_TOKEN`.
     - "Dataset not found": Verify the dataset slug provided by the user.
     - "Kernel run error": The code inside the notebook threw an error. The user may need to debug the notebook code.

4. **Report Results**:
   - Once the script completes successfully, check the `--output-dir` (default: `./results`) for the downloaded files.
   - Inform the user that the run is complete and summarize the output files.
