# Skim

Skim ROOT TTree ntuples

Install code:

```
git clone https://github.com/GhentAnalysis/Skim
```

Get list of samples:

```
cd Skim
./createList.py --input=/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21 --copy='TTGamma'
```

Samples containing the key words specified with the --copy option
(comma-separated) will be
copied without skimming. Only the removal of the branches will be
done. You can manually modify the list of samples after it is created.

Process samples with no event skimming applied with 10 files per condor job:

```
./postproc.py --proxy=/user/kskovpen/proxy/x509up_u20657 --filter=all --list=list.txt --split=10 --input=/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21 --output=/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21_PP
```

Process samples with applying 1-lepton filter with 10 files per condor job:

```
./postproc.py --proxy=/user/kskovpen/proxy/x509up_u20657 --filter=1lep --list=list.txt --split=10 --input=/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21 --output=/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21_PP
```
