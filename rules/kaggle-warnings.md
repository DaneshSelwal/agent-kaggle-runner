# Kaggle Warnings

1. **Destructive Commands**: Never execute `kaggle` commands that overwrite or delete datasets/kernels without explicit user confirmation first.
2. **GPU Quota Consumption**: When preparing to run a notebook on Kaggle with `--accelerator gpu` or `--accelerator tpu`, always warn the user that this will consume their weekly Kaggle GPU/TPU quota (30 hours/week limit by default). Proceed only if they agree or if they've pre-approved it for the session.
