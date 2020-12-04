# <div align="left"><img src="img/rapids_bbo.png" width="160px"/>&nbsp;NVIDIA RAPIDS.AI Solution of BBO NeurIPS 2020</div>
We won **the 2nd place of the NeurIPS 2020 competition: Find the best black-box optimizer for machine learning.** [Leaderboard](https://bbochallenge.com/leaderboard)🎉 
We proposed a simple ensemble algorithm of black-box optimizers that outperforms any single optimizer but within the same timing budget. 
Evaluation of optimizers is a computing-intensive and time consuming task since the number of test cases grow exponentially with models, datasets and metrics. In our case, we need to **evaluate 15 optimizers, execute 4,230 jobs, train 2.7 million models and run 541,440 optimizations (suggest-observe)**. Utilizing the [RAPIDS](rapids.ai) libraries [cuDF](https://github.com/rapidsai/cudf) and [cuML](https://github.com/rapidsai/cuml), our GPU Accelerated exhaustive search is capable of finding the best ensemble in reasonable time. On a DGX-1, the search time is **reduced from more than 10 days on two 20-core CPUs to less than 24 hours on 8-GPUs.**

### Introduction


### Final Submission
Our final submission is an ensemble of optimizer [TuRBO](https://github.com/uber-research/TuRBO) and [scikit-optimize](https://scikit-optimize.github.io/stable/). [Code](https://github.com/daxiongshu/rapids-ai-BBO-2nd-place-solution/tree/master/example_submissions/turbosk) is in `example_submissions/turbosk`.

### Soltuion Overview

### Install Instructions
#### Create a conda Environment
- conda create -n bbo_rapids python=3.7
- conda activate bbo_rapids
#### Install cudf, cuml and pytorch
- conda install "pytorch=1.6" "cudf=0.16" "cuml=0.16" cudatoolkit=10.2.89 -c pytorch -c rapidsai -c nvidia -c conda-forge -c defaults
#### Install optimization algorithms
- pip install gpytorch==1.2.1
- pip install git+https://github.com/uber-research/TuRBO.git@master
- pip install pySOT==0.2.3 opentuner==0.8.2 nevergrad==0.1.4 hyperopt==0.1.1 scikit-optimize==0.5.2 scikit-learn==0.20.2 xgboost==1.2.1
#### Install rapids-enabled bayesmark
- git clone https://github.com/daxiongshu/bayesmark
- cd bayesmark
- git checkout rapids
- ./build_wheel.sh
- python setup.py install
