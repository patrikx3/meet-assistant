import '@fortawesome/fontawesome-free/css/all.min.css'
import './style.css'

const $ = id => document.getElementById(id)

/* ── State ──────────────────────────────────────── */
let theme = localStorage.getItem('ma-theme') || 'dark'
let fontSize = parseInt(localStorage.getItem('ma-fontsize') || '20')
let language = localStorage.getItem('ma-language') || 'en'

let ws, reconnectMs = 1000
let autoScroll = true
let availableLanguages = {}
let entries = []
let micCapture = null, tabCapture = null

/* ── Theme / language selector ──────────────────── */
function applyTheme() {
 document.documentElement.setAttribute('data-theme', theme)
 $('themeBtn').innerHTML = theme === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>'
}

function populateLanguages() {
 const sel = $('langSelect')
 sel.innerHTML = ''
 for (const [code, native] of Object.entries(availableLanguages)) {
  const opt = document.createElement('option')
  opt.value = code
  opt.textContent = native
  sel.appendChild(opt)
 }
 sel.value = language
}

function applyFontSize() {
 document.querySelectorAll('.entry-text').forEach(el => { el.style.fontSize = fontSize + 'px' })
}

/* ── Scrolling ──────────────────────────────────── */
function isAtBottom(el) { return el.scrollHeight - el.scrollTop - el.clientHeight < 50 }
function scrollToBottom() {
 $('scrollAll').scrollTop = $('scrollAll').scrollHeight
 autoScroll = true
 updateScrollBtn()
}
function updateScrollBtn() { $('scrollBtn').style.display = autoScroll ? 'none' : 'flex' }

$('scrollAll').addEventListener('scroll', () => {
 autoScroll = isAtBottom($('scrollAll'))
 updateScrollBtn()
})

/* ── Entry rendering ────────────────────────────── */
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML }
function speakerClass(n) { return n ? 'spk-' + (((n - 1) % 8) + 1) : 'spk-unknown' }
function speakerLabel(n) { return n ? 'Speaker ' + n : 'Speaker' }

function createEntryEl(data) {
 const div = document.createElement('div')
 const spk = data.speaker
 div.className = 'entry ' + speakerClass(spk)
 const langHtml = data.lang ? '<span class="entry-lang">' + esc(data.lang) + '</span>' : ''
 div.innerHTML =
  '<div class="entry-header">' +
   '<span class="entry-time">' + esc(data.time) + '</span>' +
   '<span class="entry-source ' + speakerClass(spk) + '-src">' + esc(speakerLabel(spk)) + '</span>' +
   langHtml +
  '</div>' +
  '<div class="entry-text" style="font-size:' + fontSize + 'px">' + esc(data.text) + '</div>'
 return div
}

function appendEntry(data) {
 const el = createEntryEl(data)
 $('scrollAll').appendChild(el)
 if (autoScroll) setTimeout(() => { $('scrollAll').scrollTop = $('scrollAll').scrollHeight }, 30)
}

function rerender() {
 $('scrollAll').innerHTML = ''
 entries.forEach(appendEntry)
}

/* ── Status ─────────────────────────────────────── */
function setStatus(status) {
 const dot = $('dot'), txt = $('statusText')
 dot.classList.remove('ok', 'pulse')
 if (status === 'listening') { dot.classList.add('ok', 'pulse'); txt.textContent = 'Listening...' }
 else if (status === 'processing') { dot.classList.add('ok'); txt.textContent = 'Processing...' }
 else if (status === 'loading') { txt.textContent = 'Loading engine...' }
 else if (status === 'error') { txt.textContent = 'Error' }
}

function showError(msg) {
 const toast = document.createElement('div')
 toast.className = 'error-toast'
 toast.textContent = msg
 document.body.appendChild(toast)
 setTimeout(() => toast.remove(), 5000)
}

/* ── WebSocket ──────────────────────────────────── */
function connect() {
 const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
 ws = new WebSocket(proto + '//' + location.host + '/ws')

 ws.onopen = () => {
  reconnectMs = 1000
  $('dot').classList.add('ok')
  $('statusText').textContent = 'Connected'
 }

 ws.onmessage = e => {
  const data = JSON.parse(e.data)
  switch (data.type) {
   case 'init':
   case 'state':
    if (data.languages) { availableLanguages = data.languages; populateLanguages() }
    if (data.engines && data.engine) $('engineLabel').textContent = data.engines[data.engine] || ''
    if (data.language && data.type === 'init') {
     language = data.language
     $('langSelect').value = language
    }
    break
   case 'transcript':
    entries.push(data); appendEntry(data); break
   case 'status': setStatus(data.status); break
   case 'error': showError(data.error); break
  }
 }

 ws.onclose = () => {
  $('dot').classList.remove('ok', 'pulse')
  $('statusText').textContent = 'Disconnected'
  setTimeout(connect, reconnectMs)
  reconnectMs = Math.min(reconnectMs * 2, 15000)
 }
}

/* ── Browser audio capture ──────────────────────── */
function writeWavStr(view, offset, str) {
 for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
}

