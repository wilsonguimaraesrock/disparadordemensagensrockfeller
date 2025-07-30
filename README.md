# 🚀 Disparador de Mensagens em Lote WhatsApp - Sistema Completo

**Sistema profissional para envio automatizado de mensagens em massa via WhatsApp com suporte completo para mídia!**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Evolution API](https://img.shields.io/badge/Evolution%20API-Suportado-green.svg)](https://github.com/EvolutionAPI/evolution-api)
[![WAHA](https://img.shields.io/badge/WAHA-Suportado-orange.svg)](https://waha.devlike.pro/)

## ✨ **Novidades da Versão Atual**

- 🔥 **Sistema principal RECONSTRUÍDO** - interface melhorada e mais robusta
- 🎥 **Envio de mídia OTIMIZADO** - retry logic avançado para imagens/vídeos
- ⚡ **Setup automático** - configuração sem Docker incluída
- 🧪 **Testes automatizados** - verificação completa do sistema
- 📊 **Relatórios detalhados** - análise de performance em tempo real
- 🛠️ **Suporte híbrido** - funciona com ou sem Docker

---

## 🎯 **Características Principais**

### 💬 **Mensagens**
- ✅ Envio em massa de mensagens de texto
- ✅ Suporte completo para **imagens, vídeos, áudios e documentos**
- ✅ Validação inteligente de números de telefone
- ✅ Mensagens personalizadas por contato

### 🔧 **APIs Suportadas**
- ✅ **Evolution API** (Recomendada - Gratuita e completa)
- ✅ **WAHA** (Core gratuito + Plus pago)
- ✅ **Chat-API, Z-API, UltraMsg** (Compatibilidade)
- ✅ Sistema de **fallback automático**

### 📊 **Gerenciamento**
- ✅ Interface de linha de comando intuitiva
- ✅ Interface web para gerenciamento
- ✅ Importação via **Excel (.xlsx/.xls)**
- ✅ Logs detalhados com análise de performance
- ✅ Relatórios de sucesso/falha

### 🛡️ **Segurança e Estabilidade**
- ✅ Intervalos aleatórios entre envios
- ✅ Sistema de **retry automático** com backoff
- ✅ Timeouts adaptativos (30s → 60s → 120s)
- ✅ Validação de arquivos e formatos
- ✅ Controle de rate limiting

---

## 🚀 **Início Rápido (5 minutos)**

### 1. **Verificar Sistema**
```bash
python teste_sistema_completo.py
```

### 2. **Configurar Evolution API** (Recomendado)
```bash
# Opção A: Com Docker (se disponível)
docker-compose up -d

# Opção B: Sem Docker (Node.js necessário)
python setup_evolution_standalone.py --setup
python setup_evolution_standalone.py --start
```

### 3. **Criar Arquivo de Exemplo**
```bash
python criar_excel_exemplo.py
```

### 4. **Enviar Mensagens**
```bash
python enviar_mensagens_lote.py
```

**Pronto! Seu sistema está funcionando!** 🎉

---

## 📋 **Requisitos do Sistema**

### **Obrigatórios**
- 🐍 **Python 3.7+**
- 📦 **pip** (gerenciador de pacotes Python)
- 🌐 **Conexão com internet**

### **Para Evolution API (Escolha uma opção)**
- 🐳 **Docker + Docker Compose** (Opção mais fácil)
- 🟢 **Node.js 16+** (Instalação local)

### **Dependências Python** (Instaladas automaticamente)
```bash
pip install -r requirements.txt
```

---

## 🎯 **Guias de Configuração**

### **📱 Evolution API (Recomendada - Gratuita)**

<details>
<summary><b>🐳 Setup com Docker (Mais Fácil)</b></summary>

```bash
# 1. Iniciar containers
docker-compose up -d

# 2. Verificar se estão rodando
docker ps

# 3. Acessar interface web
# http://localhost:8081

# 4. Conectar WhatsApp via QR Code
```

</details>

<details>
<summary><b>🟢 Setup sem Docker (Node.js)</b></summary>

```bash
# 1. Verificar dependências
python setup_evolution_standalone.py --check

# 2. Setup completo
python setup_evolution_standalone.py --setup

# 3. Iniciar API
python setup_evolution_standalone.py --start

# 4. Em outro terminal, criar instância
python setup_evolution_standalone.py --create-instance
python setup_evolution_standalone.py --connect
```

</details>

### **📡 WAHA (Funciona, mas limitado)**

<details>
<summary><b>WAHA - Configuração e Limitações</b></summary>

```bash
# Versão Core (Gratuita) - Só texto
docker run -it --rm -p 3000:3000 devlikeapro/waha

# Versão Plus (Paga $19/mês) - Mídia completa
docker run -it --rm -p 3000:3000 devlikeapro/waha-plus

# Configurar no config.json:
{
  "provider": "waha",
  "base_url": "http://localhost:3000",
  "token": "seu-token-waha",
  "instance_id": "default"
}
```

**⚠️ LIMITAÇÃO:** WAHA Core não suporta envio de mídia (apenas texto)

</details>

---

## 📊 **Formato da Planilha Excel**

### **Estrutura Obrigatória**

| **numero** | **mensagem** | **nome** (opcional) | **caminho_midia** (opcional) |
|------------|--------------|---------------------|------------------------------|
| +5521999887766 | Olá! Como você está? | João Silva | imagens/foto.jpg |
| 5511988776655 | Mensagem sem mídia | Maria Santos | |
| +5531977665544 | Documento anexo | Pedro Costa | documentos/relatorio.pdf |

### **📝 Regras Importantes**
- ✅ **numero**: Com ou sem `+` (será normalizado automaticamente)
- ✅ **mensagem**: Texto da mensagem (obrigatório)
- ✅ **nome**: Nome do contato (opcional, usado nos logs)
- ✅ **caminho_midia**: Caminho do arquivo (opcional)

### **🎥 Formatos de Mídia Suportados**

| **Tipo** | **Formatos** | **Tamanho Máximo** |
|----------|--------------|-------------------|
| 🖼️ **Imagens** | JPG, PNG, GIF, WebP, SVG | 16 MB |
| 🎥 **Vídeos** | MP4, 3GP, MOV | 16 MB |
| 🎵 **Áudios** | MP3, AAC, OGG, M4A | 16 MB |
| 📄 **Documentos** | PDF, DOC, XLS, TXT, ZIP | 64 MB |

---

## 🚀 **Próximos Passos e Roadmap**

### **🎯 Para Começar Agora**

1. **Execute o teste completo:**
   ```bash
   python teste_sistema_completo.py
   ```

2. **Configure sua API preferida:**
   ```bash
   # Evolution API (Recomendada)
   python setup_evolution_standalone.py --setup
   
   # ou WAHA (se preferir)
   docker-compose up -d
   ```

3. **Crie arquivo de exemplo:**
   ```bash
   python criar_excel_exemplo.py
   ```

4. **Faça seu primeiro envio:**
   ```bash
   python enviar_mensagens_lote.py
   ```

---

## ⚖️ **Licença e Avisos Legais**

### **📝 Licença**
Este projeto está sob a **Licença MIT**. Veja [LICENSE](LICENSE) para detalhes.

### **⚠️ Avisos Importantes**

- ✅ **Use responsavelmente:** Respeite os termos do WhatsApp
- ✅ **Anti-spam:** Obtenha consentimento antes de enviar
- ✅ **Rate limiting:** O sistema já implementa intervalos seguros
- ✅ **Backup:** Sempre teste com poucos contatos primeiro

### **🛡️ Isenção de Responsabilidade**

Este software é fornecido "como está", sem garantias. Os desenvolvedores não se responsabilizam por:
- Bloqueios de conta WhatsApp
- Problemas com APIs de terceiros
- Perda de dados
- Uso inadequado do sistema

**Use com responsabilidade e sempre em conformidade com as leis locais e termos de serviço das plataformas.**

---

## 📞 **Contato e Suporte**

- 🐛 **Issues:** [GitHub Issues](https://github.com/wilsonguimaraesrock/disparadordemensagensrockfeller/issues)
- 📧 **Email:** suporte@exemplo.com
- 📚 **Documentação:** Arquivos `.md` neste repositório

---

<div align="center">

### ⭐ **Se este projeto te ajudou, deixe uma estrela!** ⭐

**Desenvolvido com ❤️ para facilitar a comunicação em massa via WhatsApp**

[![GitHub stars](https://img.shields.io/github/stars/wilsonguimaraesrock/disparadordemensagensrockfeller?style=social)](https://github.com/wilsonguimaraesrock/disparadordemensagensrockfeller/stargazers)

</div>