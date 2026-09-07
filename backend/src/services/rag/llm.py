import os
from typing import Iterator

from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from ollama import Client

from schemas.env_schema import settings


# -------------------------
# Client setup (all keys resolved the same way: settings -> env var)
# -------------------------
def safe_openai_client():
    key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if key is None or key.strip() == "":
        return None
    return OpenAI(api_key=key)


def safe_claude_client():
    key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
    if key is None or key.strip() == "":
        return None
    return Anthropic(api_key=key)


def safe_gemini_client():
    key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if key is None or key.strip() == "":
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-1.5-pro")

client_openai = safe_openai_client()
client_claude = safe_claude_client()
client_gemini = safe_gemini_client()

client = Client(settings.OLLAMA_HOST or os.getenv("OLLAMA_HOST"))

# Model + Ollama config in one place so you're not hunting through methods to update them
OPENAI_MODEL = "gpt-4o-mini"
CLAUDE_MODEL = "claude-sonnet-5"
REWRITE_MODEL = "qwen2.5:3b"
GENERATION_MODEL = "qwen3.6:27b"


class generationModel:
    """Handles prompt building and multi-provider streamed generation."""

    def build_prompt(self, query: str, context: str) -> str:
        return f"""You are a helpful assistant. Use ONLY the context below to answer the question.
            Context:
            {context}
            Question:
            {query}
            Answer:
        """

    def _query_rephrase_(self, query):
        return f"""Correct only the grammar and spelling of the question below.
            Do not answer the question. Do not add explanations, preamble, or quotation marks.
            If the question is already grammatically correct, return it unchanged.
            Question: {query}
            Corrected question:
        """

    def rephrase_query(self, query: str) -> str:
        query = self._query_rephrase_(query)
        res = client.chat(
            model=REWRITE_MODEL,
            messages=[{"role": "user", "content": query}],
            stream=False,
            keep_alive=0
        )
        return res["message"]["content"]

    # -------------------------
    # OpenAI
    # -------------------------
    def generate_openai(self, prompt: str) -> Iterator[str]:
        if client_openai is None:
            raise RuntimeError("OpenAI is not configured")
        
        stream = client_openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    # -------------------------
    # Claude
    # -------------------------
    def generate_claude(self, prompt: str) -> Iterator[str]:
        if client_claude is None:
            raise RuntimeError("Claude is not configured")
        
        # .stream()'s text_stream only yields text deltas, so it won't choke
        # on tool-use/thinking deltas the way manually filtering event.type did.
        with client_claude.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            yield from stream.text_stream

    # -------------------------
    # Gemini
    # -------------------------
    def generate_gemini(self, prompt: str) -> Iterator[str]:
        if client_gemini is None:
            raise RuntimeError("Gemini is not configured")
        
        response = client_gemini.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    # -------------------------
    # Ollama (local)
    # -------------------------
    def generate_ollama(self, prompt: str) -> Iterator[str]:
        stream = client.chat(
            model=GENERATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in stream:
            yield chunk["message"]["content"]

        # unload by making a follow-up call with keep_alive=0 —
        # there is no standalone ollama.unload()
        client.chat(model=GENERATION_MODEL, messages=[], keep_alive=0)