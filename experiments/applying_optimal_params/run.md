to run the experiments at once:

```bash
for f in experiments/applying_optimal_params/*_scale/*_facilities; do
  echo RUNNING $f
  python $f/optimize_network.py
  python $f/add_meta_results.py
done;
```

Do not forget to activate the venv first.