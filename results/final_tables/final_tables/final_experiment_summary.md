# Final experiment summary

| group | task | mode | test AUROC | test F1@0.5 | test FPR@0.5 | FPR<=0.01 infeasible |
|---|---|---|---:|---:|---:|---|
| milestone2_avsync | mismatch | sync_only | 0.8114333529939244 | 0.7004341534008683 | 0.18735224586288415 | False |
| milestone2_avsync | videoauth | sync_only | 0.7508641123441883 | 0.983969220904136 | 0.9803921568627451 | False |
| milestone3_ablation | mismatch | visual_only | 0.13491241446444072 | 0.0 | 0.0 | True |
| milestone3_ablation | mismatch | sync_only | 0.8114333529939244 | 0.7030520646319569 | 0.19326241134751773 | False |
| milestone3_ablation | mismatch | visual_sync | 0.815380256610674 | 0.7052480230050323 | 0.19030732860520094 | False |
| milestone3_ablation | videoauth | visual_only | 0.6721053035094781 | 0.9909414428987383 | 0.49019607843137253 | True |
| milestone3_ablation | videoauth | sync_only | 0.7508641123441883 | 0.9838063171396505 | 0.9803921568627451 | False |
| milestone3_ablation | videoauth | visual_sync | 0.8968783342597385 | 0.9910988833144522 | 0.47058823529411764 | False |
