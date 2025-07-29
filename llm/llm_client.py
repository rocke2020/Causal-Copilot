import re
import json
from typing import Optional, Dict, Any, Union
from openai import OpenAI
from .ollama_client import OllamaClient

class LLMClient:
    def __init__(self, args):
        """
        Initialize the LLM client.
        
        Args:
            args: Configuration arguments containing:
                - llm_provider: "openai" or "ollama"
                - model_name: Name of the model to use
                - api_key: API key for OpenAI (if using OpenAI)
                - base_url: Base URL for Ollama (if using Ollama)
        """
        self.provider = getattr(args, 'llm_provider', 'openai')
        self.model = getattr(args, 'model_name', 'gpt-4o-mini' if self.provider == 'openai' else 'llama2')
        
        if self.provider == 'openai':
            self.client = OpenAI(api_key=getattr(args, 'api_key', None))
        elif self.provider == 'ollama':
            self.client = OllamaClient(
                model_name=self.model,
                base_url=getattr(args, 'base_url', 'http://localhost:11434')
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def chat_completion(self, 
                       prompt: str, 
                       system_prompt: str = "You are a helpful assistant.", 
                       json_response: bool = False, 
                       model: Optional[str] = None,
                       temperature: float = 0.0) -> Union[str, Dict]:
        """
        Send a chat completion request to the LLM.
        
        Args:
            prompt (str): The user prompt
            system_prompt (str): The system prompt
            json_response (bool): Whether to expect JSON response
            model (str, optional): Override the default model
            temperature (float): Temperature for response generation
            
        Returns:
            Union[str, Dict]: The model's response (string or JSON)
        """
        if self.provider == 'openai':
            messages = []
            if system_prompt is not None:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": model if model else self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if json_response:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            if json_response:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract JSON from the response
                    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    raise ValueError("Failed to parse JSON response from OpenAI")
            
            return content
            
        elif self.provider == 'ollama':
            return self.client.chat_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                json_response=json_response,
                temperature=temperature
            ) 