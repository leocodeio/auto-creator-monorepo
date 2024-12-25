monorepo for auto-creator

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

sha256sum Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
conda create -n joyvasa python=3.10 -y
git clone https://github.com/jdh-algo/JoyVASA.git
conda activate joyvasa

sudo apt install build-essential
sudo apt-get update  
sudo apt-get install ffmpeg -y

sudo apt install nvidia-cuda-toolkit
 
cd src/utils/dependencies/XPose/models/UniPose/ops
python setup.py build install
cd

huggingface-cli download KwaiVGI/LivePortrait --local-dir pretrained_weights --exclude "*.git*" "README.md" "docs"
cd pretrained_weights

git lfs install
git clone https://huggingface.co/jdh-algo/JoyVASA
git clone https://huggingface.co/TencentGameMate/chinese-hubert-base
git clone https://huggingface.co/facebook/wav2vec2-base-960h

```