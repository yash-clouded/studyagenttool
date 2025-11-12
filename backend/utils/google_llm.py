import os
import google.generativeai as genai
from langchain_core.language_models import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from typing import Optional, List, Any

class GoogleLLM(LLM):
    """
    Wrapper around Google Generative AI (Gemini) to be compatible with LangChain.
    """
    
    model: str = "gemini-2.5-flash"
    temperature: float = 0.1
    top_p: float = 0.95
    top_k: int = 64
    max_output_tokens: int = 8192

    def __init__(self, api_key, **kwargs):
        super().__init__(**kwargs)
        if not api_key:
            raise ValueError("Google API key is required.")
        genai.configure(api_key=api_key)

    @property
    def _llm_type(self) -> str:
        return "google_generative_ai"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            generation_config = {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "max_output_tokens": self.max_output_tokens,
            }
            
            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config
            )
            response = model.generate_content(prompt)
            return response.text if response.text else ""
                
        except Exception as e:
            raise RuntimeError(f"Google Gemini API error: {str(e)}")

    def predict(self, prompt: str) -> str:
        return self._call(prompt)

def create_google_llm(
    api_key: str,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.1,
    **kwargs
) -> GoogleLLM:
    return GoogleLLM(api_key=api_key, model=model, temperature=temperature, **kwargs)
