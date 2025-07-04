# Configuration Migration Guide

## Environment Variable Changes

### Variable Name Updates

- `OPENAI_DEFAULT_MODEL` → `OPENAI_MODEL`
- `ANTHROPIC_DEFAULT_MODEL` → `ANTHROPIC_MODEL`
- `MISTRAL_DEFAULT_MODEL` → `MISTRAL_MODEL`
- `GROQ_DEFAULT_MODEL` → `GROQ_MODEL`
- `HUGGINGFACE_DEFAULT_MODEL` → `HUGGINGFACE_MODEL`
- `OLLAMA_DEFAULT_MODEL` → `OLLAMA_MODEL`
- `GOOGLE_API_KEY` → `GOOGLE_AI_API_KEY`
- `GOOGLE_MODEL` → `GOOGLE_AI_MODEL`

### Recommended Model Updates

- `OPENAI_MODEL`: gpt-3.5-turbo → gpt-4-turbo-preview
- `GROQ_MODEL`: llama2-70b-4096 → mixtral-8x7b-32768
- `HUGGINGFACE_MODEL`: microsoft/DialoGPT-large → google/gemma-7b-it
- `OPENROUTER_MODEL`: anthropic/claude-3-opus → openai/gpt-3.5-turbo
