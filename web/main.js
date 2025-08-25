const form = document.getElementById("send-form")
const API_BASE = location.port && location.port !== "8000" ? "http://localhost:8000" : ""
const statusEl = document.getElementById("status")
const logEl = document.getElementById("log")
const btn = document.getElementById("send-btn")
const fileInput = document.getElementById("file")
const fileLabel = document.querySelector(".file-upload-label")
const useEnvCheckbox = document.getElementById("use_env")
const smtpFieldsContainer = document.getElementById("smtp_fields")
const smtpServerFieldsContainer = document.getElementById("smtp_server_fields")

fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0]
  const uploadTitle = document.querySelector(".upload-title")
  const uploadSubtitle = document.querySelector(".upload-subtitle")

  if (file) {
    uploadTitle.textContent = file.name
    uploadSubtitle.textContent = `${(file.size / 1024).toFixed(1)} KB - Arquivo selecionado ✓`
    fileLabel.style.borderColor = "#10b981"
    fileLabel.style.background = "rgba(16, 185, 129, 0.08)"
    fileLabel.style.transform = "scale(1.02)"

    // Add success animation
    setTimeout(() => {
      fileLabel.style.transform = "scale(1)"
    }, 200)
  } else {
    uploadTitle.textContent = "Clique para selecionar"
    uploadSubtitle.textContent = 'Planilha Excel (.xlsx) com colunas "Nome" e "E-mail"'
    fileLabel.style.borderColor = "rgba(102, 126, 234, 0.4)"
    fileLabel.style.background = "rgba(30, 41, 59, 0.4)"
    fileLabel.style.transform = "scale(1)"
  }
})

function log(msg, type = "info") {
  const time = new Date().toLocaleTimeString("pt-BR")
  const icons = {
    info: "💡",
    success: "🎉",
    error: "🚨",
    warning: "⚠️",
    progress: "⏳",
    email: "📧",
    check: "✅",
  }

  const icon = icons[type] || icons.info
  logEl.textContent += `[${time}] ${icon} ${msg}\n`
  logEl.scrollTop = logEl.scrollHeight

  const logContainer = document.querySelector(".log-container")
  const colors = {
    info: "rgba(102, 126, 234, 0.6)",
    success: "rgba(16, 185, 129, 0.6)",
    error: "rgba(239, 68, 68, 0.6)",
    warning: "rgba(245, 158, 11, 0.6)",
  }

  logContainer.style.borderColor = colors[type] || colors.info
  logContainer.style.boxShadow = `0 0 20px ${colors[type] || colors.info}40`

  setTimeout(() => {
    logContainer.style.borderColor = "rgba(51, 65, 85, 0.4)"
    logContainer.style.boxShadow = "none"
  }, 1500)
}

function updateStatus(message, type = "info") {
  statusEl.textContent = message
  statusEl.className = `status-display ${type}`

  // Add sophisticated animation based on type
  statusEl.style.animation = "none"
  setTimeout(() => {
    if (type === "success") {
      statusEl.style.animation = "successPulse 1.5s ease-in-out 3"
    } else if (type === "error") {
      statusEl.style.animation = "errorShake 0.5s ease-in-out 2"
    } else {
      statusEl.style.animation = "pulse 0.8s ease-in-out"
    }
  }, 10)
}

function validateForm() {
  const requiredFields = form.querySelectorAll("[required]")
  let isValid = true

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.style.borderColor = "#ef4444"
      field.style.boxShadow = "0 0 0 3px rgba(239, 68, 68, 0.25)"
      field.style.background = "rgba(239, 68, 68, 0.05)"
      isValid = false

      // Add shake animation
      field.style.animation = "errorShake 0.5s ease-in-out"

      // Reset error styling after user starts typing
      field.addEventListener("input", function resetError() {
        field.style.borderColor = ""
        field.style.boxShadow = ""
        field.style.background = ""
        field.style.animation = ""
        field.removeEventListener("input", resetError)
      })
    }
  })

  return isValid
}

