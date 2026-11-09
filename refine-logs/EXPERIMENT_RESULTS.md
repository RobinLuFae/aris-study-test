# Baseline results (interim)

2026-11-07. R001 completed8000 optimizer updates in1219.68s, peak allocated2858.74MiB. Exact author WITT components, CIFAR-10/AWGN/C32, CBR1/3, fixed45k/5k training-partition split, seed42. Source/protocol differences remain in EXPERIMENT_PLAN.md. This is a functional and finite-budget local reproduction. The original Figure3(a) curve is visibly higher and local training still improves; numerical replication is incomplete. Do not digitize approximate paper graph values into exact benchmark rows.

## R001 validation

| Physical SNR(dB) | PSNR from aggregate MSE(dB) | Mean per-image PSNR(dB) |
|---|---|---|
|1|26.0371|26.2289|
|7|30.8019|31.0152|
|13|34.3450|34.7035|

Each point uses all5000 validation images and one fixed noise realization. Validation-selected adaptive checkpoint is at global8000. Results and sample preview: results/R001_validation.json/.png. Training curve: results/R001_training_curve.png. No official test-set metrics have been computed.

## Baseline conditioning diagnostic

The separated-condition adapter exactly matches the author's forward at matched SNR under identical noise: maximum absolute reconstruction difference0.0. Three noise repeats per case, first1000 fixed validation indices; all supplied SNR values within1..13dB. The physical AWGN SNR is unchanged; both encoder and decoder receive the same erroneous condition. This is not a feedback-protocol or satellite-channel simulation.

| Physical SNR(dB) | Supplied SNR error−3dB | Matched | Supplied SNR error+3dB |
|---|---|---|---|
|4|27.9463|28.5733|28.1758|
|7|30.4735|30.8835|30.7327|
|10|32.6772|32.8732|32.8294|

Values are aggregate-MSE PSNR(dB) averaged across the three noise repeats, not independent training-seed results. The pessimistic condition causes a larger drop than the optimistic condition in these cases. This is a local measured signal for further hypotheses, not an established general law. Raw27 records and index list: results/R001_conditioning_diagnostic.json.

## Checkpoint continuation verification

Continuous22 updates versus R00020+resumed2: state_dict,Adam,validation,sampler order/offset/epoch/RNG,CPU/CUDA/Python RNG and counters are exactly equal; maximum parameter absolute difference0.0. Evidence: logs/resume-equivalence.json. The test covers a fixed-SNR single-stage path on this machine; code review also checked stage-boundary logic. It does not establish cross-hardware bitwise reproducibility.

R002 continues R001 from its final checkpoint with the same Adam and random state, in a bounded segment. No new method or improvement result yet.

## 2026-11-08 reviewed continuation and stronger-checkpoint validation

R003continuedR002withsameAdam/RNG,pausedat22645totalupdates. Besteligiblecheckpoint21500verifiedagainst41historicaleligiblechecks,meanselectionMSE0.00096685555;validationPSNR1/7/13=27.09074/31.84668/35.33237dB. Original-paper numericalparity/convergenceremainsunestablished.

P001post-trainingtablescompleted7variants,13conditions,3pairednoise,1000val. Correctedtruefull-gridworstlinear3loss0.093756dBat4;theearlier0.080834isacommon8pointsubset.13primarysaves29.72%,maxpilotloss0.000258dB. Independentresearch-reviewverifiedrawmetrics andstates;refinementselected13primarybeforefollow-upevaluation. No accelerationclaim.

P002uses21500stepcheckpoint,1000val,32fixedSNRs,3noise,original/5/13.13saves29.7213778%ofwholefile,maxsignedloss0.00045356dBat2.25,roundtrip0,engineeringgatePASS. P003usesall5000val,8SNRs,3noise,original/13;maxsignedloss0.00026418dBat2.375,gatePASS. Per-method/per-repeatbatcherrors/counts andconditionalpointwisepairedbootstraprecords retained. See rawresults and analyses with correspondingP002/P003names.

P004 completed after both validation gates passed and the protocol was frozen. Same checkpoint, original/13, eight predeclared conditions, 10000 official test images, three new paired noises (seed base 91001). Maximum signed PSNR loss is 0.000186487920257 dB at 2.375 dB; maximum absolute change is 0.000337846133154 dB at 1.5 dB. Whole-file storage reduction is 29.7213778%. Raw results: results/P004_R003_final_test.json; analysis: results/P004_R003_analysis.json. Final integrity audit PASS. Claims remain bounded to one CIFAR/AWGN/CBR1/3 training trajectory. User requested stopping this week; no further experiments or writing started.
