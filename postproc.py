#!/bin/env python

import htcondor
import os, sys, glob, shutil
from optparse import OptionParser

def job(cdir, s, t, p, v, batch, fsh):
    
    j = "#!/bin/bash\n\n"
    
    j += "export X509_USER_PROXY="+options.proxy+"\n"

    j += "echo \"Start: $(/bin/date)\"\n"
    j += "echo \"User: $(/usr/bin/id)\"\n"
    j += "echo \"Node: $(/bin/hostname)\"\n"
    j += "echo \"CPUs: $(/bin/nproc)\"\n"
    j += "echo \"Directory: $(/bin/pwd)\"\n"
    
    j += "source /cvmfs/cms.cern.ch/cmsset_default.sh\n"
    
    j += "cd "+cdir+"\n"

    j += "export SCRAM_ARCH=slc6_amd64_gcc700\n"
    j += "eval `scramv1 runtime -sh`\n"

    for b in batch:
        
        fin = options.input+'/'+s+'/'+t+'/'+d+'/'+p+'/'+os.path.basename(b)
        fout = options.output+'/'+s+'/'+t+'/'+d+'/'+p+'/'+os.path.basename(b)
        
        if bool(v): j += "cp "+fin+" "+fout+"\n"
        else: j += "python applySkim.py "+fin+" "+fout+" "+options.filter+"\n"
        if options.clean: j += "rm -rf "+fin+"\n"

    with open(fsh, 'w') as f:
        f.write(j)

def main(argv = None):

    if argv == None:
        argv = sys.argv[1:]
    
    usage = "usage: %prog [options]\n Run postprocessing steps on alredy produced heavyNeutrino ntuples"
    
    parser = OptionParser(usage)
    
    parser.add_option("--list", type=str, default='list.txt', help="List with names of the samples [default: %default]")
    parser.add_option("--filter", type=str, default='all', help="Filter to apply (all, 1lep, 2lep, 3lep) [default: %default]")
    parser.add_option("--proxy", type=str, default='/user/kskovpen/proxy/x509up_u20657', help="Proxy location [default: %default]")
    parser.add_option("--split", type=int, default=10, help="Number of processed files per job [default: %default]")
    parser.add_option("--input", type=str, default='/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21', help="Input directory [default: %default]")
    parser.add_option("--output", type=str, default='/pnfs/iihe/cms/store/user/kskovpen/heavyNeutrinoMoriond21Skim', help="Output directory [default: %default]")
    parser.add_option("--clean", action='store_true', help="Remove all input files once the processing is done [default: %default]")
    
    (options, args) = parser.parse_args(sys.argv[1:])
    
    return options

def getFiles(dir, files):
    
    return [f for f in files if os.path.isfile(os.path.join(dir, f))]

if __name__ == '__main__':

    options = main()

    cdir = os.getcwd()
    
    samples = {}
    with open(options.list) as fr:
        for l in fr.readlines():
            if '#' in l: continue
            name = l.split(' ')[0]
            copy = int(l.split(' ')[1])
            samples[name] = copy

    if not os.path.isdir('jobs'): os.system('mkdir jobs')
    
    if not os.path.isdir(options.output): os.system('mkdir '+options.output)        

    for s, v in samples.iteritems():
        
        print s
        
        os.system('rm -rf '+options.output+'/'+s)
            
        shutil.copytree(options.input+'/'+s, options.output+'/'+s, ignore=getFiles)
          
        tags = [i.split('/')[-2] for i in glob.glob(options.input+'/'+s+'/*/')]
        for t in tags:
            dtime = [i.split('/')[-2] for i in glob.glob(options.input+'/'+s+'/'+t+'/*/')]
            for d in dtime:
                parts = [i.split('/')[-2] for i in glob.glob(options.input+'/'+s+'/'+t+'/'+d+'/*/')]
                for p in parts:
                    files = glob.glob(options.input+'/'+s+'/'+t+'/'+d+'/'+p+'/*.root')
                    
                    jobs = []
                    schedd = htcondor.Schedd()

                    batches = []
                    for f in range(0, len(files), options.split):
                        batches.append(files[f:f + options.split])
                    
                    for ib, b in enumerate(batches):

                        fout = ('jobs/'+s+'_'+t+'_'+p+'_'+os.path.basename(b[0])+'_'+str(ib)).replace('.root', '')
                        job(cdir, s, t, p, v, b, fout+'.sh')

                        js = htcondor.Submit({\
                        "executable": fout+'.sh', \
                        "output": fout+'.out', \
                        "error": fout+'.err', \
                        "log": fout+'.log' \
                        })
            
                        with schedd.transaction() as shd:
                            cluster_id = js.queue(shd)
                            jobs.append(cluster_id)
