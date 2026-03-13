# Milestone 2 summary

## Mismatch retraining

Validation AUROC: 0.8166  
Test AUROC: 0.8114

Interpretation:
Retraining the AV-sync branch on the explicit mismatch target produced strong ranking performance, and the learned score direction aligned with the positive class without requiring post hoc inversion.

## Video-authenticity retraining

Validation AUROC: 0.7516  
Test AUROC: 0.7509

Interpretation:
The AV-sync branch showed ranking signal on video authenticity, but threshold-dependent behaviour remained problematic because the aligned subset was highly imbalanced.

## Overall conclusion

The main outcome of Milestone 2 is that the AV-sync branch can now be interpreted using explicit task-aligned labels rather than inherited authenticity labels. The strongest result is on the mismatch proxy task.