function encodeWav(samples, sampleRate) {
 const buf = new ArrayBuffer(44 + samples.length * 2)
 const v = new DataView(buf)
 writeWavStr(v, 0, 'RIFF'); v.setUint32(4, 36 + samples.length * 2, true)
 writeWavStr(v, 8, 'WAVE'); writeWavStr(v, 12, 'fmt ')
 v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true)
 v.setUint32(24, sampleRate, true); v.setUint32(28, sampleRate * 2, true)
 v.setUint16(32, 2, true); v.setUint16(34, 16, true)
 writeWavStr(v, 36, 'data'); v.setUint32(40, samples.length * 2, true)
 for (let i = 0; i < samples.length; i++) {
  const s = Math.max(-1, Math.min(1, samples[i]))
  v.setInt16(44 + i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
 }
 return new Uint8Array(buf)
}

function startBrowserCapture(stream) {
 let ctx
 try { ctx = new AudioContext({ sampleRate: 16000 }) } catch { ctx = new AudioContext() }
 const src = ctx.createMediaStreamSource(stream)
 const processor = ctx.createScriptProcessor(4096, 1, 1)
 let buffer = [], bufLen = 0
 const chunkSize = ctx.sampleRate * 5

 processor.onaudioprocess = e => {
  if (!ws || ws.readyState !== 1) return
  const data = new Float32Array(e.inputBuffer.getChannelData(0))
  buffer.push(data); bufLen += data.length
  if (bufLen >= chunkSize) {
   const combined = new Float32Array(bufLen)
   let off = 0
   for (const c of buffer) { combined.set(c, off); off += c.length }
   buffer = []; bufLen = 0
   let peak = 0
   for (let i = 0; i < combined.length; i++) peak = Math.max(peak, Math.abs(combined[i]))
   if (peak < 0.01) return
   const wav = encodeWav(combined, ctx.sampleRate)
   ws.send(wav.buffer)
  }
 }
 src.connect(processor); processor.connect(ctx.destination)
 return { ctx, processor, stream }
}

function stopBrowserCapture(capture) {
 if (!capture) return
 capture.stream.getTracks().forEach(t => t.stop())
 capture.processor.disconnect(); capture.ctx.close()
}

$('micCaptureBtn').onclick = async () => {
 if (micCapture) {
  stopBrowserCapture(micCapture); micCapture = null
  $('micCaptureBtn').classList.remove('active', 'recording')
 } else {
  try {
   const stream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
   })
   micCapture = startBrowserCapture(stream)
   $('micCaptureBtn').classList.add('active', 'recording')
  } catch (e) { showError('Mic: ' + e.message) }
 }
}

$('tabCaptureBtn').onclick = async () => {
 if (tabCapture) {
  stopBrowserCapture(tabCapture); tabCapture = null
  $('tabCaptureBtn').classList.remove('active', 'recording')
 } else {
  try {
   const stream = await navigator.mediaDevices.getDisplayMedia({ audio: true, video: true })
   stream.getVideoTracks().forEach(t => t.stop())
   if (!stream.getAudioTracks().length) { showError('No audio track - check "Share audio"'); return }
   tabCapture = startBrowserCapture(stream)
   $('tabCaptureBtn').classList.add('active', 'recording')
  } catch (e) { showError('Tab: ' + e.message) }
 }
}

/* ── Init ───────────────────────────────────────── */
applyTheme()

$('themeBtn').onclick = () => { theme = theme === 'dark' ? 'light' : 'dark'; localStorage.setItem('ma-theme', theme); applyTheme() }
$('langSelect').onchange = () => {
 language = $('langSelect').value
 localStorage.setItem('ma-language', language)
 if (ws?.readyState === 1) ws.send(JSON.stringify({ action: 'set_language', language }))
}
$('fontUp').onclick = () => { fontSize = Math.min(fontSize + 2, 40); localStorage.setItem('ma-fontsize', fontSize); applyFontSize() }
$('fontDown').onclick = () => { fontSize = Math.max(fontSize - 2, 12); localStorage.setItem('ma-fontsize', fontSize); applyFontSize() }
$('clearBtn').onclick = () => {
 entries = []; rerender()
 if (ws?.readyState === 1) ws.send(JSON.stringify({ action: 'reset_speakers' }))
}
$('exportBtn').onclick = () => {
 let txt = 'Meet Assistant\n' + '='.repeat(40) + '\n\n'
 entries.forEach(e => {
  txt += '[' + e.time + '] ' + speakerLabel(e.speaker) + (e.lang ? ' [' + e.lang + ']' : '') + '\n' + e.text + '\n\n'
 })
 const blob = new Blob([txt], { type: 'text/plain' })
 const a = document.createElement('a')
 a.href = URL.createObjectURL(blob)
 a.download = 'transcript-' + new Date().toISOString().slice(0, 10) + '.txt'
 a.click()
 URL.revokeObjectURL(a.href)
}
$('scrollBtn').onclick = scrollToBottom

connect()
