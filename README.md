# 🚀 Auto creator : Monorepo  🎥

Welcome to the  Auto creator  monorepo! This project aims to automate the creation of videos using various tools and technologies. 🌟

## 📋 Prerequisites

Before getting started, make sure you have the following prerequisites installed:

- [Miniconda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh) 🐍
- [FFmpeg](https://ffmpeg.org/) 🎬
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) 💻

## 🛠️ Setup

Follow these steps to set up the project:

1. Download and install Miniconda:
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   sha256sum Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   source ~/.bashrc
   ```

2. Create a new conda environment and activate it:
   ```bash
   conda create -n joyvasa python=3.10 -y
   conda activate joyvasa
   ```

3. Clone the JoyVASA repository:
   ```bash
   git clone https://github.com/jdh-algo/JoyVASA.git
   ```

4. Install the necessary dependencies:
   ```bash
   sudo apt install build-essential
   sudo apt-get update
   sudo apt-get install ffmpeg -y
   sudo apt install nvidia-cuda-toolkit
   ```

5. Build and install the XPose dependencies:
   ```bash
   cd src/utils/dependencies/XPose/models/UniPose/ops
   python setup.py build install
   cd
   ```

6. Download the pretrained weights:
   ```bash
   huggingface-cli download KwaiVGI/LivePortrait --local-dir pretrained_weights --exclude "*.git*" "README.md" "docs"
   cd pretrained_weights
   ```

7. Install Git LFS and clone additional repositories:
   ```bash
   git lfs install
   git clone https://huggingface.co/jdh-algo/JoyVASA
   git clone https://huggingface.co/TencentGameMate/chinese-hubert-base
   git clone https://huggingface.co/facebook/wav2vec2-base-960h
   ```

## 🏃‍♂️ Running the FastAPI Application

/yt-api-python

To run the FastAPI application (`app.py`), follow these steps:

1. Install the required dependencies:
   ```bash
   pip install --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2 fastapi python-multipart uvicorn
   ```

2. Run the FastAPI application:
   ```bash
   python app.py
   ```

3. Access the application in your web browser at `http://localhost:3001`.

4. To authenticate and grant permissions for uploading videos to YouTube:
   - Visit `http://localhost:3001/auth` and follow the authentication flow.
   - After successful authentication, you will be redirected to the upload page.

5. To upload a video:
   - Go to `http://localhost:3001/upload`.
   - Fill in the video details (title, description, tags, privacy status).
   - Select a video file to upload.
   - Click the "Upload" button to start the upload process.

6. To retrieve information about your YouTube channel:
   - Make a GET request to `http://localhost:3001/channel-info`.
   - The response will contain details about your channel.

That's it! You're now ready to use the JoyVASA monorepo and explore its features. Happy auto-creating! 🎉

If you encounter any issues or have questions, feel free to reach out to the project maintainers. 📧

```
Note: The above instructions assume a Linux-based environment. Adjust the commands accordingly for other operating systems.
```

🌟 Enjoy! 🚀