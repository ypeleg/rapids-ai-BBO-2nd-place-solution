import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
import sys
import os
import subprocess

from bayesmark.data import DATA_LOADERS, REAL_DATA_LOADERS
from bayesmark.constants import MODEL_NAMES
from time import sleep,time
import glob
from random import shuffle, randint
import numpy as np
from combine_experiments import combine
from utils import get_run_name, run_cmd, run_bayesmark_init, run_bayesmark_agg, run_bayesmark_anal

no_multi_class_cuml = ['RF-cuml', 'SVM-cuml', 'xgb-cuml']
multi_class_data = ['iris', 'digits', 'wine', 'mnist']
real_data = []
COUNTER = 0 

def run_all(opt, n_jobs=16, N_STEP=16, N_BATCH=8, N_REPEAT=1, 
            run_cuml=False, quick_check=False, data_loaders=DATA_LOADERS,
            model_names=MODEL_NAMES, must_have_tag=None):

    start = time()
    in_path = os.path.abspath('./input')
    out_path = os.path.abspath('./output')
    if 'RandomSearch' == opt:
        opt_root,opt = '.',opt
    elif 'RandomSearch' in opt:
        assert 0, "not supported yet"
        optx = opt.split()[-1]
        opt_root,opt = optx.split('/')[-2], optx.split('/')[-1]
        opt = 'RandomSearch '+opt
    else:
        optx = opt
        opt_root,opt = optx.split('/')[-2], optx.split('/')[-1]

    name = get_run_name()
    
    if os.path.exists(out_path) == 0:
        os.mkdir(out_path)
        
    if os.path.exists(f"{out_path}/{name}"):
        assert 0, f"{out_path}/{name} already exists"
                      
    run_bayesmark_init(out_path, name)
    
    tag = '-cuml-all' if run_cuml else ''
    baseline = f"{in_path}/baseline-{N_STEP}-{N_BATCH}{tag}.json"
    if os.path.exists(baseline)==False:
        assert 0, f"{baseline} doesn't exist"
   
    if 'RandomSearch' not in opt:
        cmd = f'cp {baseline} {out_path}/{name}/derived/baseline.json'
        run_cmd(cmd)
    else:
        if os.path.exists(baseline)==False:
            assert 0, f"{baseline} doesn't exist"

    cmds = [] 
    if quick_check: 
        data_loaders = {'boston': (2,2)}
        if run_cuml:
            model_names = ['xgb-cuml']#['MLP-sgd-cuml']
        else:
            model_names = ['xgb']#['MLP-adam']

    if run_cuml:
        model_names = [i for i in model_names if i.endswith('-cuml')]# and 'MLP' not in i and 'xgb' not in i]

    if must_have_tag is not None:
        if isinstance(must_have_tag, list):
            model_names = [i for i in model_names if isin(i, must_have_tag)]
        else:
            model_names = [i for i in model_names if must_have_tag in i]
    print(model_names)

    for data in data_loaders:
        metrics = ['nll', 'acc'] if data_loaders[data][1] == 1 else ['mse', 'mae']
        for metric in metrics:
            for model in model_names:
                for _ in range(N_REPEAT):
                    if run_cuml==False and '-cuml' in model:
                        continue
                    if run_cuml and model in no_multi_class_cuml and data in multi_class_data:
                        continue
                    if run_cuml and model == 'SVM-cuml' and data_loaders[data][1] == 1:
                        continue
                    cmd = f"bayesmark-launch -dir {out_path} -b {name} -n {N_STEP} -r 1 -p {N_BATCH} -o {opt} --opt-root {opt_root} -v -c {model} -d {data} -m {metric} -dr ./more_data&"
                    cmds.append(cmd)

    N = len(cmds)
    cmds = run_cmds(cmds, min(n_jobs, N))

    last = 0 
    while True:
        done, n = check_complete(N, out_path, name)
        sofar = time() - start    
        print(f"{sofar:.1f} seconds passed, {N - len(cmds)} tasks launched, {n} out of {N} tasks finished ...")
        if done:
            break
        sleep(3)
        if last < n:
            lc = len(cmds)
            cmds = run_cmds(cmds, min(n-last, lc))
        last = n
        
    run_bayesmark_agg(out_path, name)
    run_bayesmark_anal(out_path, name)
    
    duration = time() - start
    print(f"All done!! {name} Total time: {duration:.1f} seconds")
    return name, duration
    
def isin(i, must_have_tag):
    for j in must_have_tag:
        if j in i:
            return True
    return False

def run_cmds(cmds, n):
    global COUNTER
    for _ in range(n):
        cmd = cmds.pop()
        os.environ["CUDA_VISIBLE_DEVICES"] = str(COUNTER%8)
        COUNTER += 1
        run_cmd(cmd)
    return cmds

def check_complete(N, out_path, name):
    path = f"{out_path}/{name}/eval"
    if os.path.exists(path) == False:
        return False
    files = glob.glob(f"{path}/*.json")
    n = len(files)
    return n == N, n

if __name__ == '__main__':
    opt = './example_submissions/pysotopen'

    # sklearn dataset
    name1,t1 = run_all(opt, N_STEP=16, N_BATCH=8, N_REPEAT=3, quick_check=False, n_jobs=32, run_cuml=True)#, must_have_tag='xgb')

    # real dataset
    name2,t2 = run_all(opt, N_STEP=16, N_BATCH=8, N_REPEAT=3, quick_check=False, n_jobs=32, run_cuml=True,
            data_loaders=REAL_DATA_LOADERS, must_have_tag=['MLP', 'xgb'] 
            )
    print(name1, name2)
    combine([name1, name2])

    print(f"Total time: {t1+t2:.1f} seconds")
