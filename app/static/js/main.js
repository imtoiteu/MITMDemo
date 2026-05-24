/**
 * Security Awareness Demo — main.js
 * Light UI enhancements. No obfuscation, fully commented.
 * No external network requests are made from this file.
 */

/* ── Copy Wireshark filters on click ── */
document.querySelectorAll('.ws-filter').forEach(function (el) {
  el.setAttribute('title', 'Click to copy filter');
  el.addEventListener('click', function () {
    var text = el.textContent.trim();
    navigator.clipboard.writeText(text).then(function () {
      var orig = el.textContent;
      el.textContent = '✓ Copied!';
      el.style.color = 'var(--clr-success)';
      setTimeout(function () {
        el.textContent = orig;
        el.style.color = '';
      }, 1500);
    }).catch(function () {
      /* Clipboard API unavailable (non-HTTPS context) — show manual hint */
      el.setAttribute('title', 'Select and copy manually: ' + text);
    });
  });
});

/* ── Toggle password visibility on login page ── */
var toggleBtn = document.getElementById('toggle-pw');
var pwInput   = document.getElementById('password');
if (toggleBtn && pwInput) {
  toggleBtn.addEventListener('click', function () {
    if (pwInput.type === 'password') {
      pwInput.type = 'text';
      toggleBtn.textContent = '🙈';
      toggleBtn.setAttribute('aria-label', 'Hide password');
    } else {
      pwInput.type = 'password';
      toggleBtn.textContent = '👁';
      toggleBtn.setAttribute('aria-label', 'Show password');
    }
  });
}

/* ── File upload drag-and-drop zone ── */
var uploadZone  = document.getElementById('upload-zone');
var fileInput   = document.getElementById('file-input');
var selectedBox = document.getElementById('selected-file');
var selectedName = document.getElementById('selected-name');
var selectedSize = document.getElementById('selected-size');

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  var k = 1024;
  var sizes = ['B', 'KB', 'MB', 'GB'];
  var i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function showSelectedFile(file) {
  if (selectedName) selectedName.textContent = file.name;
  if (selectedSize) selectedSize.textContent = formatBytes(file.size);
  if (selectedBox)  selectedBox.style.display = 'flex';
  var icon = document.getElementById('upload-icon');
  if (icon) icon.textContent = '📄';
}

if (uploadZone && fileInput) {
  /* Click on zone opens file picker */
  uploadZone.addEventListener('click', function () { fileInput.click(); });

  /* File selected via picker */
  fileInput.addEventListener('change', function () {
    if (fileInput.files && fileInput.files[0]) {
      showSelectedFile(fileInput.files[0]);
    }
  });

  /* Drag over */
  uploadZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
  });

  uploadZone.addEventListener('dragleave', function () {
    uploadZone.classList.remove('drag-over');
  });

  /* Drop */
  uploadZone.addEventListener('drop', function (e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    var files = e.dataTransfer.files;
    if (files && files[0]) {
      /* Assign to hidden input so form submits the dropped file */
      var dt = new DataTransfer();
      dt.items.add(files[0]);
      fileInput.files = dt.files;
      showSelectedFile(files[0]);
    }
  });
}

/* ── Chat: auto-scroll to bottom on load ── */
var chatMessages = document.getElementById('chat-messages');
if (chatMessages) {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ── Highlight the capture box briefly after login ── */
var captureBox = document.getElementById('capture-box');
if (captureBox) {
  captureBox.style.transition = 'box-shadow 0.4s ease';
  setTimeout(function () {
    captureBox.style.boxShadow = '0 0 0 3px rgba(63,185,80,0.5)';
    setTimeout(function () { captureBox.style.boxShadow = ''; }, 1200);
  }, 300);
}

/* ── Animate nav active link indicator ── */
var activeLink = document.querySelector('.nav-link.active');
if (activeLink) {
  activeLink.style.transition = 'background 0.3s ease';
}
