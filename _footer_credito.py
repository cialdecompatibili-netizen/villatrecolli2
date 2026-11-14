# -*- coding: utf-8 -*-
"""Sostituisce il <p> copyright del footer (CrazyWeb / Avada) in tutte le pagine html con: anno automatico + credito webtomars.it (occhio animato).
Idempotente: ri-lanciabile (riconosce anche il blocco gia' messo, marker WTM-FOOT). Uso: python _footer_credito.py [--dry]"""
import re, glob, sys
DRY = "--dry" in sys.argv
NEW = ('<p><!--WTM-FOOT-->&copy; Copyright 2012 - <span class="wtm-y">2026</span>'
 '<script>document.querySelectorAll(".wtm-y").forEach(function(e){e.textContent=new Date().getFullYear()})</script>'
 ' |   <span class="wtm-fc">Design, Development &amp; Digital Marketing by '
 '<span class="wtm-eye" aria-hidden="true"><svg viewBox="0 0 48 32" xmlns="http://www.w3.org/2000/svg"><defs>'
 '<radialGradient id="wtmIris" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#ffe2b8"/><stop offset=".45" stop-color="#f0966a"/>'
 '<stop offset=".8" stop-color="#cf5a33"/><stop offset="1" stop-color="#6b2310"/></radialGradient>'
 '<clipPath id="wtmClip"><path d="M2 16 Q24 -2 46 16 Q24 34 2 16 Z"/></clipPath></defs><g class="wtm-open">'
 '<path d="M2 16 Q24 -2 46 16 Q24 34 2 16 Z" fill="#fff6ee"/><g clip-path="url(#wtmClip)"><g class="wtm-look">'
 '<circle cx="24" cy="16" r="9.5" fill="url(#wtmIris)"/><ellipse cx="24" cy="16" rx="2.4" ry="6" fill="#1a0a05"/>'
 '<circle cx="21" cy="12.5" r="1.7" fill="#fff" opacity=".9"/></g></g>'
 '<path d="M2 16 Q24 -2 46 16 Q24 34 2 16 Z" fill="none" stroke="#f0966a" stroke-width="1.6"/></g></svg></span>'
 '<a class="wtm-link" href="https://webtomars.it/" target="_blank" rel="noopener">webtomars.it</a></span>'
 '     |   All Rights Reserved'
 '<style>.wtm-fc{display:inline-flex;align-items:center;gap:8px;vertical-align:middle}'
 '.wtm-eye{position:relative;display:inline-block;width:34px;height:23px;margin:0 2px}'
 '.wtm-eye:before{content:"";position:absolute;left:-8px;right:-8px;top:-8px;bottom:-8px;border-radius:50%;'
 'background:radial-gradient(circle,rgba(255,170,110,.65) 0%,rgba(207,90,51,.30) 42%,rgba(207,90,51,0) 72%);filter:blur(3px);animation:wtm-aura 3.4s ease-in-out infinite}'
 '.wtm-eye svg{position:relative;width:100%;height:100%;overflow:visible;display:block}'
 '.wtm-open{transform-origin:24px 16px;animation:wtm-blink 6s infinite}.wtm-look{animation:wtm-look 7s ease-in-out infinite}'
 '.wtm-fc a.wtm-link{color:#f4a77f!important;font-weight:600;text-decoration:none!important;text-shadow:0 0 6px rgba(244,167,127,.55);animation:wtm-glow 3.4s ease-in-out infinite}'
 '.wtm-fc a.wtm-link:hover{color:#fff!important}'
 '@keyframes wtm-aura{0%,100%{opacity:.4;transform:scale(.82)}50%{opacity:1;transform:scale(1.18)}}'
 '@keyframes wtm-glow{0%,100%{text-shadow:0 0 4px rgba(244,167,127,.35)}50%{text-shadow:0 0 13px rgba(255,170,110,.95)}}'
 '@keyframes wtm-blink{0%,92%,100%{transform:scaleY(1)}95%{transform:scaleY(.06)}}'
 '@keyframes wtm-look{0%,14%,100%{transform:translateX(0)}28%,44%{transform:translateX(4px)}58%,74%{transform:translateX(-4px)}}'
 '@media (prefers-reduced-motion:reduce){.wtm-eye:before,.wtm-open,.wtm-look,.wtm-fc a.wtm-link{animation:none}}</style></p>')
PAT = re.compile(r"<p>(?:<!--WTM-FOOT-->)?(?:\xa9|&copy;)\s*Copyright 2012 - (?:20\d\d|<span class=\"wtm-y\">.*?</span><script>.*?</script>).*?(?:All Rights Reserved(?:\s*\|\s*Powered by <a [^>]*>WordPress</a>)?)(?:<style>\.wtm-fc.*?</style>)?</p>", re.S)
tot = 0; files = 0
for f in glob.glob("**/*.html", recursive=True):
    if f.startswith((".git", "node_modules")): continue
    b = open(f, "rb").read(); t = b.decode("utf-8", "surrogateescape")
    n, k = PAT.subn(lambda m: NEW, t)
    if k:
        tot += k; files += 1
        if not DRY: open(f, "wb").write(n.encode("utf-8", "surrogateescape"))
print("file modificati:", files, "| sostituzioni:", tot, "(DRY)" if DRY else "")