// "Modo simples": usar .env e desabilitar campos SMTP
function applyUseEnvState(checked) {
  const user = document.getElementById("smtp_user")
  const pass = document.getElementById("smtp_pass")
  const server = document.getElementById("smtp_server")
  const port = document.getElementById("smtp_port")

  if (checked) {
    user.dataset.wasRequired = user.hasAttribute("required") ? "1" : "0"
    pass.dataset.wasRequired = pass.hasAttribute("required") ? "1" : "0"
    user.removeAttribute("required")
    pass.removeAttribute("required")

    user.disabled = true
    pass.disabled = true
    server.disabled = true
    port.disabled = true

    smtpFieldsContainer.style.display = "none"
    smtpServerFieldsContainer.style.display = "none"
  } else {
    if (user.dataset.wasRequired === "1") user.setAttribute("required", "")
    if (pass.dataset.wasRequired === "1") pass.setAttribute("required", "")

    user.disabled = false
    pass.disabled = false
    server.disabled = false
    port.disabled = false

    smtpFieldsContainer.style.display = "grid"
    smtpServerFieldsContainer.style.display = "grid"
  }
}

// Persistir estado do checkbox e aplicar ao carregar
if (useEnvCheckbox) {
  const saved = localStorage.getItem("emailSender_use_env")
  if (saved !== null) {
    useEnvCheckbox.checked = saved === "1"
  }
  applyUseEnvState(useEnvCheckbox.checked)
  useEnvCheckbox.addEventListener("change", () => {
    localStorage.setItem("emailSender_use_env", useEnvCheckbox.checked ? "1" : "0")
    applyUseEnvState(useEnvCheckbox.checked)
  })
}

form.addEventListener("submit", async (e) => {
  e.preventDefault()

  // Clear previous results
  statusEl.textContent = ""
  statusEl.className = "status-display"
  logEl.textContent = ""

  // Validate form
  if (!validateForm()) {
    updateStatus("Por favor, preencha todos os campos obrigatórios.", "error")
    log("Validação falhou - campos obrigatórios não preenchidos", "error")
    return
  }

  btn.disabled = true
  btn.style.transform = "scale(0.98)"

  try {
    const fd = new FormData(form)

    log("🚀 Iniciando envio da campanha...", "info")
    updateStatus("Processando arquivo e enviando emails...", "info")

    const progressMessages = [
      { msg: "Lendo arquivo Excel...", type: "progress" },
      { msg: "Validando endereços de email...", type: "check" },
      { msg: "Conectando ao servidor SMTP...", type: "progress" },
      { msg: "Enviando emails...", type: "email" },
    ]

    let progressIndex = 0
    const progressInterval = setInterval(() => {
      if (progressIndex < progressMessages.length) {
        const { msg, type } = progressMessages[progressIndex]
        log(msg, type)
        progressIndex++
      }
    }, 1200)

    const res = await fetch(`${API_BASE}/api/send`, {
      method: "POST",
      body: fd,
    })

    clearInterval(progressInterval)

    // Robust response parsing
    const ct = res.headers.get("content-type") || ""
    let data = null
    if (ct.includes("application/json")) {
      try {
        data = await res.json()
      } catch (_) {
        // ignore JSON parse error; will handle below
      }
    } else {
      const text = await res.text()
      if (!res.ok) {
        throw new Error(text || res.statusText)
      }
      if (!text && res.ok) {
        throw new Error("Resposta vazia do servidor")
      }
      throw new Error(text)
    }

    if (!res.ok) {
      const msg = (data && (data.error || data.message)) || res.statusText
      throw new Error(msg)
    }
    if (!data) {
      throw new Error("Resposta JSON vazia do servidor")
    }

    const summary = data.summary
    const successRate = summary.requested > 0 ? Math.round((summary.sent_ok / summary.requested) * 100) : 0

    if (summary.requested === 0) {
      updateStatus(
        "⚠️ Nenhum contato elegível encontrado. Verifique se a planilha possui coluna 'E-mail' e linhas sem 'Status=Contatado'.",
        "warning",
      )
    } else {
      updateStatus(
        `🎉 Campanha concluída com sucesso! ${summary.sent_ok}/${summary.requested} emails enviados (${successRate}% sucesso)`,
        "success",
      )
    }

    log(`🎊 Campanha finalizada com sucesso!`, "success")
    log(`📊 Estatísticas Detalhadas:`, "info")
    log(`   • Solicitados: ${summary.requested}`, "info")
    log(`   • Enviados: ${summary.sent_ok}`, "success")
    log(`   • Falhas: ${summary.failed}`, summary.failed > 0 ? "warning" : "info")
    log(`   • Taxa de sucesso: ${successRate}%`, "info")
    log(`   • Limite diário: ${summary.limit}`, "info")

    // Log individual results
    if (data.results && data.results.length > 0) {
      log(`\n📋 Detalhes por destinatário:`, "info")
      data.results.forEach((result, index) => {
        const status = result.success ? "success" : "error"
        const email = result.email || `Linha ${index + 1}`
        log(`   ${email}: ${result.status}`, status)
      })
    }

    if (summary.sent_ok > 0) {
      celebrateSuccess(successRate)
    }
  } catch (err) {
    updateStatus(`❌ Erro: ${err.message}`, "error")
    log(`💥 Erro durante o envio: ${err.message}`, "error")
    log("🔧 Verifique suas configurações e tente novamente.", "warning")
  } finally {
    btn.disabled = false
    btn.style.transform = "scale(1)"
  }
})

