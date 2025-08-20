let eventSource

document.addEventListener('DOMContentLoaded', function () {
  eventSource = null
  loadHistory()

  // Adicionar event listeners aos botões e inputs
  const sendButton = document.getElementById('send-button')
  if (sendButton) {
    sendButton.addEventListener('click', sendQuestion)
  }

  const questionInput = document.getElementById('question-input')
  if (questionInput) {
    questionInput.addEventListener('keypress', handleKeyPress)
  }

  const learnUrlButton = document.getElementById('learn-url-button')
  if (learnUrlButton) {
    learnUrlButton.addEventListener('click', showLearnModal)
  }

  const learnDirButton = document.getElementById('learn-dir-button')
  if (learnDirButton) {
    learnDirButton.addEventListener('click', showDirModal)
  }

  const trainModelButton = document.getElementById('train-model-button')
  if (trainModelButton) {
    trainModelButton.addEventListener('click', trainModel)
  }

  const listConceptsButton = document.getElementById('list-concepts-button')
  if (listConceptsButton) {
    listConceptsButton.addEventListener('click', listarConceitos)
  }

  const learnUrlSubmit = document.getElementById('learn-url-submit')
  if (learnUrlSubmit) {
    learnUrlSubmit.addEventListener('click', learnFromUrl)
  }

  const learnDirSubmit = document.getElementById('learn-dir-submit')
  if (learnDirSubmit) {
    learnDirSubmit.addEventListener('click', learnFromDirectory)
  }
})

function handleKeyPress(event) {
  if (event.key === 'Enter') {
    sendQuestion()
  }
}

function sendQuestion() {
  const input = document.getElementById('question-input')
  const question = input.value.trim()

  if (!question) return

  addMessage(question, 'user')
  input.value = ''
  showTypingIndicator()
  sendQuestionWithStreaming(question)
}

function addMessage(content, type) {
  const messagesArea = document.getElementById('messages-area')
  const messageDiv = document.createElement('div')
  messageDiv.className = `message ${type}-message`

  // Formatação simples de markdown
  const formattedContent = formatMarkdown(content)
  messageDiv.innerHTML = formattedContent

  messagesArea.appendChild(messageDiv)

  // Aplicar syntax highlighting
  messageDiv.querySelectorAll('pre code').forEach((block) => {
    Prism.highlightElement(block)
  })

  messagesArea.scrollTop = messagesArea.scrollHeight
}

