# Kaggle Runner Plugin for AI Agents

This repository provides a remote-execution capability that allows AI coding agents (like Google Antigravity, Claude Code, Cursor, etc.) to automatically run Jupyter Notebooks on Kaggle's free GPU/TPU environments.

## What it does
When an agent is asked to "run this notebook on Kaggle," it can invoke this plugin to:
1. Parse the notebook to auto-detect if a GPU/TPU is needed based on imports (e.g., `import torch`).
2. Generate the necessary Kaggle `kernel-metadata.json`.
3. Push the notebook and any specified datasets to Kaggle.
4. Poll the Kaggle API for the kernel status.
5. Automatically download the results and outputs once the run is complete.

## Prerequisites
- Python 3
- The `kaggle` CLI (`pip install kaggle`)
- A valid Kaggle API Token. 

### Kaggle Token Setup
1. Go to your [Kaggle Account Settings](https://www.kaggle.com/settings).
2. Click **Create New Token**.
3. Download the `kaggle.json` file.
4. Move the file to `~/.kaggle/kaggle.json` (Mac/Linux) or `C:\Users\<Windows-username>\.kaggle\kaggle.json` (Windows).
5. On Mac/Linux, restrict permissions: `chmod 600 ~/.kaggle/kaggle.json`.
*(Alternatively, you can set the `KAGGLE_API_TOKEN` environment variable).*

## Installation for Antigravity (AGY)
You can install this plugin directly into your Antigravity environment:
```bash
agy plugin install <path-to-this-repo>
```

## Using this with other agents
The core logic is contained in a portable Python script (`kaggle_runner/run.py`). You can easily adapt this for other agents like Claude Code or Cursor.

### For Claude Code
1. Copy `kaggle_runner/run.py` to your project workspace.
2. Copy the `AGENTS.md` context file to your repository and rename it to `CLAUDE.md`.
3. Create a `.claude/skills/kaggle-run.md` (or equivalent) copying the instructions from `skills/kaggle-run.md`.

### Manual Usage
You can also use the script manually from your terminal:
```bash
python kaggle_runner/run.py \
  --notebook path/to/notebook.ipynb \
  --target your-username/kernel-slug \
  --dataset your-username/dataset-slug \
  --accelerator auto \
  --output-dir ./results
```

## Examples
Check the `examples/` directory for a dummy notebook (`dummy.ipynb`) that you can use to test the setup.
