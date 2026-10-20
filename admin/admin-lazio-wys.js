/* Funzioni dell'EDITOR VISIVO delle pagine (Home ecc.), usate da admin-lazio.js. Nessuna dipendenza dall'admin: lavorano solo sul DOM, cosi' si collaudano con jsdom.
   COSA FA: mostra la pagina vera in un iframe e rende scrivibili i testi (come l'editor di WordPress); i pezzi automatici di Jekyll ({% ... %}, {{ ... }}) diventano
   riquadri grigi non modificabili e al salvataggio tornano IDENTICI all'originale.
   PUNTI CRITICI: (1) i tag Liquid fuori dai tag HTML diventano commenti <!--LQn-->, dentro un tag (attributi) diventano @@LQn@@: cosi' il parser del browser non li sposta
   (un <span> dentro una tabella verrebbe spostato fuori). Il blocco {% for %}...{% endfor %} e' un pezzo unico. (2) le immagini lazy (data-orig-src) si mostrano col loro
   vero indirizzo, ma al salvataggio l'src originale torna com'era se non l'hai cambiata. (3) i testi con soli numeri (contatori animati) non si modificano qui: il
   valore vero e' in un attributo e il numero visibile lo scrive uno script. */
(function (W) {
  var INLINE = /^(A|B|STRONG|EM|I|U|SPAN|BR|SMALL|SUP|SUB|CODE|MARK|S|ABBR)$/;
  var SKIP = /^(SCRIPT|STYLE|NOSCRIPT|SVG|IMG|BR|IFRAME|VIDEO|AUDIO|CANVAS|INPUT|TEXTAREA|SELECT|BUTTON|FORM)$/;
  var LZW = {};

  LZW.CSS = '.lzlq{display:inline-block!important;background:#f0f0f1!important;color:#50575e!important;font:11px/1.4 monospace!important;padding:2px 8px!important;border:1px dashed #8c8f94!important;margin:2px!important;opacity:1!important;visibility:visible!important;transform:none!important;position:static!important;float:none!important;width:auto!important;height:auto!important;text-transform:none!important;letter-spacing:0!important}' +
    '[contenteditable=true]{cursor:text;outline:1px dashed transparent;outline-offset:2px}' +
    '[contenteditable=true]:hover{outline-color:#72aee6}' +
    '[contenteditable=true]:focus{outline:2px solid #2271b1;background-color:rgba(34,113,177,.07)}' +
    'main img{cursor:pointer}main img:hover{outline:3px solid #2271b1}' +
    '*{animation:none!important;transition:none!important}' +
    '.fusion-slider-loading,.fusion-loading-container{display:none!important}.tfs-slider,.fusion-slider-container .slides{visibility:visible!important;opacity:1!important}' +
    '.fusion-animated,[class*="fusion-animated"],[data-animationtype]{opacity:1!important;visibility:visible!important;transform:none!important}';

  /* etichetta del riquadro grigio; '' = nessun riquadro (pezzi tecnici invisibili) */
  LZW.label = function (raw) {
    var t = raw.replace(/\s+/g, ' ').trim(), m;
    if (/^\{%-?\s*(raw|endraw|assign|capture|endcapture|comment|endcomment)\b/.test(t)) return '';
    if ((m = /^\{%-?\s*include\s+([^\s%]+)/.exec(t))) return 'Blocco automatico: ' + m[1].replace(/^.*\//, '').replace(/\.\w+$/, '');
    if (/^\{%-?\s*for\b/.test(t)) return 'Elenco automatico (si genera dagli articoli)';
    return t.length > 40 ? t.slice(0, 40) + '…' : t;
  };

  /* src (HTML con Liquid) -> HTML senza Liquid; store riceve i pezzi originali */
  LZW.tokenize = function (src, store) {
    var out = '', i = 0, n = src.length, inTag = false, qt = '', c;
    while (i < n) {
      c = src.charAt(i);
      if (c === '{' && (src.charAt(i + 1) === '%' || src.charAt(i + 1) === '{')) {
        var cl = src.charAt(i + 1) === '%' ? '%}' : '}}', j = src.indexOf(cl, i + 2);
        if (j > 0) {
          var end = j + 2, raw = src.slice(i, end);
          if (/^\{%-?\s*for\b/.test(raw)) {
            var depth = 1, re = /\{%-?\s*(for|endfor)\b[^%]*%\}/g, mm;
            re.lastIndex = end;
            while ((mm = re.exec(src))) { depth += mm[1] === 'for' ? 1 : -1; if (!depth) { end = re.lastIndex; break; } }
            raw = src.slice(i, end);
          }
          var idx = store.push(raw) - 1;
          out += inTag ? '@@LQ' + idx + '@@' : '<!--LQ' + idx + '-->';
          i = end; continue;
        }
      }
      if (!inTag && c === '<') {
        if (src.substr(i, 4) === '<!--') { var ce = src.indexOf('-->', i + 4); ce = ce < 0 ? n : ce + 3; out += src.slice(i, ce); i = ce; continue; }
        if (/[a-zA-Z\/]/.test(src.charAt(i + 1))) { inTag = true; qt = ''; }
      } else if (inTag) {
        if (qt) { if (c === qt) qt = ''; } else if (c === '"' || c === "'") qt = c; else if (c === '>') inTag = false;
      }
      out += c; i++;
    }
    return out;
  };

  function comments(root) {
    var w = root.ownerDocument.createTreeWalker(root, 128, null), l = [], c;
    while ((c = w.nextNode())) if (/^LQ\d+$/.test(c.nodeValue)) l.push(c);
    return l;
  }
  LZW.chips = function (root, store) {
    comments(root).forEach(function (c) {
      var lab = LZW.label(store[+c.nodeValue.slice(2)]); if (!lab) return;
      var s = root.ownerDocument.createElement('span');
      s.className = 'lzlq'; s.setAttribute('contenteditable', 'false'); s.textContent = lab;
      c.parentNode.insertBefore(s, c);
    });
  };

  function isTextBlock(el) {
    var t = el.textContent || '';
    if (!/\S/.test(t) || /^[\s\d.,+% ]+$/.test(t)) return false;
    if (el.querySelector('.lzlq, img, svg, input, textarea, select, video, iframe, canvas, button, form')) return false;
    if (comments(el).length) return false;
    var all = el.getElementsByTagName('*'), k;
    for (k = 0; k < all.length; k++) if (!INLINE.test(all[k].nodeName)) return false;
    return true;
  }
  /* rende scrivibili i blocchi di solo testo (il piu' esterno possibile); ritorna quanti */
  LZW.markEditable = function (root) {
    var n = 0;
    (function walk(el) {
      [].slice.call(el.children).forEach(function (c) {
        if (SKIP.test(c.nodeName) || (c.className && /\blzlq\b/.test(c.className))) return;
        if (isTextBlock(c)) { c.setAttribute('contenteditable', 'true'); n++; } else walk(c);
      });
    })(root);
    return n;
  };

  /* immagini: mostra l'indirizzo vero di quelle lazy e ricorda l'src originale */
  LZW.prepImgs = function (root) {
    [].forEach.call(root.getElementsByTagName('img'), function (im) {
      im.setAttribute('data-lz-src0', im.hasAttribute('src') ? im.getAttribute('src') : '\u0000');
      var real = im.getAttribute('data-orig-src') || im.getAttribute('data-src');
      if (real) im.setAttribute('src', real);
      im.removeAttribute('loading');
    });
  };

  /* zona <main> dell'iframe -> HTML sorgente (con Liquid ripristinato) */
  LZW.serialize = function (mainEl, store) {
    var m = mainEl.cloneNode(true);
    [].slice.call(m.querySelectorAll('.lzlq')).forEach(function (e) { e.parentNode.removeChild(e); });
    [].forEach.call(m.querySelectorAll('[contenteditable]'), function (e) { e.removeAttribute('contenteditable'); });
    [].forEach.call(m.getElementsByTagName('img'), function (im) {
      var nw = im.getAttribute('data-lz-new'), s0 = im.getAttribute('data-lz-src0');
      if (nw !== null) {
        im.setAttribute('src', nw);
        if (im.hasAttribute('data-orig-src')) im.setAttribute('data-orig-src', nw);
        if (im.hasAttribute('data-src')) im.setAttribute('data-src', nw);
        im.removeAttribute('srcset'); im.removeAttribute('data-srcset');
      } else if (s0 !== null) {
        if (s0 === '\u0000') im.removeAttribute('src'); else im.setAttribute('src', s0);
      }
      im.removeAttribute('data-lz-new'); im.removeAttribute('data-lz-src0');
    });
    var h = m.innerHTML;
    h = h.replace(/<!--LQ(\d+)-->/g, function (x, n) { return store[+n]; });
    return h.replace(/@@LQ(\d+)@@/g, function (x, n) { return store[+n]; });
  };

  W.LZW = LZW;
  if (typeof module !== 'undefined' && module.exports) module.exports = LZW;
})(typeof window !== 'undefined' ? window : this);