function formatMarkdown(text) {
  // Escape HTML básico
  const escapeHtml = (unsafe) => {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
  }

  // Detectar blocos de código com melhor preservação de indentação
  const codeBlockRegex = /```(\w+)?\s*\n?([\s\S]*?)```/g
  let formattedText = text

  // Processar blocos de código preservando indentação
  formattedText = formattedText.replace(
    codeBlockRegex,
    (match, language, code) => {
      const lang = language || 'text'
      // Preservar indentação original
      const preservedCode = code.replace(/^\n+|\n+$/g, '') // Remove quebras extras no início/fim
      const escapedCode = escapeHtml(preservedCode)

      // Gerar ID único para o bloco de código
      const codeId = 'code-' + Math.random().toString(36).substr(2, 9)

      return `
                <div class="code-block-container">
                    <div class="code-header">
                        <span class="code-language">${lang}</span>
                        <button class="copy-btn" onclick="copyCode('${codeId}')" title="Copiar código">
                            📋 Copiar
                        </button>
                    </div>
                    <pre><code id="${codeId}" class="language-${lang}">${escapedCode}</code></pre>
                </div>`
    }
  )

  // Código inline
  formattedText = formattedText.replace(
    /`([^`\n]+)`/g,
    '<code class="inline-code">$1</code>'
  )

  // Negrito
  formattedText = formattedText.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong>$1</strong>'
  )

  // Itálico
  formattedText = formattedText.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  // Quebras de linha
  formattedText = formattedText.replace(/\n/g, '<br>')

  return formattedText
}

// Função para copiar código
function copyCode(codeId) {
  const codeElement = document.getElementById(codeId)
  const text = codeElement.textContent

  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Feedback visual
      const copyBtn = codeElement
        .closest('.code-block-container')
        .querySelector('.copy-btn')
      const originalText = copyBtn.innerHTML
      copyBtn.innerHTML = '✅ Copiado!'
      copyBtn.style.background = '#4CAF50'

      setTimeout(() => {
        copyBtn.innerHTML = originalText
        copyBtn.style.background = ''
      }, 2000)
    })
    .catch((err) => {
      console.error('Erro ao copiar:', err)
      alert('Erro ao copiar código')
    })
}

function showTypingIndicator() {
  const indicator = document.getElementById('typing-indicator')
  indicator.innerHTML = 'Agente Maestro está analisando e gerando código...'
  indicator.classList.add('show')
  clearTimeout(indicator.timeout)
  indicator.timeout = setTimeout(hideTypingIndicator, 3000); // Aumentando o tempo para 3000ms para melhor visualização
}

function updateTypingIndicator(message) {
  const indicator = document.getElementById('typing-indicator')
  if (indicator.classList.contains('show')) {
    indicator.innerHTML = `🤖 ${message}`
  }
}

function hideTypingIndicator() {
  document.getElementById('typing-indicator').classList.remove('show')
}

function showDirModal() {
  new bootstrap.Modal(document.getElementById('dirModal')).show()
}

function showLearnModal() {
  new bootstrap.Modal(document.getElementById('learnModal')).show()
}

function showListarConceitosModal() {
  new bootstrap.Modal(document.getElementById('listarConceitosModal')).show()
}

function listarConceitos() {
  fetch('/api/listar_conceitos', {
    method: 'GET',
  })
    .then((response) => response.json())
    .then((data) => {
      addMessage(`📝 ${data.mensagem}`, 'bot')
      const conceitosList = document.getElementById('conceitos-list')
      conceitosList.innerHTML = ''

      if (data.conceitos && data.conceitos.length > 0) {
        data.conceitos.forEach((conceito) => {
          const percentMatch = conceito.match(/\((\d+\.?\d*)% do total\)/)
          const percent = percentMatch ? parseFloat(percentMatch[1]) : 0

          const listItem = document.createElement('li')
          listItem.style.marginBottom = '12px'
          listItem.style.padding = '8px'
          listItem.style.borderBottom = '1px solid #333'
          listItem.style.listStyle = 'none'

          listItem.innerHTML = `
                            <div style="margin-bottom: 6px; font-weight: 500;">${conceito}</div>
                            <div style="background-color: #333; border-radius: 10px; height: 8px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, #4CAF50, #45a049); height: 100%; width: ${percent}%; transition: width 0.3s ease;"></div>
                            </div>
                        `

          conceitosList.appendChild(listItem)
        })
        showListarConceitosModal()
      } else {
        const listItem = document.createElement('li')
        listItem.textContent = 'Nenhum conceito encontrado.'
        listItem.style.fontStyle = 'italic'
        listItem.style.color = '#888'
        conceitosList.appendChild(listItem)
        showListarConceitosModal()
      }
    })
    .catch((error) => {
      addMessage('Erro ao listar conceitos. Tente novamente.', 'bot')
      console.error('Erro:', error)
    })
}

async function learnFromDirectory() {
  try {
    const diretorio = prompt(
      'Digite o caminho completo do diretório para aprender:'
    )

    if (!diretorio || diretorio.trim() === '') {
      addMessage('❌ Caminho do diretório não fornecido.', 'bot')
      bootstrap.Modal.getInstance(document.getElementById('dirModal')).hide()
      return
    }

    fetch('/api/aprender_com_diretorio', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `diretorio=${encodeURIComponent(diretorio.trim())}`,
    })
      .then((res) => res.json())
      .then((data) => {
        addMessage(`📂 ${data.mensagem}`, 'bot')
        bootstrap.Modal.getInstance(document.getElementById('dirModal')).hide()
      })
      .catch((err) => {
        console.error('Erro:', err)
        addMessage('Erro ao aprender com a pasta.', 'bot')
        bootstrap.Modal.getInstance(document.getElementById('dirModal')).hide()
      })
  } catch (err) {
    console.log('Erro:', err)
    bootstrap.Modal.getInstance(document.getElementById('dirModal')).hide()
  }
}

function sendQuestionWithStreaming(question) {
  if (eventSource) {
    eventSource.close()
  }

  eventSource = new EventSource(
    `/api/perguntar_stream?pergunta=${encodeURIComponent(question)}`
  )
  let responseDiv = null
  let isFirstChunk = true

  eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data)

    if (data.type === 'start') {
      hideTypingIndicator()
      responseDiv = document.createElement('div')
      responseDiv.className = 'message bot-message'
      responseDiv.setAttribute('data-raw-content', '')
      document.getElementById('messages-area').appendChild(responseDiv)
    } else if (data.type === 'chunk' && responseDiv) {
      const currentContent = responseDiv.getAttribute('data-raw-content') || ''
      const newContent = currentContent + data.content
      responseDiv.setAttribute('data-raw-content', newContent)

      // Aplicar formatação em tempo real preservando indentação
      const formattedContent = formatMarkdownStreaming(newContent)
      responseDiv.innerHTML = formattedContent

      // Aplicar syntax highlighting nos blocos completos
      responseDiv.querySelectorAll('pre code').forEach((block) => {
        if (!block.classList.contains('highlighted')) {
          Prism.highlightElement(block)
          block.classList.add('highlighted')
        }
      })

      document.getElementById('messages-area').scrollTop =
        document.getElementById('messages-area').scrollHeight
    } else if (data.type === 'end') {
      if (responseDiv) {
        const finalContent = responseDiv.getAttribute('data-raw-content') || ''
        const formattedContent = formatMarkdown(finalContent)
        responseDiv.innerHTML = formattedContent

        // Aplicar syntax highlighting final
        responseDiv.querySelectorAll('pre code').forEach((block) => {
          Prism.highlightElement(block)
        })
      }

      eventSource.close()
      eventSource = null
      loadHistory()
    }
  }

  eventSource.onerror = function (event) {
    hideTypingIndicator()
    addMessage('Erro ao processar a pergunta. Tente novamente.', 'bot')
    eventSource.close()
    eventSource = null
  }
}

// Nova função para formatação durante streaming
function formatMarkdownStreaming(text) {
  const escapeHtml = (unsafe) => {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
  }

  // Detectar blocos de código completos e incompletos
  const completeCodeBlockRegex = /```(\w+)?\s*\n?([\s\S]*?)```/g
  const incompleteCodeBlockRegex = /```(\w+)?\s*\n?([\s\S]*)$/

  let formattedText = text

  // Processar blocos de código completos
  formattedText = formattedText.replace(
    completeCodeBlockRegex,
    (match, language, code) => {
      const lang = language || 'text'
      const preservedCode = code.replace(/^\n+|\n+$/g, '')
      const escapedCode = escapeHtml(preservedCode)
      const codeId = 'code-' + Math.random().toString(36).substr(2, 9)

      return `
                <div class="code-block-container">
                    <div class="code-header">
                        <span class="code-language">${lang}</span>
                        <button class="copy-btn" onclick="copyCode('${codeId}')" title="Copiar código">
                            📋 Copiar
                        </button>
                    </div>
                    <pre><code id="${codeId}" class="language-${lang}">${escapedCode}</code></pre>
                </div>`
    }
  )

  // Processar bloco de código incompleto (ainda sendo digitado)
  const incompleteMatch = formattedText.match(incompleteCodeBlockRegex)
  if (
    incompleteMatch &&
    !formattedText.includes('```', incompleteMatch.index + 3)
  ) {
    const [fullMatch, language, code] = incompleteMatch
    const lang = language || 'text'
    const escapedCode = escapeHtml(code)

    formattedText = formattedText.replace(
      incompleteCodeBlockRegex,
      `<div class="code-block-container streaming">
                        <div class="code-header">
                            <span class="code-language">${lang}</span>
                            <span class="streaming-indicator">✍️ Digitando...</span>
                        </div>
                        <pre><code class="language-${lang}">${escapedCode}</code></pre>
                    </div>`
    )
  }

  // Código inline
  formattedText = formattedText.replace(
    /`([^`\n]+)`/g,
    '<code class="inline-code">$1</code>'
  )

  // Negrito
  formattedText = formattedText.replace(
    /\*\*([^*]+)\*\*/g,
    '<strong>$1</strong>'
  )

  // Itálico
  formattedText = formattedText.replace(/\*([^*]+)\*/g, '<em>$1</em>')

  // Quebras de linha (preservar para código)
  formattedText = formattedText.replace(/\n/g, '<br>')

  return formattedText
}

function loadHistory() {
  fetch('/api/historico')
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById('history-container')
      container.innerHTML = ''

      if (data.historico && Array.isArray(data.historico)) {
        data.historico.forEach((item) => {
          const historyItem = document.createElement('div')
          historyItem.className = 'history-item'
          historyItem.onclick = () =>
            loadHistoryItem(item.pergunta, item.resposta)

          historyItem.innerHTML = `
                            <div class="history-question">${item.pergunta.substring(
                              0,
                              50
                            )}${item.pergunta.length > 50 ? '...' : ''}</div>
                            <div class="history-time">${new Date(
                              item.timestamp
                            ).toLocaleString()}</div>
                        `

          container.appendChild(historyItem)
        })
      } else {
        container.innerHTML = '<p>Nenhum histórico encontrado.</p>'
      }
    })
    .catch((error) => console.error('Erro ao carregar histórico:', error))
}

function loadHistoryItem(question, answer) {
  const messagesArea = document.getElementById('messages-area')
  messagesArea.innerHTML = ''
  addMessage(question, 'user')
  addMessage(answer, 'bot')
}

function learnFromUrl() {
  const url = document.getElementById('url-input').value.trim()
  if (!url) return

  fetch('/api/aprender_com_documentacao', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: `url=${encodeURIComponent(url)}`,
  })
    .then((response) => response.json())
    .then((data) => {
      addMessage(`📚 Aprendizado concluído: ${data.mensagem}`, 'bot')
      bootstrap.Modal.getInstance(document.getElementById('learnModal')).hide()
      document.getElementById('url-input').value = ''
    })
    .catch((error) => {
      addMessage('Erro ao aprender com a URL. Tente novamente.', 'bot')
      console.error('Erro:', error)
    })
}

function trainModel() {
  fetch('/api/treinar', {
    method: 'POST',
  })
    .then((response) => response.json())
    .then((data) => {
      addMessage(`🎯 ${data.mensagem}`, 'bot')
    })
    .catch((error) => {
      addMessage('Erro ao treinar o modelo. Tente novamente.', 'bot')
      console.error('Erro:', error)
    })
}