function celebrateSuccess(successRate = 100) {
  // Create multiple waves of confetti
  const colors = ["#667eea", "#764ba2", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

  // First wave - immediate burst
  for (let i = 0; i < 60; i++) {
    setTimeout(() => {
      createConfetti(colors[Math.floor(Math.random() * colors.length)])
    }, i * 30)
  }

  // Second wave - delayed burst
  setTimeout(() => {
    for (let i = 0; i < 40; i++) {
      setTimeout(() => {
        createConfetti(colors[Math.floor(Math.random() * colors.length)])
      }, i * 40)
    }
  }, 1000)

  // Third wave - final celebration
  setTimeout(() => {
    for (let i = 0; i < 30; i++) {
      setTimeout(() => {
        createConfetti(colors[Math.floor(Math.random() * colors.length)])
      }, i * 50)
    }
  }, 2000)

  if (successRate >= 90) {
    createScreenFlash()
  }

  createFloatingMessages(successRate)
}

function createConfetti(color) {
  const confetti = document.createElement("div")
  const size = Math.random() * 8 + 4
  const duration = Math.random() * 2 + 2
  const delay = Math.random() * 0.5

  confetti.style.cssText = `
    position: fixed;
    width: ${size}px;
    height: ${size}px;
    background: ${color};
    top: -20px;
    left: ${Math.random() * 100}vw;
    border-radius: ${Math.random() > 0.5 ? "50%" : "0"};
    pointer-events: none;
    z-index: 10000;
    animation: confettiFall ${duration}s linear ${delay}s forwards;
    box-shadow: 0 0 10px ${color}40;
  `

  document.body.appendChild(confetti)

  setTimeout(
    () => {
      confetti.remove()
    },
    (duration + delay) * 1000,
  )
}

function createScreenFlash() {
  const flash = document.createElement("div")
  flash.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.3) 0%, transparent 70%);
    pointer-events: none;
    z-index: 9999;
    animation: flashEffect 0.8s ease-out forwards;
  `

  const style = document.createElement("style")
  style.textContent = `
    @keyframes flashEffect {
      0% { opacity: 0; }
      50% { opacity: 1; }
      100% { opacity: 0; }
    }
  `
  document.head.appendChild(style)
  document.body.appendChild(flash)

  setTimeout(() => {
    flash.remove()
    style.remove()
  }, 800)
}

function createFloatingMessages(successRate) {
  const messages = ["🎉 Incrível!", "✨ Perfeito!", "🚀 Fantástico!", "💫 Excelente!", "🎊 Sucesso!"]

  messages.forEach((message, index) => {
    setTimeout(() => {
      const messageEl = document.createElement("div")
      messageEl.textContent = message
      messageEl.style.cssText = `
        position: fixed;
        top: 50%;
        left: ${20 + index * 15}%;
        transform: translate(-50%, -50%);
        font-size: 2rem;
        font-weight: bold;
        color: #10b981;
        pointer-events: none;
        z-index: 9998;
        animation: floatUp 3s ease-out forwards;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
      `

      const style = document.createElement("style")
      style.textContent = `
        @keyframes floatUp {
          0% {
            opacity: 0;
            transform: translate(-50%, -50%) scale(0.5);
          }
          20% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1.2);
          }
          100% {
            opacity: 0;
            transform: translate(-50%, -150%) scale(0.8);
          }
        }
      `
      document.head.appendChild(style)
      document.body.appendChild(messageEl)

      setTimeout(() => {
        messageEl.remove()
        style.remove()
      }, 3000)
    }, index * 300)
  })
}

document.addEventListener("keydown", (e) => {
  // Submit form with Ctrl+Enter
  if (e.ctrlKey && e.key === "Enter" && !btn.disabled) {
    form.dispatchEvent(new Event("submit"))
  }

  // Clear log with Ctrl+L
  if (e.ctrlKey && e.key === "l") {
    e.preventDefault()
    logEl.textContent = ""
    updateStatus("", "")
  }

  if (e.ctrlKey && e.key === "f") {
    e.preventDefault()
    fileInput.focus()
  }

  if (e.ctrlKey && e.key === "s") {
    e.preventDefault()
    btn.focus()
  }
})

// Auto-save form data to localStorage
const formFields = form.querySelectorAll('input:not([type="file"]), textarea')
formFields.forEach((field) => {
  // Load saved data
  const savedValue = localStorage.getItem(`emailSender_${field.name}`)
  if (savedValue && field.type !== "password") {
    field.value = savedValue
  }

  // Save data on change
  field.addEventListener("input", () => {
    if (field.type !== "password") {
      localStorage.setItem(`emailSender_${field.name}`, field.value)
    }
  })
})

document.querySelectorAll("[title]").forEach((element) => {
  element.addEventListener("mouseenter", showTooltip)
  element.addEventListener("mouseleave", hideTooltip)
})

function showTooltip(e) {
  const tooltip = document.createElement("div")
  tooltip.className = "tooltip"
  tooltip.textContent = e.target.title
  tooltip.style.cssText = `
    position: absolute;
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(30, 41, 59, 0.9));
    color: white;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 12px;
    pointer-events: none;
    z-index: 10001;
    white-space: nowrap;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.3);
    animation: tooltipFadeIn 0.2s ease-out;
  `

  const style = document.createElement("style")
  style.textContent = `
    @keyframes tooltipFadeIn {
      from {
        opacity: 0;
        transform: translateY(5px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `
  document.head.appendChild(style)
  document.body.appendChild(tooltip)

  const rect = e.target.getBoundingClientRect()
  tooltip.style.left = rect.left + "px"
  tooltip.style.top = rect.top - tooltip.offsetHeight - 12 + "px"

  e.target.tooltip = tooltip
  e.target.tooltipStyle = style
  e.target.removeAttribute("title")
}

function hideTooltip(e) {
  if (e.target.tooltip) {
    e.target.tooltip.remove()
    e.target.tooltipStyle.remove()
    e.target.title = e.target.tooltip.textContent
    delete e.target.tooltip
    delete e.target.tooltipStyle
  }
}

document.querySelectorAll(".form-section").forEach((section, index) => {
  section.style.scrollMarginTop = "2rem"

  // Add intersection observer for section highlighting
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.borderColor = "rgba(102, 126, 234, 0.5)"
          setTimeout(() => {
            entry.target.style.borderColor = "rgba(51, 65, 85, 0.4)"
          }, 2000)
        }
      })
    },
    { threshold: 0.5 },
  )

  observer.observe(section)
})

const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
}

const animationObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = "running"
      entry.target.style.opacity = "1"
    }
  })
}, observerOptions)

document.querySelectorAll(".form-section").forEach((section) => {
  section.style.animationPlayState = "paused"
  section.style.opacity = "0.8"
  animationObserver.observe(section)
})

function typeWriter(element, text, speed = 50) {
  let i = 0
  element.textContent = ""

  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i)
      i++
      setTimeout(type, speed)
    }
  }

  type()
}

// Apply typing effect to subtitle on load
window.addEventListener("load", () => {
  const subtitle = document.querySelector(".subtitle")
  const originalText = subtitle.textContent
  typeWriter(subtitle, originalText, 30)
})

console.log("🚀 Email Sender Pro carregado com sucesso! ✨")
console.log("💡 Dicas:")
console.log("   • Ctrl+Enter: Enviar formulário")
console.log("   • Ctrl+L: Limpar log")
console.log("   • Ctrl+F: Focar no upload de arquivo")
console.log("   • Ctrl+S: Focar no botão de envio")
