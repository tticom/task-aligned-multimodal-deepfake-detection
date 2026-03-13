# Milestone 3 summary: complementarity ablations

## Aim

This milestone tested whether synchronisation-aware evidence adds value beyond the corrected visual baseline, and whether that value depends on task definition.

Two tasks were evaluated:

- mismatch proxy
- video authenticity

Three ablation modes were compared on each task:

- visual_only
- sync_only
- visual_sync

## Headline findings

### Mismatch

Test AUROC:
- visual_only: 0.1349
- sync_only: 0.8114
- visual_sync: 0.8154

Test F1 at threshold 0.5:
- visual_only: 0.0000
- sync_only: 0.7031
- visual_sync: 0.7052

Interpretation:
- synchronisation-aware evidence carries the mismatch signal
- the corrected visual score is not useful for mismatch and appears directionally misaligned
- adding visual score to sync provides only a marginal gain

### Video authenticity

Test AUROC:
- visual_only: 0.6721
- sync_only: 0.7509
- visual_sync: 0.8969

Test F1 at threshold 0.5:
- visual_only: 0.9909
- sync_only: 0.9838
- visual_sync: 0.9911

Test FPR at threshold 0.5:
- visual_only: 0.4902
- sync_only: 0.9804
- visual_sync: 0.4706

Interpretation:
- visual+sync provides a strong ranking improvement over either unimodal score
- however, threshold-0.5 behaviour remains problematic because the task is highly imbalanced
- ranking performance and operating-point behaviour must therefore be reported separately

## Overall conclusion

The ablation results support the dissertation’s core methodological claim that multimodal value is task-dependent.

- On mismatch, synchronisation is the primary informative signal.
- On video authenticity, combining visual and synchronisation evidence materially improves ranking.
- Strong multimodal performance should therefore not be treated as task-invariant.

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_mismatch_sync_only_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.7085998578535891
val_fpr: 0.19471153846153846
val_auroc: 0.8166358873460766
test_f1: 0.7030520646319569
test_fpr: 0.19326241134751773
test_auroc: 0.8114333529939244

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_mismatch_visual_only_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.0
val_fpr: 0.0
val_auroc: 0.12185350546138393
test_f1: 0.0
test_fpr: 0.0
test_auroc: 0.13491241446444072

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_mismatch_visual_sync_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.7243703440936502
val_fpr: 0.18329326923076922
val_auroc: 0.8212032755422742
test_f1: 0.7052480230050323
test_fpr: 0.19030732860520094
test_auroc: 0.815380256610674

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_videoauth_sync_only_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.9853768278965129
val_fpr: 1.0
val_auroc: 0.751577727058653
test_f1: 0.9838063171396505
test_fpr: 0.9803921568627451
test_auroc: 0.7508641123441883

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_videoauth_visual_only_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.9919015225137674
val_fpr: 0.5
val_auroc: 0.6668441836032315
test_f1: 0.9909414428987383
test_fpr: 0.49019607843137253
test_auroc: 0.6721053035094781

==========================================================================================
results_preds_v2/ablation_v1/metrics/metrics_ablation_videoauth_visual_sync_thr05.json
selected_threshold: 0.5
infeasible: None
val_f1: 0.9915748541801686
val_fpr: 0.5
val_auroc: 0.8996268521537514
test_f1: 0.9910988833144522
test_fpr: 0.47058823529411764
test_auroc: 0.8968783342597385

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_sync_only_f1.json
selected_threshold: 0.3273617808841551
infeasible: None
val_f1: 0.7366504854368932
val_fpr: 0.35396634615384615
val_auroc: 0.8166358873460766
test_f1: 0.7271039603960396
test_fpr: 0.3416075650118203
test_auroc: 0.8114333529939244

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_sync_only_fpr01.json
selected_threshold: 0.8917953991921537
infeasible: False
val_f1: 0.33902036323610346
val_fpr: 0.009615384615384616
val_auroc: 0.8166358873460766
test_f1: 0.358500814774579
test_fpr: 0.018912529550827423
test_auroc: 0.8114333529939244

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_only_f1.json
selected_threshold: 0.45498676531531435
infeasible: None
val_f1: 0.6479913137893594
val_fpr: 0.9735576923076923
val_auroc: 0.12185350546138393
test_f1: 0.6420182688125272
test_fpr: 0.9710401891252955
test_auroc: 0.13491241446444072

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_only_fpr01.json
selected_threshold: None
infeasible: True
reason: No validation threshold achieved target FPR with non-zero recall.
val_metrics: None
test_metrics: None

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_sync_f1.json
selected_threshold: 0.3523695044669239
infeasible: None
val_f1: 0.7368421052631579
val_fpr: 0.3215144230769231
val_auroc: 0.8212032755422742
test_f1: 0.720967228762329
test_fpr: 0.31382978723404253
test_auroc: 0.815380256610674

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_mismatch_visual_sync_fpr01.json
selected_threshold: 0.8667016492719339
infeasible: False
val_f1: 0.4273058884835852
val_fpr: 0.009615384615384616
val_auroc: 0.8212032755422742
test_f1: 0.43020833333333336
test_fpr: 0.016548463356973995
test_auroc: 0.815380256610674

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_sync_only_f1.json
selected_threshold: 0.7575960769726877
infeasible: None
val_f1: 0.9856890175269336
val_fpr: 0.9666666666666667
val_auroc: 0.751577727058653
test_f1: 0.9836433611289288
test_fpr: 0.9803921568627451
test_auroc: 0.7508641123441883

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_sync_only_fpr01.json
selected_threshold: 0.9849799127726712
infeasible: False
val_f1: 0.16786140979689368
val_fpr: 0.0
val_auroc: 0.751577727058653
test_f1: 0.15004519433564326
test_fpr: 0.00980392156862745
test_auroc: 0.7508641123441883

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_only_f1.json
selected_threshold: 0.25196707547125996
infeasible: None
val_f1: 0.9923935911959864
val_fpr: 0.5111111111111111
val_auroc: 0.6668441836032315
test_f1: 0.9912734324499031
test_fpr: 0.5098039215686274
test_auroc: 0.6721053035094781

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_only_fpr01.json
selected_threshold: None
infeasible: True
reason: No validation threshold achieved target FPR with non-zero recall.
val_metrics: None
test_metrics: None

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_sync_f1.json
selected_threshold: 0.25571431776076536
infeasible: None
val_f1: 0.9920699142256029
val_fpr: 0.5222222222222223
val_auroc: 0.8996268521537514
test_f1: 0.9919146183699871
test_fpr: 0.47058823529411764
test_auroc: 0.8968783342597385

==========================================================================================
results_preds_v2/ablation_v1/metrics/threshold_sweep_ablation_videoauth_visual_sync_fpr01.json
selected_threshold: 0.9936877775947502
infeasible: False
val_f1: 0.19800235017626322
val_fpr: 0.0
val_auroc: 0.8996268521537514
test_f1: 0.18127962085308058
test_fpr: 0.00980392156862745
test_auroc: 0.8968783342597385