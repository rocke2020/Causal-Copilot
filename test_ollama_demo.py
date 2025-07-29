#!/usr/bin/env python3
"""
Test script to verify Ollama configuration for the demo.
This script tests different Ollama models with the demo configuration.
"""

import os
import sys
from llm import LLMClient

def test_ollama_models():
    """Test different Ollama models with the demo configuration."""
    
    # Test models
    models_to_test = ['llama2', 'llama3.2']
    
    for model in models_to_test:
        print(f"\n{'='*50}")
        print(f"Testing model: {model}")
        print(f"{'='*50}")
        
        # Set environment variables
        os.environ['LLM_PROVIDER'] = 'ollama'
        os.environ['LLM_MODEL'] = model
        
        try:
            # Create a simple args-like object
            class Args:
                def __init__(self):
                    self.llm_provider = os.environ.get('LLM_PROVIDER', 'ollama')
                    self.model_name = os.environ.get('LLM_MODEL', 'llama2')
                    self.api_key = None
            
            args = Args()
            
            # Test LLMClient
            client = LLMClient(args)
            
            # Simple test prompt
            test_prompt = "Hello! Please respond with 'Hello from [model_name]' where [model_name] is your model name."
            
            print(f"Testing with prompt: {test_prompt}")
            
            # Test chat completion
            response = client.chat_completion(
                prompt=test_prompt,
                system_prompt="You are a helpful assistant.",
                temperature=0.1
            )
            
            print(f"✅ Success! Response: {response}")
            
        except Exception as e:
            print(f"❌ Error with {model}: {str(e)}")
            print(f"Make sure {model} is available: ollama list")
    
    print(f"\n{'='*50}")
    print("Test completed!")
    print(f"{'='*50}")

if __name__ == "__main__":
    test_ollama_models() 