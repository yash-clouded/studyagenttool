# quiz_agent.py
import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Use absolute import for the utils module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.google_llm import create_google_llm

QUIZ_PROMPT = """You are a quiz generator.
Given the following text chunk, produce between 1 and 5 multiple-choice questions and return them as a valid JSON array.

Requirements:
- Output must be a valid JSON array of objects.
- Each object must have four keys: "question", "options", "answer", and "difficulty".
- The "options" key must be an array of 4 strings.
- The "answer" key must be one of the strings from the "options" array.
- The "difficulty" must be a string: "Easy", "Medium", or "Hard".
- Do NOT include any explanatory text, markdown, or code fences — output only the JSON array.
- If no suitable quiz can be produced, return an empty array: []
- Escape any quotes or special characters so the JSON is valid.

Example output:
[
    {{
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris",
        "difficulty": "Easy"
    }}
]

Text to use for generating the quiz:

{chunk}


Return strictly a JSON array.
"""

class QuizAgent:
    def __init__(self, llm=None):
        if llm is None:
            self.llm = create_google_llm()
            self.chain = None
        else:
            self.llm = llm
            prompt = PromptTemplate.from_template(QUIZ_PROMPT)
            self.chain = prompt | self.llm

    def _response_to_text(self, resp):
        if resp is None:
            return ""
        if isinstance(resp, str):
            return resp
        if isinstance(resp, dict):
            for k in ("text", "output_text", "response", "result"):
                if k in resp and isinstance(resp[k], str):
                    return resp[k]
            for v in resp.values():
                if isinstance(v, str):
                    return v
            try:
                return json.dumps(resp)
            except Exception:
                return str(resp)
        return str(resp)

    def generate_from_chunks(self, chunks):
        print("***QuizAgent generating from chunks...")
        out = []
        for c in chunks:
            print(f"***QuizAgent processing chunk...")
            try:
                if self.chain is None:
                    resp = self.llm.predict(QUIZ_PROMPT.replace("{chunk}", c))
                else:
                    result = self.chain.invoke({"chunk": c})
                    resp = result.content if hasattr(result, 'content') else str(result)
            except Exception as e:
                print(f"***QuizAgent exception during prediction/invocation: {e}")
                resp = ""
            
            text = self._response_to_text(resp)
            print(f"***QuizAgent processed text: {text}")

            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    for q in parsed:
                        if isinstance(q, dict):
                            q['source_chunk'] = c
                    out.extend(parsed)
                    continue
            except Exception:
                pass

            m = re.search(r'(\[.*\])', text, re.S)
            print(f"***QuizAgent regex search match: {m}")
            if m:
                try:
                    parsed = json.loads(m.group(1))
                    if isinstance(parsed, list):
                        for q in parsed:
                            if isinstance(q, dict):
                                q['source_chunk'] = c
                        out.extend(parsed)
                        continue
                except Exception:
                    pass

        return out
