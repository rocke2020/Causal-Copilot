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

# Function to install system packages on macOS
install_macos_deps() {
    echo "🍎 Installing macOS dependencies..."
    
    # Check for Homebrew
    if command_exists brew; then
        echo "✅ Homebrew found"
        
        # Install Graphviz
        if ! command_exists dot; then
            echo "📦 Installing Graphviz..."
            brew install graphviz
        else
            echo "✅ Graphviz already installed"
        fi
        
        # Install LaTeX (BasicTeX - lightweight)
        if ! command_exists pdflatex; then
            echo "📄 Installing BasicTeX..."
            brew install --cask basictex
            echo "⚠️  Please restart your terminal after installation completes"
            echo "⚠️  Then add to PATH: export PATH=\"\$PATH:/Library/TeX/texbin\""
        else
            echo "✅ LaTeX already installed"
        fi
    else
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
}

# Function to install system packages on Linux
install_linux_deps() {
    echo "🐧 Installing Linux dependencies..."
    
    # Detect Linux distribution
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
    else
        echo "❌ Cannot detect Linux distribution"
        exit 1
    fi
    
    case $OS in
        *"Ubuntu"*|*"Debian"*)
            echo "🔵 Detected Ubuntu/Debian"
            sudo apt-get update
            
            # Install Graphviz
            if ! command_exists dot; then
                echo "📦 Installing Graphviz..."
                sudo apt-get install -y graphviz graphviz-dev
            fi
            
            # Install LaTeX
            if ! command_exists pdflatex; then
                echo "📄 Installing TeX Live..."
                sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended
            fi
            
            # Install CUDA development tools if GPU detected
            if check_gpu >/dev/null 2>&1; then
                echo "🔧 Installing CUDA development tools..."
                sudo apt-get install -y cuda-toolkit-dev || echo "⚠️  CUDA toolkit installation failed - continuing anyway"
            fi
            ;;
        *"CentOS"*|*"Red Hat"*|*"Amazon Linux"*)
            echo "🔴 Detected CentOS/RHEL/Amazon Linux"
            
            # Install Graphviz
            if ! command_exists dot; then
                echo "📦 Installing Graphviz..."
                if command_exists dnf; then
                    sudo dnf install -y graphviz graphviz-devel
                else
                    sudo yum install -y graphviz graphviz-devel
                fi
            fi
            
            # Install LaTeX
            if ! command_exists pdflatex; then
                echo "📄 Installing TeX Live..."
                if command_exists dnf; then
                    sudo dnf install -y texlive-latex texlive-latex-extra
                else
                    sudo yum install -y texlive-latex texlive-latex-extra
                fi
            fi
            ;;
        *)
            echo "⚠️  Unsupported Linux distribution: $OS"
            echo "   Please install graphviz and texlive manually"
            ;;
    esac
}

# Detect operating system and install system dependencies
echo "🔧 Installing system dependencies..."
case "$(uname -s)" in
    Darwin*)
        install_macos_deps
        ;;
    Linux*)
        install_linux_deps
        ;;
    *)
        echo "❌ Unsupported operating system: $(uname -s)"
        echo "   Please install graphviz and LaTeX manually"
        ;;
esac

echo ""
