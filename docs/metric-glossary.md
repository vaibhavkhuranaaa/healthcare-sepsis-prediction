# Metric glossary

## Brier score

Mean squared difference between a predicted probability and the synthetic binary outcome. Lower is better. The constant baseline predicts training prevalence for every held-out row.

## Expected calibration error

Weighted average gap between mean predicted probability and synthetic outcome frequency across ten probability bins. Lower is better. Finite synthetic samples make this descriptive evidence only.

## Alert rate

Share of held-out synthetic rows at or above an illustrative threshold. It communicates review burden, not a recommended clinical alert policy.

## AUROC and AUPRC

Ranking summaries over held-out synthetic rows. Higher is better, but neither proves calibrated probabilities, clinical utility, or safe use.
