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
# Install PyTorch with appropriate CUDA support
echo "🔥 Installing PyTorch..."
if [ "$GPU_AVAILABLE" = "true" ]; then
    echo "   Installing PyTorch with CUDA support..."
else
    echo "   Installing PyTorch CPU version..."
fi
