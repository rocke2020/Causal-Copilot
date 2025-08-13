#!/bin/bash
echo "🚀 Causality-Copilot GPU Setup Script"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check GPU availability
check_gpu() {
    if command_exists nvidia-smi; then
        echo "🎮 NVIDIA GPU detected:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
        return 0
    else
        echo "⚠️  No NVIDIA GPU detected or nvidia-smi not found"
        echo "   Installing CPU versions of GPU packages..."
        return 1
    fi
}

echo "🎮 Checking GPU availability..."
check_gpu
if [ $? -eq 0 ]; then
    GPU_AVAILABLE="true"
else
    GPU_AVAILABLE="false"
fi
echo "GPU available: $GPU_AVAILABLE"

echo ""
echo "🐍 Installing Python packages..."
echo "================================"

# Install the base packages
echo "📦 Installing base requirements..."
pip install -r requirements_gpu.txt --no-deps --no-cache-dir

Install PyTorch with appropriate CUDA support
echo "🔥 Installing PyTorch..."

if [ "$GPU_AVAILABLE" = "true" ]; then
    echo "   Installing PyTorch with CUDA support..."
    pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128

else
    echo "   Installing PyTorch CPU version..."
    pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cpu

fi

# Install the rest of the packages gradio needs  
echo "🌐 Installing Gradio..."
pip install gradio

# Install LaTeX-related Python packages
echo "📄 Installing LaTeX integration packages..."
pip install -r requirements_latex.txt


# Install GPU-specific packages if available
if [ "$GPU_AVAILABLE" = "true" ]; then
    echo "🎮 Installing GPU-accelerated packages..."
    pip install cupy-cuda12x fastrlock 2>/dev/null || echo "⚠️  Some GPU packages may not be available"
    
    # Try to install GPU-accelerated causal discovery packages
    pip install culingam gpucsl 2>/dev/null || echo "⚠️  GPU-accelerated causal discovery packages not available"
fi

# Update LaTeX package manager and install essential packages
if command_exists tlmgr; then
    echo "📚 Updating LaTeX packages..."
    tlmgr update --self
    echo "📦 Installing essential LaTeX packages..."
    tlmgr install fancyhdr geometry amsmath booktabs array longtable float caption hyperref url listings xcolor 2>/dev/null || echo "⚠️  Some LaTeX packages may already be installed"
else
    echo "⚠️  tlmgr not found - LaTeX packages will be installed on-demand"
fi

echo ""
echo "✅ Installation completed!"
echo "========================="

echo ""
echo "📄 Running LaTeX functionality test..."
python test_latex_functionality.py

# Test GPU functionality if available
if [ "$GPU_AVAILABLE" = "true" ]; then
    echo ""
    echo "🎮 Testing GPU functionality..."
    python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA devices: {torch.cuda.device_count()}')
    print(f'Current device: {torch.cuda.get_device_name()}')
else:
    print('No CUDA devices found')
"
fi

echo ""
echo "🎉 Setup complete! You can now run:"
echo "   python web_demo/demo.py"
if [ "$GPU_AVAILABLE" = "true" ]; then
    echo ""
    echo "🎮 GPU acceleration is available for supported algorithms!"
fi