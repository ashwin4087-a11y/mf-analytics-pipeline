# Sprint 3 Demo Script

**Visual:** Open terminal showing the workspace.
**Audio:** "Welcome to the Sprint 3 demonstration for the Nifty 100 Financial Intelligence Platform. In this sprint, we integrated the data and ratios from Sprints 1 and 2 into an advanced Screener and Peer Analytics Engine."

**Visual:** Open `config/screener_config.yaml` in the IDE.
**Audio:** "First, let's look at the screener configuration. We've defined six preset strategies dynamically in YAML. For instance, the 'Quality Compounder' targets companies with ROE above 15% and Debt-to-Equity below 1, among other criteria."

**Visual:** Run `python scripts/run_sprint3.py`. Show the console output printing execution steps.
**Audio:** "When we run the pipeline, the engine calculates a Composite Quality Score for all companies using sector-relative normalization. It then executes the presets and computes peer percentiles."

**Visual:** Open `output/screener_output.xlsx`. Tab through the sheets.
**Audio:** "The first output is the Screener Excel report. As you can see, we have six separate tabs—one for each preset. The companies are sorted by their Composite Quality Score."

**Visual:** Open `output/peer_comparison.xlsx`. Show a specific sector tab, e.g., 'IT'.
**Audio:** "Next is the Peer Comparison report. Companies are grouped by their peer segments. The metrics are displayed alongside their percentile ranks within that specific group. Notice the conditional formatting: green highlights the top quartile, and the benchmark company is marked in gold."

**Visual:** Open `reports/radar_charts/TCS_radar.png` (or another generated chart).
**Audio:** "Finally, the pipeline generates radar charts for all 100 benchmark and peer companies. The blue shaded area represents the individual company's performance across 8 dimensions, overlaid on the red dashed line representing the peer group average."

**Visual:** Show the `Sprint_3_Submission/` directory structure.
**Audio:** "All deliverables, including the source code, reports, and generated datasets, are neatly packaged in the Sprint 3 submission folder. The `peer_percentiles` database schema discrepancy has been logged and formally proposed for reconciliation. Thank you."
