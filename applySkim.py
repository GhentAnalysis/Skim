#!/bin/env python

import os, sys, ROOT

def countLeptons(ev):

    nele, nmu, ntau = (0 for _ in range(3))
    
    for il in range(ev._nL):
        
        if ev._lFlavor[il] == 0:
            
            if ev._lPtCorr[il] < 7: continue
            elif abs(ev._lEta[il]) > 2.5: continue
            elif abs(ev._dxy[il]) > 0.05: continue
            elif abs(ev._dz[il]) > 0.1: continue
            elif ev._3dIPSig[il] > 8: continue
            elif ev._lElectronMissingHits[il] >= 2: continue
            elif ev._miniIso[il] > 0.4: continue
            
        elif ev._lFlavor[il] == 1:
            
            if ev._lPt[il] < 5: continue
            elif abs(ev._lEta[il]) > 2.4: continue
            elif abs(ev._dxy[il]) > 0.05: continue
            elif abs(ev._dz[il]) > 0.1: continue
            elif ev._3dIPSig[il] > 8: continue
            elif ev._miniIso[il] > 0.4: continue
            elif not bool(ev._lPOGMedium[il]): continue
            
        elif ev._lFlavor[il] == 2:
            
            if not bool(ev._decayModeFindingDeepTau[il]): continue
        
        if ev._lFlavor[il] == 0: nele += 1
        elif ev._lFlavor[il] == 1: nmu += 1
        elif ev._lFlavor[il] == 2: ntau += 1
    
    return nele, nmu, ntau

filt = sys.argv[3]

if filt not in ['all', '1lep', '2lep', '3lep']:
    print 'Unknown skim requested:', filt
    sys.exit()

f = ROOT.TFile(sys.argv[1], 'READ')

tr = f.Get('blackJackAndHookers/blackJackAndHookersTree');

brRemove = ['_jetPt_*JECGrouped*', '_jetPt_*JECSources*']
histCopy = ['nVertices', 'hCounter', 'lheCounter', 'psCounter', 'tauCounter', 'nTrueInteractions']

fout = ROOT.TFile(sys.argv[2], 'RECREATE', '', ROOT.ROOT.CompressionSettings(ROOT.ROOT.kLZMA, 4))

for b in brRemove: tr.SetBranchStatus(b, 0)

fout.mkdir('blackJackAndHookers')
fout.cd('blackJackAndHookers')

for h in histCopy: 
    hw = f.Get('blackJackAndHookers/'+h).Clone()
    hw.Write()

if filt in ['all']: trout = tr.CloneTree(-1, 'fast')

else:
    
    trout = tr.CloneTree(0, 'fast')

    for iev, ev in enumerate(tr):
        
        nele, nmu, ntau = countLeptons(ev)
#        nlep = nele+nmu+ntau
        nlep = nele+nmu # filter on light leptons
        
        if filt in ['1lep'] and nlep < 1: continue
        elif filt in ['2lep'] and nlep < 2: continue
        elif filt in ['3lep'] and nlep < 3: continue
    
        tr.GetEntry(iev)
        trout.Fill()
    
fout.Write()
fout.Close()
f.Close()
