# Set up the environment for running the training

- You need to run the following commands by yourself on terminal

## set global pip proxy and hf endpoint miior

```bash
mkdir -p ~/.pip && echo -e '[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\ntrusted-host = pypi.tuna.tsinghua.edu.cn' >> ~/.pip/pip.conf

echo -e 'export HF_ENDPOINT="https://hf-mirror.com"' >> ~/.bashrc && source ~/.bashrc
```

## install uv

```bash
pip install uv
uv venv
source .venv/bin/activate
export UV_HTTP_TIMEOUT=300
```
## install libs

**DO NOT** use the following way to install flash attention since it is too slow in China  

```bash
uv pip install flash-attn --no-build-isolation
```

 Instead, we can use the precompiled wheel file flash_attn-2.7.4.post1+cu12torch2.2cxx11abiFALSE-cp310-cp310-linux_x86_64.whl from [Github](https://github.com/Dao-AILab/flash-attention/releases) which contains key info as follows. Download corresponding file for your environment.

 ```text
       cu12：CUDA 12.x
       torch2.2：PyTorch 2.2
       cp310：Python 3.10 
       FALSE: PyTorch C++ ABI status
              you can check it by 
              import torch; print(torch._C._GLIBCXX_USE_CXX11_ABI)
```

Then run the following command:

```bash
uv pip install libs/flash_attn-2.7.4.post1+cu12torch2.4cxx11abiFALSE-cp311-cp311-linux_x86_64.whl
```

Finally, install the libs specified in the requirements file

```bash
uv pip install -r requirements.txt 
```
