## 📱 WhatsApp API Sender - Disparo em Massa

Sistema completo para envio de mensagens em massa via WhatsApp com suporte a **sequências personalizadas**, **upload de mídia** e **templates reutilizáveis**.

### 🆕 **Novas Funcionalidades**

#### **🔄 Sequências de Mensagens**
- Configure múltiplas mensagens para serem enviadas em ordem para cada contato
- Suporte a textos e mídias na mesma sequência  
- Intervalos randômicos ultra-humanizados entre mensagens
- Sistema de fadiga que simula comportamento humano real

#### **📤 Upload de Mídia Integrado**
- **Upload direto** de arquivos pela interface web
- **Preview em tempo real** de imagens, vídeos e áudios
- **Drag & Drop** - arraste e solte arquivos
- **Validação automática** de tipos de arquivo
- **Compressão inteligente** para otimizar envios
- **Fallback para caminhos** - compatibilidade total

#### **📚 Sistema de Templates**
- **Salve sequências** como templates reutilizáveis
- **Templates predefinidos** (Promocional, Informativo, Storytelling)
- **Templates personalizados** criados pelo usuário
- **Carregamento rápido** com um clique

#### **🎭 Simulação Humana Avançada**
- **3 perfis de comportamento**: Conservador, Normal, Agressivo
- **Intervalos inteligentes**: 
  - Entre mensagens: 1s-2min (com variações)
  - Entre contatos: 3s-5min (com pausas especiais)
- **Fadiga da sessão**: Intervalos aumentam com o tempo
- **Pausas contextuais**: Horários de refeição detectados
- **Micro-variações**: Inconsistência humana simulada

### 🚀 **Como Usar as Novas Funcionalidades**

#### **1. Configurar Sequência com Upload**
1. Acesse **"Mensagens"** → **"Configurar Sequência"**
2. Clique em **"Adicionar Mensagem"**
3. Para mídia:
   - Selecione **"Upload"** como método
   - Arraste seu arquivo ou clique para selecionar
   - Preview automático será exibido
   - Adicione legenda se desejar
4. Configure intervalos e nome padrão
5. **Salve a sequência**

#### **2. Salvar como Template**
1. Configure sua sequência perfeita
2. Clique em **"Salvar"** no painel de Templates
3. Digite um nome descritivo
4. O template fica disponível para reutilização

#### **3. Usar Templates Salvos**
1. No painel de Templates, veja seus templates personalizados
2. Clique no ícone ▶️ para carregar
3. Template é carregado instantaneamente
4. Personalize se necessário

### 📋 **Estrutura Simplificada da Planilha**

A planilha agora é **mais simples** - apenas 2 colunas:

| Nome | Numero |
|------|---------|
| João Silva | 5511999998888 |
| Maria Santos | 5511999997777 |

**As mensagens e mídias são configuradas pela interface**, não mais na planilha!

### 🎨 **Interface Moderna**

#### **Dark Mode Elegante**
- Tons grafite com gradientes sutis
- Contraste perfeito para uso prolongado
- Alternância rápida com botão de tema

#### **Componentes Interativos**
- **Upload area com drag & drop**
- **Preview de mídia em tempo real**
- **Progress bars animadas**
- **Notificações contextuais**
- **Modais elegantes**

### ⚙️ **Tipos de Mídia Suportados**

| Tipo | Formatos | Tamanho Máx |
|------|----------|-------------|
| **Imagens** | JPG, PNG, GIF, WebP | 16MB |
| **Vídeos** | MP4, AVI, MOV, MKV | 16MB |
| **Áudios** | MP3, WAV, OGG, AAC | 16MB |
| **Documentos** | PDF, DOC, XLS, TXT | 16MB |

### 🔧 **APIs Suportadas**

- **WAHA** (WhatsApp HTTP API)
- **Chat-API**
- **Z-API** 
- **UltraMsg**
- **WPPConnect**
- **Baileys**
- E muitas outras compatíveis com HTTP POST

### 📱 **Acesso Rápido**

**Interface Web:** http://127.0.0.1:5000

**Scripts de Inicialização:**
- **Windows:** `start_web.bat`
- **Linux/macOS:** `./start_web.sh`
- **Manual:** `python3 restart.py`

### 🎯 **Exemplo de Sequência Completa**

1. **Texto:** "Olá {nome}! 👋 Como você está?"
2. **Imagem:** Foto do produto (upload)
3. **Texto:** "Temos uma oferta especial para você! 🎉"  
4. **Vídeo:** Demonstração do produto (upload)
5. **Texto:** "Interessado? Responda este WhatsApp!"

**Intervalos:** 8-15s entre mensagens, 25-45s entre contatos
**Comportamento:** Simulação humana com pausas inteligentes

### 🔒 **Segurança e Privacidade**

- **Arquivos locais**: Todos os uploads ficam na pasta `uploads/media/`
- **Templates locais**: Salvos em `templates_saved/`
- **Sem nuvem**: Nenhum dado é enviado para serviços externos
- **Validação rigorosa**: Tipos de arquivo checados automaticamente

### 📈 **Logs Detalhados**

O sistema registra:
- ✅ **Uploads realizados** com timestamp
- 🎭 **Perfil de comportamento** usado
- ⏱️ **Duração das sessões**
- 📊 **Taxa de sucesso** por sequência
- 🤔 **Pausas especiais** (distração, refeição, etc.)

---

**🎉 Pronto para criar campanhas profissionais com a máxima humanização!** 