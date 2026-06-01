# 🚀 Guia de Configuração OpenRouter

Este guia documenta a configuração **CORRETA** para usar o OpenClaw com OpenRouter.

## ✅ Configuração que FUNCIONA

### 1. Arquivo `.env`

```bash
# Gateway auth token
GATEWAY_AUTH_TOKEN=seu-token-seguro-aqui

# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-seu-token-aqui

# Modelo (IMPORTANTE: usar prefixo openrouter/)
DEFAULT_MODEL=openrouter/anthropic/claude-sonnet-4.5

# Porta do gateway
GATEWAY_PORT=18789

# Log level
LOG_LEVEL=info
```

### 2. Comandos para Iniciar

```bash
# Build e start
docker compose up -d

# Ver logs
docker compose logs -f

# Verificar status
docker compose ps
```

### 3. Acessar o Webchat

```
http://localhost:18789/chat?token=seu-gateway-auth-token
```

## 📝 Formato do Modelo - MUITO IMPORTANTE!

### ❌ Formatos INCORRETOS que NÃO funcionam:

```bash
# SEM o prefixo openrouter/
DEFAULT_MODEL=anthropic/claude-sonnet-4.5

# Com hífen ao invés de ponto
DEFAULT_MODEL=openrouter/anthropic/claude-sonnet-4-5
```

### ✅ Formato CORRETO:

```bash
DEFAULT_MODEL=openrouter/anthropic/claude-sonnet-4.5
```

**Padrão:** `openrouter/<provider>/<model>`

## 🎯 Modelos Disponíveis via OpenRouter

### Claude (Anthropic)
- `openrouter/anthropic/claude-opus-4-5` - Mais poderoso
- `openrouter/anthropic/claude-sonnet-4.5` - Melhor custo-benefício (recomendado)
- `openrouter/anthropic/claude-3.5-sonnet` - Versão anterior
- `openrouter/anthropic/claude-3.5-haiku` - Mais rápido

### GPT (OpenAI)
- `openrouter/openai/gpt-4o`
- `openrouter/openai/gpt-4-turbo`
- `openrouter/openai/o1-preview`

### Gemini (Google)
- `openrouter/google/gemini-2.0-flash-exp` - Gratuito!
- `openrouter/google/gemini-pro`

### Open Source (Gratuitos!)
- `openrouter/meta-llama/llama-3.3-70b-instruct` - Llama 3.3 70B
- `openrouter/deepseek/deepseek-r1` - DeepSeek R1

**Lista completa:** https://openrouter.ai/models

## 🔧 Troubleshooting

### Erro: "Unknown model: anthropic/claude-sonnet-4.5"

**Causa:** Falta o prefixo `openrouter/`

**Solução:**
```bash
# Errado
DEFAULT_MODEL=anthropic/claude-sonnet-4.5

# Correto
DEFAULT_MODEL=openrouter/anthropic/claude-sonnet-4.5
```

### Container não inicia

```bash
# Limpar tudo e rebuildar
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## 📊 Como Verificar se Está Funcionando

### 1. Verificar logs do container

```bash
docker compose logs --tail 50
```

Deve mostrar:
```
✓ OpenRouter configured — multi-model gateway active
✓ Model: openrouter/anthropic/claude-sonnet-4.5
✓ gateway: listening on ws://0.0.0.0:18789
```

### 2. Verificar variáveis de ambiente

```bash
docker exec openclaw sh -c "env | grep OPENROUTER"
```

### 3. Testar uma mensagem

Envie "olá" pelo webchat e verifique os logs:

```bash
docker compose logs --tail 20 --follow
```

## 📚 Documentação Oficial

- **OpenClaw:** https://docs.openclaw.ai
- **OpenRouter:** https://openrouter.ai/works-with-openrouter
- **Modelos:** https://openrouter.ai/models
- **API Keys:** https://openrouter.ai/settings/keys

## ⚙️ Configuração Avançada

### Trocar de modelo

1. Editar `.env`:
```bash
DEFAULT_MODEL=openrouter/google/gemini-2.0-flash-exp
```

2. Recriar container:
```bash
docker compose down -v && docker compose up -d
```

### Usar modelo gratuito

Modelos gratuitos no OpenRouter:
```bash
# Gemini 2.0 Flash
DEFAULT_MODEL=openrouter/google/gemini-2.0-flash-exp

# Llama 3.3 70B
DEFAULT_MODEL=openrouter/meta-llama/llama-3.3-70b-instruct

# DeepSeek R1
DEFAULT_MODEL=openrouter/deepseek/deepseek-r1
```

## 💰 Custos

### Claude Sonnet 4.5
- **Input:** $1.00 / 1M tokens
- **Output:** $5.00 / 1M tokens
- **Context:** 200K tokens

### Modelos Gratuitos
- Gemini 2.0 Flash
- Llama 3.3 70B
- DeepSeek R1

**Criar conta OpenRouter:** https://openrouter.ai/

## 🎉 Sucesso!

Se você vir nos logs:
```
message processed: outcome=completed duration=...ms
```

**Parabéns! 🎉 O OpenClaw está funcionando com OpenRouter!**
