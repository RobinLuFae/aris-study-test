# Frozen gate-deployment experiment plan

2026-11-08;research-review→refinementREADY9.1(course scope). Problem Anchor and full thesis:FINAL_PROPOSAL.md. Baseline plan archived asEXPERIMENT_PLAN_baseline_20261107.md.

Claims:C1actualwhole-state storage reduction>=25%,4150272gateparametersremoved,nongatetensorsretained,roundtrip0. C2measured signed pooledPSNR loss<=0.1dB on declaredCIFAR/AWGN/CBR1/3conditions. No universalbounds,newtabulationtheory,semantic-taskaccuracyoraccelerationclaim.

Run order:
1.R003resumesR002withsameAdam/RNG/batch128/4threads,20minsegment,todayhardstop11:01:19China. Select inheritedeligiblebest by minimum meanMSE at1/7/13dB on scheduled500step/stage-final checks,tieskeepprior;cutoff-onlychecks excluded. Recordactualcheckpointstep,do notpresumeR003wins.
2.P002/E1:preparefrozendeployments from selectedcheckpoint;original/linear5/linear13,1000fixedvalidationimages,32SNRs,3pairednoise repetitions. Grid=configs/P002_R003_dense_validation.json:half-dB1..13plus1.75,2.25,2.375,3.375,5.25,8.25,11.25. Preservepermethod/perrepeat/perbatchsumofperimageMSEandimagecount.
3.P003/E2:original/main13,all5000validationimages,8SNRs{1,1.5,2.375,3,7,12,12.5,13},3pairednoises. Protocol=configs/P003_R003_full_validation.json.5integerknots,3interpolationpoints;batch128/final8fixed acrossmethods/repeats.
4.Admission:bothvalidationjobscomplete;13tableactualfilesaves>=25%,roundtrip0,maxsignedloss<=0.1overeverypointinbothgrids.5tabledoesnotcontroladmission. Onlythenfreezeactualcheckpoint/artifacts,8testSNRs,dataorder,batchmembership,noisebase91001.
5.P004/E3:oncefrozen,original/main13onofficial10000testimages,same8SNRs,3pairednoises. Nochoice/tuningusingtest;preservefailures. Ifvalidationfails/budgetexpires,leave testunopenedandreportvalidation-only.

Statistics:retainbothmodels'perbatchMSEsums/counts andimagePSNRsums.2000bootstrapdraws(seedbase20261108),resamplebatchIDs jointlyacrossmethods/noises,weightbyimagecount,compute10log10(tableMSE/originalMSE). Pointwise95%descriptivepercentilesconditionedoncheckpoint/fixedbatches/noises,notcontinuous/simultaneousguarantees.3noisesarenottrainingseeds.E1overlapsE2,E2usedforcheckpointselection;bothvalidationonly.

Controls:P001alreadyhasoriginal/shared-SNRcompute/linear3/5/9/13/nearest5. Preserveallresults andcorrecttrue3tablemaximum0.093756dBat4.13primarychosenbeforeE1;5optionalablation. Sidedinterventionsonlyifclaimingamplification. Noadditionaltrainablecomponent/frontierprimitive/channel/datasetneeded.

EstimatedGPU:P0022–5min,P0032–6min,P0043–8min;estimatesnotmeasurements. SequentialGPU,partialrecords/source snapshots,deadlineenforced. Freshcode reviewbeforepairedentry. Formalresult-to-claim,experiment/citationaudits andauto-review-loopprecedefinalpaper. Originalpaper numericalparity/convergence remainsunestablished;reportfinite-budget localreproduction honestly.
