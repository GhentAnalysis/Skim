#!/bin/env python

import os, sys, ROOT

def countLeptons(ev, pt = 5.):

    nele, nmu, ntau = (0 for _ in range(3))
    
    for il in range(ev._nL):
        
        if ev._lPt[il] < pt: continue
        
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

fout = ROOT.TFile(sys.argv[2], 'RECREATE')

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
        
        nele, nmu, ntau = countLeptons(ev, pt = 5.)
        nlep = nele+nmu+ntau
        
        if filt in ['1lep'] and nlep < 1: continue
        elif filt in ['2lep'] and nlep < 2: continue
        elif filt in ['3lep'] and nlep < 3: continue
    
        tr.GetEntry(iev)
        trout.Fill()
    
fout.Write()
fout.Close()
f.Close()
