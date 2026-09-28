/* Motor gráfico determinista: window.renderFrame(t) deja la página exactamente
   en el instante t (segundos). Todas las animaciones viven en una línea de tiempo
   GSAP pausada + funciones continuas dependientes de t. */
(function () {
  "use strict";
  const V = window.VIDEO;
  const T = V.timeline;
  const W = 1920, H = 1080;
  document.documentElement.style.setProperty("--accent", V.accent);
  document.documentElement.style.setProperty("--accent2", V.accent2);

  const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
  const every = [];
  const bursts = [];
  const stage = document.getElementById("stage");
  const chrome = document.getElementById("chrome");
  const SVGNS = "http://www.w3.org/2000/svg";

  // ───────────────────────────── utilidades
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const svgIcon = (n) => V.icons[n] || "";
  const rich = (s) => esc(s).replace(/→/g, `<span class="arr">${svgIcon("arrow-right")}</span>`);
  function mk(tag, cls, parent, html) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    if (parent) parent.appendChild(e);
    return e;
  }
  function place(e, x, y, w, h) {
    e.style.left = x + "px"; e.style.top = y + "px";
    if (w !== undefined && w !== null) e.style.width = w + "px";
    if (h !== undefined && h !== null) e.style.height = h + "px";
    return e;
  }
  function icirc(name, size, parent) {
    const c = mk("div", "icirc", parent, svgIcon(name));
    c.style.width = c.style.height = size + "px";
    return c;
  }
  function ico(name, cls, parent) { return mk("div", "ico " + (cls || ""), parent, svgIcon(name)); }
  function splitWords(el, text) {
    el.innerHTML = String(text).split(" ").map((w) => `<span class="w"><span>${rich(w)}</span></span>`).join(" ");
    return Array.from(el.querySelectorAll(".w > span"));
  }
  function fitWidth(el, maxW, size, min) {
    let s = size; el.style.fontSize = s + "px";
    while (el.scrollWidth > maxW && s > min) { s -= 2; el.style.fontSize = s + "px"; }
    return s;
  }
  function svgLayer(parent) {
    const s = document.createElementNS(SVGNS, "svg");
    s.setAttribute("width", W); s.setAttribute("height", H);
    s.style.position = "absolute"; s.style.left = "0"; s.style.top = "0"; s.style.overflow = "visible";
    s.innerHTML = `<defs><linearGradient id="gacc${Math.random().toString(36).slice(2, 7)}" gradientUnits="userSpaceOnUse" x1="120" x2="1800" y1="0" y2="0">
      <stop offset="0" stop-color="${V.accent}"/><stop offset="1" stop-color="${V.accent2}"/></linearGradient></defs>`;
    s._gid = s.querySelector("linearGradient").id;
    parent.appendChild(s);
    return s;
  }
  function svgEl(svg, tag, attrs) {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    svg.appendChild(e);
    return e;
  }
  function drawable(el) {
    const L = el.getTotalLength();
    el.style.strokeDasharray = L + " " + (L + 10);
    el.style.strokeDashoffset = L;
    return L;
  }
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  function cue(S, key, fb) {
    const c = T.cues[String(S.index)];
    return c && c[key] !== undefined ? c[key] : fb;
  }
  function lineT(S, li, which) {
    const l = T.lines.find((x) => x.scene === S.index && x.line === li);
    return l ? l[which || "start"] : S.first;
  }
  function hexA(hex, a) {
    const h = hex.replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  // brillo activo de una lista de tarjetas: la i-ésima se ilumina de times[i] a times[i+1]
  function activate(glows, times, endT) {
    glows.forEach((g, i) => {
      if (!g) return;
      const on = times[i];
      const off = i + 1 < times.length ? times[i + 1] : endT;
      tl.to(g, { opacity: 1, duration: 0.35, ease: "power2.out" }, on + 0.15);
      if (off > on + 0.5) tl.to(g, { opacity: 0, duration: 0.5, ease: "power2.inOut" }, off);
    });
  }
  // puntos de datos que viajan por un trazado SVG
  function flowDots(svg, path, tStart, tEnd, n, speed, size) {
    const L = path.getTotalLength();
    const dots = [];
    for (let i = 0; i < n; i++) dots.push(svgEl(svg, "circle", { r: size || 5, fill: "#fff", opacity: 0 }));
    every.push((t) => {
      const vis = t >= tStart && t <= tEnd;
      dots.forEach((d, i) => {
        if (!vis) { d.setAttribute("opacity", 0); return; }
        const u = (((t - tStart) * speed) / L + i / n) % 1;
        const p = path.getPointAtLength(u * L);
        d.setAttribute("cx", p.x); d.setAttribute("cy", p.y);
        const fadeIn = clamp((t - tStart) / 0.4, 0, 1);
        d.setAttribute("opacity", (0.9 * Math.sin(Math.PI * u) * fadeIn).toFixed(3));
      });
    });
  }
  function pulseRing(parent, x, y, size, tOn, tOff) {
    const r = mk("div", "abs", parent);
    place(r, x - size / 2, y - size / 2, size, size);
    r.style.borderRadius = "50%"; r.style.border = `2px solid ${V.accent}`;
    every.push((t) => {
      if (t < tOn || t > tOff) { r.style.opacity = 0; return; }
      const ph = ((t - tOn) % 1.6) / 1.6;
      r.style.opacity = ((1 - ph) * 0.8).toFixed(3);
      r.style.transform = `scale(${1 + ph * 0.55})`;
    });
    return r;
  }

  // ───────────────────────────── escena base, cabecera y transiciones
  function sceneRoot(S) {
    const r = mk("div", "scene", stage);
    tl.set(r, { autoAlpha: 1 }, S.start);
    if (S.index < T.scenes.length - 1) {
      tl.to(r, { autoAlpha: 0, y: -28, scale: 0.985, duration: 0.45, ease: "power2.in" }, S.end - 0.28);
    }
    return r;
  }
  function header(r, S, kicker, title) {
    const k = mk("div", "kicker", r, `<span class="dot"></span><span>${esc(kicker)}</span>`);
    const t = mk("div", "title", r);
    const words = splitWords(t, title);
    fitWidth(t, 1680, 66, 44);
    tl.from(k, { x: -40, autoAlpha: 0, duration: 0.6 }, S.start + 0.1);
    tl.from(words, { yPercent: 115, duration: 0.75, stagger: 0.045, ease: "power4.out" }, S.start + 0.16);
    return { k, t };
  }

  // ───────────────────────────── plantillas
  const B = {};

  B.intro = function (sc, S) {
    const r = sceneRoot(S);
    const mod = mk("div", "intro-mod", r, esc(V.module));
    const hero = mk("div", "intro-hero", r);
    hero.style.top = "400px";
    const rings = [[250, "1.5px solid " + hexA(V.accent, 0.35)], [300, "2px dashed " + hexA(V.accent2, 0.35)], [360, "1px solid rgba(255,255,255,.10)"]]
      .map(([rad, border]) => {
        const g = mk("div", "intro-ring", hero);
        place(g, -rad, -rad, rad * 2, rad * 2);
        g.style.border = border;
        return g;
      });
    const halo = mk("div", "abs", hero);
    place(halo, -330, -330, 660, 660);
    halo.style.borderRadius = "50%";
    halo.style.background = `radial-gradient(circle, ${hexA(V.accent, 0.28)}, ${hexA(V.accent2, 0.10)} 45%, transparent 70%)`;
    const glowTxt = mk("div", "intro-num", hero, "UT" + esc(V.num));
    glowTxt.style.color = V.accent; glowTxt.style.filter = "blur(34px)"; glowTxt.style.opacity = "0.55";
    const num = mk("div", "intro-num", hero, "UT" + esc(V.num));
    num.style.backgroundImage = `linear-gradient(100deg, ${V.accent} 0%, #ffffff 45%, ${V.accent2} 55%, ${V.accent} 100%)`;
    num.style.backgroundSize = "250% 100%";
    num.style.webkitBackgroundClip = "text"; num.style.backgroundClip = "text"; num.style.color = "transparent";
    const orb = mk("div", "abs", hero);
    const oc = icirc(V.icon, 96, orb);
    place(orb, -48, -48, 96, 96);
    const title = mk("div", "intro-title", r);
    const words = splitWords(title, V.title);
    title.style.top = "668px";
    const chip = mk("div", "intro-chip", r);
    const c = mk("div", "chip", chip, `${svgIcon("timer")}<span>Resumen en 2 minutos</span>`);
    c.querySelector("svg").classList.add("ico");
    c.querySelector("svg").style.cssText = `width:28px;height:28px;stroke:${V.accent};stroke-width:2.2`;

    tl.from(mod, { autoAlpha: 0, letterSpacing: "0.7em", duration: 1.4, ease: "power2.out" }, 0.25);
    tl.from(halo, { scale: 0.3, autoAlpha: 0, duration: 1.3, ease: "power2.out" }, 0.1);
    tl.from(rings, { scale: 0.55, autoAlpha: 0, duration: 1.1, stagger: 0.12, ease: "expo.out" }, 0.2);
    tl.from([num, glowTxt], { scale: 1.35, autoAlpha: 0, duration: 1.0, ease: "expo.out" }, 0.3);
    tl.from(num, { clipPath: "inset(0% 100% 0% 0%)", duration: 0.9, ease: "power3.inOut" }, 0.3);
    tl.from(orb, { scale: 0, autoAlpha: 0, duration: 0.7, ease: "back.out(2)" }, 1.0);
    tl.from(words, { yPercent: 115, duration: 0.8, stagger: 0.07, ease: "power4.out" }, 0.9);
    tl.from(c, { y: 30, autoAlpha: 0, scale: 0.9, duration: 0.6, ease: "back.out(1.7)" }, 1.8);
    bursts.push({ t: 0.35, x: 960, y: 400, n: 90, spread: 620 });
    every.push((t) => {
      if (t > S.end + 1) return;
      rings[1].style.transform = `rotate(${t * 14}deg)`;
      rings[2].style.transform = `rotate(${-t * 6}deg)`;
      const a = -1.2 + t * 0.5;
      orb.style.left = (Math.cos(a) * 330 - 48) + "px";
      orb.style.top = (Math.sin(a) * 190 - 48) + "px";
      num.style.backgroundPosition = `${(100 - ((t * 22) % 250))}% 0`;
    });
  };

  B.timeline = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const N = sc.items.length;
    const x0 = N >= 5 ? 250 : 300, x1 = W - x0, y = 590;
    const xs = sc.items.map((_, i) => (N === 1 ? 960 : x0 + ((x1 - x0) * i) / (N - 1)));
    const svg = svgLayer(r);
    svgEl(svg, "line", { x1: 120, y1: y, x2: 1800, y2: y, stroke: "rgba(255,255,255,.12)", "stroke-width": 4, "stroke-linecap": "round" });
    const prog = svgEl(svg, "path", { d: `M120 ${y} L1800 ${y}`, stroke: `url(#${svg._gid})`, "stroke-width": 6, "stroke-linecap": "round", fill: "none" });
    const L = drawable(prog);
    const colW = Math.min(380, (x1 - x0) / Math.max(1, N - 1) - 16);
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 0.6 + i * 1.4));
    const glows = [];
    sc.items.forEach((it, i) => {
      const t = times[i];
      const node = mk("div", "tl-node", r);
      place(node, xs[i], y);
      const c = icirc(it.icon, 118, node);
      const g = mk("div", "abs", node);
      place(g, -8, -8, 134, 134);
      g.style.borderRadius = "50%"; g.style.border = `3px solid ${V.accent}`; g.style.boxShadow = `0 0 40px ${hexA(V.accent, 0.6)}`; g.style.opacity = 0;
      glows.push(g);
      const tag = mk("div", "tl-tag", r, esc(it.tag)); place(tag, xs[i] - colW / 2, y - 196, colW);
      const year = mk("div", "tl-year grad", r, esc(it.year)); place(year, xs[i] - colW / 2, y - 160, colW);
      const txt = mk("div", "tl-text", r); place(txt, xs[i] - colW / 2, y + 88, colW);
      mk("div", "lbl", txt, rich(it.label));
      mk("div", "desc", txt, rich(it.desc));
      tl.to(prog, { strokeDashoffset: L - (xs[i] - 120), duration: 0.7, ease: "power2.inOut" }, t - 0.35);
      tl.from(node, { scale: 0, autoAlpha: 0, duration: 0.65, ease: "back.out(1.8)" }, t);
      tl.from([tag, year], { y: 34, autoAlpha: 0, duration: 0.55, stagger: 0.07 }, t + 0.08);
      tl.from(txt, { y: -24, autoAlpha: 0, duration: 0.6 }, t + 0.16);
      const off = i + 1 < N ? times[i + 1] : S.end;
      pulseRing(r, xs[i], y, 124, t + 0.4, off);
    });
    tl.to(prog, { strokeDashoffset: 0, duration: 1.2, ease: "power2.inOut" }, times[N - 1] + 0.6);
    activate(glows, times, S.end);
    // chispa que recorre la línea
    const spark = svgEl(svg, "circle", { r: 7, fill: "#fff", opacity: 0 });
    spark.style.filter = `drop-shadow(0 0 10px ${V.accent})`;
    every.push((t) => {
      if (t < times[0] || t > S.end) { spark.setAttribute("opacity", 0); return; }
      const prog1 = (L - parseFloat(prog.style.strokeDashoffset || L)) / L;
      const u = ((t - times[0]) * 0.45) % 1;
      spark.setAttribute("cx", 120 + u * prog1 * 1680);
      spark.setAttribute("cy", y);
      spark.setAttribute("opacity", (Math.sin(Math.PI * u) * 0.95).toFixed(3));
    });
    if (sc.footer) {
      const f = mk("div", "pill", r, `${svgIcon("quote")}<span>${rich(sc.footer)}</span>`);
      f.querySelector("svg").setAttribute("class", "ico");
      f.querySelector("svg").style.cssText = `width:40px;height:40px;stroke:${V.accent};stroke-width:2;flex:none`;
      f.style.fontStyle = "italic"; f.style.fontSize = "32px";
      f.style.left = "50%"; f.style.top = "880px"; f.style.transform = "translateX(-50%)"; f.style.whiteSpace = "nowrap";
      tl.from(f, { y: 40, autoAlpha: 0, duration: 0.7, ease: "back.out(1.5)" }, cue(S, "f", times[N - 1] + 2));
    }
  };

  B.grid = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    let top = sc.chips || sc.banner ? 350 : 380;
    if (sc.lead) {
      const l = mk("div", "lead", r, rich(sc.lead));
      l.style.top = "268px";
      tl.from(l, { autoAlpha: 0, y: 20, duration: 0.7 }, Math.max(S.start + 0.4, cue(S, "d", S.start + 0.6) - 0.1));
      top = 370;
    }
    const N = sc.items.length, cols = sc.cols || Math.min(N, 4), rows = Math.ceil(N / cols);
    const gap = cols >= 5 ? 24 : 32;
    const cw = (1680 - gap * (cols - 1)) / cols;
    const bottom = sc.chips || sc.banner ? 812 : 950;
    const ch = Math.min(rows === 1 ? 440 : 250, (bottom - top - gap * (rows - 1)) / rows);
    const horizontal = rows > 1;
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 0.5 + i * 0.9));
    const glows = [];
    sc.items.forEach((it, i) => {
      const cx = 120 + (i % cols) * (cw + gap), cy = top + Math.floor(i / cols) * (ch + gap);
      const card = mk("div", "card", r); place(card, cx, cy, cw, ch);
      glows.push(mk("div", "glow", card));
      const inner = mk("div", "", card);
      inner.style.cssText = horizontal
        ? "position:absolute;inset:0;display:flex;align-items:center;gap:30px;padding:0 38px"
        : `position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;text-align:center;padding:${Math.max(34, (ch - 330) / 2)}px 26px 30px;gap:26px`;
      const c = icirc(it.icon, horizontal ? 104 : cols >= 5 ? 116 : 128, inner);
      const txt = mk("div", "", inner);
      const lb = mk("div", "lbl", txt, rich(it.label));
      lb.style.fontSize = (cols >= 5 ? 29 : 33) + "px";
      const ds = mk("div", "desc", txt, rich(it.desc));
      ds.style.fontSize = (cols >= 5 ? 23 : 25) + "px"; ds.style.marginTop = "12px";
      const t = times[i];
      tl.from(card, { y: 70, autoAlpha: 0, scale: 0.93, duration: 0.75, ease: "back.out(1.4)" }, t);
      tl.from(c, { scale: 0, rotation: -40, duration: 0.7, ease: "back.out(2.2)" }, t + 0.12);
      every.push((tt) => {
        const on = tt >= t + 0.6 && tt < (i + 1 < N ? times[i + 1] : S.end);
        const k = on ? 1 + 0.045 * Math.sin((tt - t) * 5) : 1;
        c.style.transform = on ? `scale(${k.toFixed(4)})` : "";
      });
    });
    const endAct = sc.chips ? cue(S, "c0", S.end) : sc.banner ? cue(S, "x", S.end) : S.end;
    activate(glows, times, endAct);
    if (sc.chips) {
      const row = mk("div", "abs", r);
      row.style.cssText = "left:120px;right:120px;top:858px;display:flex;justify-content:center;gap:24px";
      sc.chips.forEach((txt, i) => {
        const c = mk("div", "chip", row, `${svgIcon("circle-check")}<span>${rich(txt)}</span>`);
        const s = c.querySelector("svg"); s.style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.2;flex:none`;
        tl.from(c, { y: 30, autoAlpha: 0, scale: 0.85, duration: 0.55, ease: "back.out(2)" }, cue(S, "c" + i, times[N - 1] + 1 + i * 0.5));
      });
    }
    if (sc.banner) {
      const b = mk("div", "pill", r, `${svgIcon(sc.banner.icon)}<span>${rich(sc.banner.text)}</span>`);
      b.querySelector("svg").style.cssText = `width:40px;height:40px;stroke:${V.accent};stroke-width:2;flex:none`;
      b.style.left = "50%"; b.style.top = "858px"; b.style.transform = "translateX(-50%)"; b.style.whiteSpace = "nowrap";
      tl.from(b, { y: 40, autoAlpha: 0, duration: 0.7, ease: "back.out(1.5)" }, cue(S, "x", times[N - 1] + 2));
    }
  };

  B.flow = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const N = sc.items.length;
    const cw = N === 3 ? 470 : 340;
    const gapX = (1680 - N * cw) / (N - 1);
    const top = sc.prompt ? 340 : sc.note ? 372 : 430, ch = sc.prompt ? 300 : 340;
    const ymid = top + ch / 2;
    const svg = svgLayer(r);
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 0.5 + i * 1.5));
    const glows = [];
    sc.items.forEach((it, i) => {
      const x = 120 + i * (cw + gapX);
      const card = mk("div", "card", r); place(card, x, top, cw, ch);
      glows.push(mk("div", "glow", card));
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:26px 30px;gap:22px";
      const c = icirc(it.icon, 116, inner);
      const txt = mk("div", "", inner);
      const lb = mk("div", "lbl", txt, rich(it.label)); lb.style.fontSize = "34px";
      const ds = mk("div", "desc", txt, rich(it.desc)); ds.style.fontSize = "25px"; ds.style.marginTop = "10px";
      if (sc.numbered) {
        const nb = mk("div", "abs mont", card, String(i + 1));
        nb.style.cssText += `left:22px;top:18px;font-weight:900;font-size:64px;line-height:1;color:${hexA(V.accent, 0.22)}`;
      }
      const t = times[i];
      tl.from(card, { x: -50, autoAlpha: 0, duration: 0.75, ease: "power3.out" }, t);
      tl.from(c, { scale: 0, rotation: 60, duration: 0.7, ease: "back.out(2)" }, t + 0.1);
      if (i > 0) {
        const xa = 120 + (i - 1) * (cw + gapX) + cw + 14, xb = x - 14;
        const p = svgEl(svg, "path", { d: `M${xa} ${ymid} L${xb - 8} ${ymid}`, stroke: `url(#${svg._gid})`, "stroke-width": 5, fill: "none", "stroke-linecap": "round" });
        const head = svgEl(svg, "path", { d: `M${xb - 20} ${ymid - 13} L${xb - 2} ${ymid} L${xb - 20} ${ymid + 13}`, stroke: V.accent2, "stroke-width": 5, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" });
        const L = drawable(p);
        tl.to(p, { strokeDashoffset: 0, duration: 0.45, ease: "power2.inOut" }, t - 0.3);
        tl.from(head, { autoAlpha: 0, duration: 0.2 }, t + 0.1);
        flowDots(svg, p, t + 0.2, S.end, 3, 90, 4.5);
      }
    });
    activate(glows, times, S.end);
    if (sc.note) {
      const n = mk("div", "pill", r, `${svgIcon("lightbulb")}<span>${rich(sc.note)}</span>`);
      n.querySelector("svg").style.cssText = `width:40px;height:40px;stroke:${V.accent};stroke-width:2;flex:none`;
      n.style.left = "50%"; n.style.top = "790px"; n.style.transform = "translateX(-50%)"; n.style.whiteSpace = "nowrap"; n.style.fontSize = "28px";
      tl.from(n, { y: 40, autoAlpha: 0, duration: 0.7, ease: "back.out(1.5)" }, Math.min(times[Math.max(0, N - 2)] + 1.3, S.end - 3.5));
    }
    if (sc.prompt) {
      const icons = { Texto: "type", Imagen: "image", Audio: "mic", "Vídeo": "video", Sensores: "activity" };
      const row = mk("div", "abs", r);
      row.style.cssText = "left:120px;right:120px;top:700px;display:flex;justify-content:center;gap:26px";
      const tp = cue(S, "p", times[N - 1] + 1.5), tm = cue(S, "m", tp + 3);
      const chips = sc.prompt.chips.map((txt, i) => {
        const c = mk("div", "chip", row, `${svgIcon(icons[txt] || "circle")}<span>${esc(txt)}</span>`);
        c.querySelector("svg").style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.2;flex:none`;
        tl.from(c, { y: 26, autoAlpha: 0, scale: 0.8, duration: 0.5, ease: "back.out(2)" }, tp + 0.7 + i * 0.32);
        return c;
      });
      const badge = mk("div", "pill", r, `${svgIcon("sparkles")}<span>${esc(sc.prompt.label)}</span>`);
      badge.querySelector("svg").style.cssText = `width:40px;height:40px;stroke:${V.accent};stroke-width:2;flex:none`;
      badge.style.left = "50%"; badge.style.top = "880px"; badge.style.transform = "translateX(-50%)"; badge.style.fontSize = "32px"; badge.style.fontFamily = "Montserrat"; badge.style.fontWeight = "800";
      // líneas que convergen en el prompt multimodal (se calculan tras el layout)
      const links = [];
      requestAnimationFrame(() => {});
      chips.forEach((c) => {
        const p = svgEl(svg, "path", { d: "M0 0", stroke: hexA(V.accent, 0.7), "stroke-width": 3, fill: "none" });
        links.push([c, p]);
      });
      window.__post = window.__post || [];
      window.__post.push(() => {
        links.forEach(([c, p]) => {
          const b = c.getBoundingClientRect();
          const x = b.left + b.width / 2, y0 = b.bottom + 4;
          p.setAttribute("d", `M${x} ${y0} C ${x} ${y0 + 40}, 960 ${860 - 40}, 960 878`);
          drawable(p);
          tl.to(p, { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut" }, tm - 0.2);
          flowDots(svg, p, tm + 0.4, S.end, 2, 110, 4);
        });
      });
      tl.from(badge, { y: 30, autoAlpha: 0, scale: 0.8, duration: 0.7, ease: "back.out(2)" }, tm + 0.3);
    }
  };

  B.quote = function (sc, S) {
    const r = sceneRoot(S);
    const k = mk("div", "kicker", r, `<span class="dot"></span><span>${esc(sc.kicker)}</span>`);
    tl.from(k, { x: -40, autoAlpha: 0, duration: 0.6 }, S.start + 0.1);
    const qi = ico("quote", "abs", r);
    place(qi, 920, 250, 80, 80);
    qi.querySelector("svg").style.cssText = `stroke:${V.accent};stroke-width:1.6`;
    const q = mk("div", "abs mont", r);
    q.style.cssText += "left:120px;width:1680px;top:352px;text-align:center;font-weight:800;line-height:1.1;white-space:nowrap";
    const words = splitWords(q, sc.quote);
    fitWidth(q, 1680, 84, 50);
    const l0s = lineT(S, 0, "start"), l0e = lineT(S, 0, "end");
    tl.from(qi, { scale: 0, autoAlpha: 0, duration: 0.6, ease: "back.out(2)" }, S.start + 0.15);
    tl.from(words, { yPercent: 115, autoAlpha: 0, duration: 0.6, stagger: (l0e - l0s) / words.length * 0.8, ease: "power4.out" }, l0s - 0.1);
    // subrayado brillante
    const u = mk("div", "abs", r);
    place(u, 560, 470, 800, 8); u.style.borderRadius = "8px"; u.style.background = `linear-gradient(90deg, ${V.accent}, ${V.accent2})`; u.style.boxShadow = `0 0 24px ${hexA(V.accent, .7)}`;
    tl.from(u, { scaleX: 0, transformOrigin: "left center", duration: 0.8, ease: "power3.inOut" }, l0e - 0.2);
    // ecuación: proceso complicado + tecnología = complicado… y digital
    const l1 = lineT(S, 1, "start"), l1e = lineT(S, 1, "end");
    const eq = mk("div", "abs", r);
    eq.style.cssText = "left:120px;right:120px;top:540px;display:flex;justify-content:center;align-items:center;gap:22px";
    const parts = [
      mk("div", "chip", eq, `${svgIcon("shuffle")}<span>Proceso complicado</span>`),
      mk("div", "mont", eq, "+"),
      mk("div", "chip", eq, `${svgIcon("cpu")}<span>Tecnología</span>`),
      mk("div", "mont", eq, "="),
      mk("div", "chip", eq, `${svgIcon("triangle-alert")}<span>Complicado… y digital</span>`),
    ];
    parts.forEach((p) => { const s = p.querySelector("svg"); if (s) s.style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.2;flex:none`; });
    [parts[1], parts[3]].forEach((p) => { p.style.fontSize = "44px"; p.style.fontWeight = "800"; p.style.color = V.accent; });
    parts[4].style.borderColor = hexA("#FB7185", 0.7); parts[4].style.background = hexA("#FB7185", 0.12);
    parts[4].querySelector("svg").style.stroke = "#FB7185";
    const span = (l1e - l1) * 0.8;
    parts.forEach((p, i) => tl.from(p, { y: 30, autoAlpha: 0, scale: 0.85, duration: 0.5, ease: "back.out(2)" }, l1 + (i * span) / parts.length));
    // término
    const tt = cue(S, "t", lineT(S, 2, "start"));
    const card = mk("div", "card", r); place(card, 260, 680, 1400, 250);
    const inner = mk("div", "", card);
    inner.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;gap:44px;padding:0 56px";
    const c = icirc(sc.icon, 150, inner);
    const txt = mk("div", "", inner);
    const term = mk("div", "mont grad", txt, esc(sc.term)); term.style.cssText += "font-weight:900;font-size:58px;line-height:1.05;text-transform:uppercase;letter-spacing:.02em";
    const def = mk("div", "desc", txt, rich(sc.definition)); def.style.cssText += "font-size:31px;margin-top:14px;color:#D6E0F5";
    tl.from(card, { y: 60, autoAlpha: 0, duration: 0.8, ease: "back.out(1.3)" }, tt - 0.1);
    tl.from(c, { scale: 0, rotation: -90, duration: 0.8, ease: "back.out(2)" }, tt + 0.1);
    every.push((t) => {
      if (t < tt + 0.8 || t > S.end) { c.style.transform = ""; return; }
      c.style.transform = `rotate(${Math.sin((t - tt) * 2.2) * 8}deg)`;
    });
  };

  B.cycle = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const cx = 640, cy = 642, R = 205;
    const svg = svgLayer(r);
    const angs = [-90, 0, 90, 180];
    const pos = angs.map((a) => [cx + R * Math.cos((a * Math.PI) / 180), cy + R * Math.sin((a * Math.PI) / 180)]);
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 1 + i * 0.9));
    // centro
    const ring = svgEl(svg, "circle", { cx, cy, r: 92, fill: "none", stroke: hexA(V.accent, 0.55), "stroke-width": 2, "stroke-dasharray": "10 12" });
    const ringOuter = svgEl(svg, "circle", { cx, cy, r: R, fill: "none", stroke: "rgba(255,255,255,.07)", "stroke-width": 2 });
    const center = mk("div", "abs mont grad", r, esc(sc.center));
    center.style.cssText += `left:${cx - 120}px;top:${cy - 40}px;width:240px;text-align:center;font-weight:900;font-size:66px;line-height:80px`;
    tl.from([ring, ringOuter], { autoAlpha: 0, duration: 0.8 }, S.start + 0.3);
    tl.from(center, { scale: 0.4, autoAlpha: 0, duration: 0.8, ease: "back.out(1.8)" }, S.start + 0.4);
    every.push((t) => { ring.setAttribute("transform", `rotate(${t * 30} ${cx} ${cy})`); });
    const glows = [];
    sc.items.forEach((it, i) => {
      const [x, y] = pos[i];
      const node = mk("div", "abs", r); place(node, x - 62, y - 62, 124, 124);
      const c = icirc(it.icon, 124, node);
      const g = mk("div", "abs", node); place(g, -8, -8, 140, 140);
      g.style.borderRadius = "50%"; g.style.border = `3px solid ${V.accent}`; g.style.boxShadow = `0 0 40px ${hexA(V.accent, 0.6)}`; g.style.opacity = 0;
      glows.push(g);
      const lab = mk("div", "abs", r);
      const right = i === 1;
      // etiquetas hacia fuera del círculo: arriba, derecha, abajo, izquierda
      const LW = i === 0 || i === 2 ? 340 : 250;
      const lx = i === 0 || i === 2 ? x - LW / 2 : i === 1 ? x + 84 : x - 84 - LW;
      const ly = i === 0 ? y - 176 : i === 2 ? y + 72 : y - 44;
      place(lab, lx, ly, LW);
      lab.style.textAlign = i === 0 || i === 2 ? "center" : right ? "left" : "right";
      const num = mk("div", "mont", lab, String(i + 1).padStart(2, "0")); num.style.cssText += `font-weight:800;font-size:20px;color:${V.accent};letter-spacing:.1em`;
      const lb = mk("div", "lbl", lab, rich(it.label)); lb.style.fontSize = "32px";
      const ds = mk("div", "desc", lab, rich(it.desc)); ds.style.fontSize = "22px"; ds.style.marginTop = "4px";
      const t = times[i];
      tl.from(node, { scale: 0, autoAlpha: 0, duration: 0.6, ease: "back.out(2)" }, t);
      tl.from(lab, { x: i === 1 ? -20 : i === 3 ? 20 : 0, y: i === 0 ? 20 : i === 2 ? -20 : 0, autoAlpha: 0, duration: 0.5 }, t + 0.1);
      // arco hacia el siguiente nodo
      const a0 = ((angs[i] + 19) * Math.PI) / 180, a1 = ((angs[(i + 1) % 4] + (i === 3 ? 360 : 0) - 19) * Math.PI) / 180;
      const p0 = [cx + R * Math.cos(a0), cy + R * Math.sin(a0)], p1 = [cx + R * Math.cos(a1), cy + R * Math.sin(a1)];
      const arc = svgEl(svg, "path", { d: `M${p0[0]} ${p0[1]} A ${R} ${R} 0 0 1 ${p1[0]} ${p1[1]}`, stroke: `url(#${svg._gid})`, "stroke-width": 5, fill: "none", "stroke-linecap": "round" });
      drawable(arc);
      const ah = ((angs[(i + 1) % 4] - 19) * Math.PI) / 180;
      const tx = -Math.sin(ah), ty = Math.cos(ah);  // tangente
      const hx = p1[0], hy = p1[1];
      const nx = Math.cos(ah), ny = Math.sin(ah);
      const head = svgEl(svg, "path", { d: `M${hx - tx * 16 + nx * 11} ${hy - ty * 16 + ny * 11} L${hx} ${hy} L${hx - tx * 16 - nx * 11} ${hy - ty * 16 - ny * 11}`, stroke: V.accent2, "stroke-width": 5, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" });
      const tArc = i < 3 ? times[i + 1] - 0.4 : times[3] + 0.8;
      tl.to(arc, { strokeDashoffset: 0, duration: 0.5, ease: "power2.inOut" }, tArc);
      tl.from(head, { autoAlpha: 0, duration: 0.15 }, tArc + 0.4);
    });
    activate(glows, times, times[3] + 1.4);
    // pulso que recorre el ciclo cuando está completo
    const pulse = svgEl(svg, "circle", { r: 9, fill: "#fff", opacity: 0 });
    pulse.style.filter = `drop-shadow(0 0 12px ${V.accent})`;
    const tLoop = times[3] + 1.3;
    every.push((t) => {
      if (t < tLoop || t > S.end) { pulse.setAttribute("opacity", 0); return; }
      const a = (-90 + ((t - tLoop) * 120) % 360) * Math.PI / 180;
      pulse.setAttribute("cx", cx + R * Math.cos(a)); pulse.setAttribute("cy", cy + R * Math.sin(a));
      pulse.setAttribute("opacity", 0.95);
    });
    if (sc.parts) {
      const box = mk("div", "abs", r);
      box.style.cssText += "left:1220px;top:420px;width:560px;display:flex;flex-direction:column;align-items:flex-start;gap:18px";
      const pIcons = ["cpu", "code", "wifi"];
      const l0 = lineT(S, 0, "start"), l0e = lineT(S, 0, "end");
      sc.parts.forEach((txt, i) => {
        if (i > 0) { const plus = mk("div", "mont", box, "+"); plus.style.cssText += `font-size:40px;font-weight:800;color:${V.accent};margin-left:34px;line-height:1`; tl.from(plus, { autoAlpha: 0, duration: 0.3 }, l0 + (l0e - l0) * (0.55 + i * 0.12) - 0.1); }
        const c = mk("div", "chip", box, `${svgIcon(pIcons[i] || "circle")}<span>${esc(txt)}</span>`);
        c.style.fontSize = "34px"; c.style.padding = "18px 30px";
        c.querySelector("svg").style.cssText = `width:36px;height:36px;stroke:${V.accent};stroke-width:2.2;flex:none`;
        tl.from(c, { x: 40, autoAlpha: 0, duration: 0.5, ease: "back.out(1.8)" }, l0 + (l0e - l0) * (0.55 + i * 0.12));
      });
      tl.to(box, { autoAlpha: 0, x: 40, duration: 0.5, ease: "power2.in" }, times[0] - 0.3);
    }
    if (sc.extra) {
      const tx = cue(S, "x", times[3] + 2);
      const card = mk("div", "card", r); place(card, 1200, 400, 600, 470);
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:44px 50px;gap:22px";
      const top = mk("div", "", inner); top.style.cssText = "display:flex;align-items:center;gap:26px";
      const c = icirc(sc.extra.icon, 104, top);
      const h = mk("div", "lbl", top, esc(sc.extra.title)); h.style.fontSize = "46px";
      const p = mk("div", "desc", inner, rich(sc.extra.text)); p.style.fontSize = "30px"; p.style.color = "#D6E0F5";
      const g = mk("div", "glow", card);
      tl.from(card, { x: 80, autoAlpha: 0, duration: 0.8, ease: "power3.out" }, tx - 0.1);
      tl.from(c, { scale: 0, duration: 0.6, ease: "back.out(2)" }, tx + 0.2);
      tl.to(g, { opacity: 1, duration: 0.5 }, tx + 0.4);
      // "gemelo": copia fantasma del ciclo
      const ghost = svgEl(svg, "circle", { cx: 1475, cy: 390, r: 0, fill: "none", stroke: hexA(V.accent, .3), "stroke-width": 2 });
    }
  };

  B.compare = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const mode = sc.mode || "versus";
    const tL = cue(S, "L", S.first + 0.3), tR = cue(S, "R", tL + 2.5);
    const hasFooter = !!sc.footer;
    const cwid = mode === "merge" ? 620 : 790;
    const nItems = Math.max((sc.left.items || []).length, (sc.right.items || []).length);
    const chgt = mode === "merge" ? 330 : mode === "chips" ? 520 : Math.min(hasFooter ? 500 : 560, 250 + nItems * 66);
    const areaTop = 330, areaBot = hasFooter ? 860 : mode === "merge" ? 740 : 980;
    const top = Math.round(areaTop + Math.max(0, (areaBot - areaTop - chgt) / 2));
    const xs = [120, 1800 - cwid];
    const cards = [sc.left, sc.right].map((side, k) => {
      const card = mk("div", "card", r); place(card, xs[k], top, cwid, chgt);
      const g = mk("div", "glow", card);
      const inner = mk("div", "", card);
      if (mode === "merge") {
        inner.style.cssText = "position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:10px;padding:30px";
        const top2 = mk("div", "", inner); top2.style.cssText = "display:flex;align-items:center;gap:26px";
        const c = icirc(side.icon, 96, top2);
        const ab = mk("div", "mont grad", top2, esc(side.abbr)); ab.style.cssText += "font-weight:900;font-size:110px;line-height:1";
        const lb = mk("div", "lbl", inner, rich(side.label)); lb.style.fontSize = "34px"; lb.style.marginTop = "16px";
        const ds = mk("div", "desc", inner, rich(side.desc)); ds.style.fontSize = "27px";
      } else {
        inner.style.cssText = "position:absolute;inset:0;padding:40px 46px;display:flex;flex-direction:column;gap:22px";
        const hd = mk("div", "", inner); hd.style.cssText = "display:flex;align-items:center;gap:24px";
        const tone = side.tone === "warn" ? "#FB7185" : side.tone === "good" ? "#34D399" : null;
        const c = icirc(side.icon, 96, hd);
        if (tone) { c.style.background = `radial-gradient(circle at 32% 28%, ${hexA(tone, .5)}, ${hexA(tone, .15)} 70%)`; c.style.borderColor = hexA(tone, .75); c.style.boxShadow = `0 0 30px ${hexA(tone, .3)}`; }
        const hh = mk("div", "", hd);
        const lb = mk("div", "lbl", hh, rich(side.label)); lb.style.fontSize = "37px";
        if (side.desc) { const ds = mk("div", "desc", hh, rich(side.desc)); ds.style.fontSize = "25px"; ds.style.marginTop = "6px"; }
        const sep = mk("div", "", inner); sep.style.cssText = "height:1px;background:rgba(255,255,255,.12);margin:4px 0 6px";
        if (mode === "chips") {
          const wrap = mk("div", "", inner); wrap.style.cssText = "display:flex;flex-wrap:wrap;gap:16px";
          side._items = side.items.map((it) => {
            const cp = mk("div", "chip", wrap, `${svgIcon(k === 0 ? "lock" : "sparkles")}<span>${rich(it)}</span>`);
            cp.style.fontSize = "25px";
            cp.querySelector("svg").style.cssText = `width:26px;height:26px;stroke:${V.accent};stroke-width:2.2;flex:none`;
            return cp;
          });
        } else {
          side._items = side.items.map((it) => {
            const row = mk("div", "row", inner);
            const kind = tone === "#FB7185" ? "warn" : tone === "#34D399" ? "good" : "acc";
            const m = mk("div", "mk " + kind, row, svgIcon(kind === "warn" ? "minus" : kind === "good" ? "plus" : "check"));
            mk("div", "", row, rich(it));
            return row;
          });
        }
      }
      card._glow = g;
      return card;
    });
    [tL, tR].forEach((t, k) => {
      const card = cards[k];
      tl.from(card, { x: k === 0 ? -80 : 80, autoAlpha: 0, duration: 0.8, ease: "power3.out" }, t);
      const side = k === 0 ? sc.left : sc.right;
      if (side._items) {
        const nxt = k === 0 ? tR : S.end - 1.5;
        const span = Math.min(0.55, Math.max(0.25, (nxt - t - 1.2) / side._items.length));
        tl.from(side._items, { x: 30, autoAlpha: 0, duration: 0.5, stagger: span }, t + 0.45);
      }
    });
    activate(cards.map((c) => c._glow), [tL, tR], mode === "merge" ? cue(S, "M", S.end) : S.end);
    if (mode === "versus" && sc.center) {
      const vs = mk("div", "abs mont", r, esc(sc.center));
      vs.style.cssText += `left:${960 - 62}px;top:${top + chgt / 2 - 62}px;width:124px;height:124px;border-radius:50%;display:grid;place-items:center;font-weight:900;font-size:42px;color:#061018;background:linear-gradient(135deg, ${V.accent}, ${V.accent2});box-shadow:0 0 50px ${hexA(V.accent, .55)}`;
      tl.from(vs, { scale: 0, rotation: -180, duration: 0.8, ease: "back.out(1.8)" }, tR - 0.2);
    }
    if (mode === "merge") {
      const tM = cue(S, "M", tR + 3);
      const svg = svgLayer(r);
      const yc = top + chgt / 2;
      const b = mk("div", "abs mont", r, esc(sc.center));
      b.style.cssText += `left:${960 - 115}px;top:${yc - 115}px;width:230px;height:230px;border-radius:50%;display:grid;place-items:center;text-align:center;font-weight:900;font-size:44px;line-height:1;color:#061018;background:radial-gradient(circle at 35% 30%, #fff, ${V.accent} 45%, ${V.accent2});box-shadow:0 0 70px ${hexA(V.accent, .7)}`;
      const beams = [[120 + cwid + 6, 960 - 118], [1800 - cwid - 6, 960 + 118]].map(([xa, xb]) => {
        const p = svgEl(svg, "path", { d: `M${xa} ${yc} L${xb} ${yc}`, stroke: `url(#${svg._gid})`, "stroke-width": 6, fill: "none", "stroke-linecap": "round" });
        drawable(p);
        tl.to(p, { strokeDashoffset: 0, duration: 0.5, ease: "power2.inOut" }, tM - 0.3);
        flowDots(svg, p, tM + 0.2, S.end, 3, 120, 5);
        return p;
      });
      tl.from(b, { scale: 0, autoAlpha: 0, duration: 0.8, ease: "back.out(1.9)" }, tM);
      pulseRing(r, 960, yc, 240, tM + 0.6, S.end);
      bursts.push({ t: tM + 0.1, x: 960, y: yc, n: 50, spread: 320 });
      const row = mk("div", "abs", r);
      row.style.cssText = "left:120px;right:120px;top:770px;display:flex;justify-content:center;gap:22px";
      sc.chips.forEach((txt, i) => {
        const c = mk("div", "chip", row, `${svgIcon(i === 3 ? "shield-check" : "circle-check")}<span>${rich(txt)}</span>`);
        c.querySelector("svg").style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.2;flex:none`;
        tl.from(c, { y: 30, autoAlpha: 0, scale: 0.85, duration: 0.55, ease: "back.out(2)" }, cue(S, "c" + i, tM + 1 + i * 0.6));
      });
    }
    if (sc.footer) {
      const f = mk("div", "pill", r, `${svgIcon("tag")}<span>${rich(sc.footer)}</span>`);
      f.querySelector("svg").style.cssText = `width:40px;height:40px;stroke:${V.accent};stroke-width:2;flex:none`;
      f.style.left = "50%"; f.style.top = "882px"; f.style.transform = "translateX(-50%)"; f.style.whiteSpace = "nowrap";
      tl.from(f, { y: 40, autoAlpha: 0, duration: 0.7, ease: "back.out(1.5)" }, cue(S, "f", tR + 3));
    }
  };

  B.definition = function (sc, S) {
    const r = sceneRoot(S);
    const k = mk("div", "kicker", r, `<span class="dot"></span><span>${esc(sc.kicker)}</span>`);
    tl.from(k, { x: -40, autoAlpha: 0, duration: 0.6 }, S.start + 0.1);
    // emblema
    const ex = 430, ey = 590;
    const halo = mk("div", "abs", r); place(halo, ex - 300, ey - 300, 600, 600);
    halo.style.borderRadius = "50%"; halo.style.background = `radial-gradient(circle, ${hexA(V.accent, .25)}, transparent 65%)`;
    const rings = [170, 215, 262].map((rad, i) => {
      const g = mk("div", "abs", r); place(g, ex - rad, ey - rad, rad * 2, rad * 2);
      g.style.borderRadius = "50%";
      g.style.border = i === 1 ? `2px dashed ${hexA(V.accent2, .5)}` : `1.5px solid ${hexA(V.accent, i === 0 ? .6 : .2)}`;
      return g;
    });
    const em = mk("div", "abs", r); place(em, ex - 130, ey - 130, 260, 260);
    const c = icirc(sc.icon, 260, em);
    c.querySelector("svg").style.strokeWidth = "1.4";
    tl.from(halo, { scale: 0.4, autoAlpha: 0, duration: 1 }, S.start + 0.2);
    tl.from(rings, { scale: 0.6, autoAlpha: 0, duration: 0.9, stagger: 0.1, ease: "expo.out" }, S.start + 0.25);
    tl.from(c, { scale: 0, rotation: -60, duration: 0.9, ease: "back.out(1.7)" }, S.start + 0.35);
    every.push((t) => {
      if (t < S.start || t > S.end + 0.5) return;
      rings[1].style.transform = `rotate(${t * 18}deg)`;
      rings[2].style.transform = `scale(${1 + 0.03 * Math.sin(t * 2)})`;
    });
    const ab = mk("div", "def-abbr", r, esc(sc.abbr));
    const term = mk("div", "def-term", r);
    const words = splitWords(term, sc.term);
    const text = mk("div", "def-text", r, rich(sc.text));
    // posición vertical según altura real (tras el layout)
    const tl0 = S.first;
    tl.from(ab, { y: 20, autoAlpha: 0, duration: 0.5 }, S.start + 0.3);
    tl.from(words, { yPercent: 115, duration: 0.75, stagger: 0.07, ease: "power4.out" }, S.start + 0.4);
    tl.from(text, { y: 30, autoAlpha: 0, duration: 0.8 }, tl0 + 0.6);
    const chipsBox = mk("div", "def-chips", r);
    const chips = sc.chips.map((txt, i) => {
      const cp = mk("div", "chip", chipsBox, `${svgIcon("circle-check")}<span>${rich(txt)}</span>`);
      cp.querySelector("svg").style.cssText = `width:28px;height:28px;stroke:${V.accent};stroke-width:2.2;flex:none`;
      cp.style.fontSize = "25px";
      tl.from(cp, { y: 26, autoAlpha: 0, scale: 0.85, duration: 0.5, ease: "back.out(2)" }, cue(S, "c" + i, tl0 + 3 + i * 0.6));
      return cp;
    });
    window.__post = window.__post || [];
    window.__post.push(() => {
      const th = term.getBoundingClientRect().height;
      const total = 50 + th + 30 + text.getBoundingClientRect().height + 40 + chipsBox.getBoundingClientRect().height;
      const y0 = Math.max(300, 590 - total / 2);
      ab.style.top = y0 + "px";
      term.style.top = (y0 + 56) + "px";
      text.style.top = (y0 + 56 + th + 26) + "px";
      chipsBox.style.top = (y0 + 56 + th + 26 + text.getBoundingClientRect().height + 42) + "px";
    });
  };

  B.stats = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    // reloj de "cada minuto"
    const clock = mk("div", "abs", r); place(clock, 1650, 110, 150, 196);
    clock.innerHTML = `<svg width="150" height="196" viewBox="0 0 150 196"><circle cx="75" cy="75" r="66" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="8"/>
      <circle class="arc" cx="75" cy="75" r="66" fill="none" stroke="${V.accent}" stroke-width="8" stroke-linecap="round" transform="rotate(-90 75 75)" stroke-dasharray="415 420" stroke-dashoffset="415"/>
      <line class="hand" x1="75" y1="75" x2="75" y2="32" stroke="#fff" stroke-width="5" stroke-linecap="round"/>
      <circle cx="75" cy="75" r="7" fill="#fff"/>
      <text x="75" y="186" text-anchor="middle" font-family="Montserrat" font-weight="800" font-size="24" fill="${V.accent}">60 s</text></svg>`;
    const arc = clock.querySelector(".arc"), hand = clock.querySelector(".hand");
    tl.from(clock, { scale: 0, autoAlpha: 0, duration: 0.7, ease: "back.out(2)" }, S.start + 0.4);
    every.push((t) => {
      if (t < S.start || t > S.end) return;
      const k = ((t - S.start) / 8) % 1;
      arc.setAttribute("stroke-dashoffset", (415 * (1 - k)).toFixed(1));
      hand.setAttribute("transform", `rotate(${k * 360} 75 75)`);
    });
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 1 + i * 1.5));
    const glows = [];
    sc.items.forEach((it, i) => {
      const x = 120 + (i % 2) * 860, y = 350 + Math.floor(i / 2) * 290;
      const card = mk("div", "card", r); place(card, x, y, 820, 260);
      glows.push(mk("div", "glow", card));
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;gap:40px;padding:0 50px";
      const c = icirc(it.icon, 128, inner);
      const txt = mk("div", "", inner);
      const num = mk("div", "mont grad", txt, "0"); num.style.cssText += "font-weight:900;font-size:104px;line-height:1;white-space:nowrap";
      const lb = mk("div", "desc", txt, rich(it.label)); lb.style.fontSize = "30px"; lb.style.color = "#D6E0F5"; lb.style.marginTop = "8px";
      const t = times[i];
      tl.from(card, { y: 60, autoAlpha: 0, scale: 0.94, duration: 0.7, ease: "back.out(1.4)" }, t);
      tl.from(c, { scale: 0, duration: 0.6, ease: "back.out(2)" }, t + 0.1);
      const o = { v: 0 };
      const fmt = (v) => v.toFixed(it.dec).replace(".", ",") + it.suffix;
      num.textContent = fmt(0);
      tl.to(o, { v: it.value, duration: 1.6, ease: "power2.out", onUpdate: () => { num.textContent = fmt(o.v); } }, t + 0.15);
    });
    activate(glows, times, S.end);
    if (sc.source) {
      const s = mk("div", "abs", r, esc(sc.source));
      s.style.cssText += "right:120px;top:950px;font-size:20px;color:var(--dim);font-style:italic";
      tl.from(s, { autoAlpha: 0, duration: 0.6 }, times[0] + 0.5);
    }
  };

  B.stack = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 1 + i * 3));
    const glows = [];
    const lw = 1330, lh = 158, gap = 26, top = 348;
    sc.items.forEach((it, i) => {
      const y = top + i * (lh + gap);
      const card = mk("div", "card", r); place(card, 120, y, lw, lh);
      glows.push(mk("div", "glow", card));
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;padding:0 44px;gap:40px";
      const left = mk("div", "", inner); left.style.width = "330px"; left.style.flex = "none";
      mk("div", "stack-abbr grad", left, esc(it.abbr));
      mk("div", "stack-name", left, esc(it.name));
      const c = icirc(it.icon, 96, inner);
      const mid = mk("div", "", inner); mid.style.flex = "1";
      const an = mk("div", "lbl", mid, rich(it.analogy)); an.style.fontSize = "33px";
      const ex = mk("div", "desc", mid, rich(it.examples)); ex.style.fontSize = "25px"; ex.style.marginTop = "8px";
      const t = times[i];
      tl.from(card, { x: 120, autoAlpha: 0, duration: 0.8, ease: "power3.out" }, t);
      tl.from(c, { scale: 0, rotation: -45, duration: 0.6, ease: "back.out(2)" }, t + 0.2);
    });
    activate(glows, times, S.end);
    // medidor lateral
    const mx = 1540, y0 = top + 10, y1 = top + 3 * lh + 2 * gap - 10;
    const svg = svgLayer(r);
    const bar = svgEl(svg, "path", { d: `M${mx} ${y0 + 20} L${mx} ${y1 - 20}`, stroke: `url(#${svg._gid})`, "stroke-width": 8, "stroke-linecap": "round", fill: "none" });
    drawable(bar);
    const hd1 = svgEl(svg, "path", { d: `M${mx - 16} ${y0 + 34} L${mx} ${y0 + 14} L${mx + 16} ${y0 + 34}`, stroke: V.accent, "stroke-width": 6, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" });
    const hd2 = svgEl(svg, "path", { d: `M${mx - 16} ${y1 - 34} L${mx} ${y1 - 14} L${mx + 16} ${y1 - 34}`, stroke: V.accent2, "stroke-width": 6, fill: "none", "stroke-linecap": "round", "stroke-linejoin": "round" });
    const l1 = mk("div", "abs", r, esc(sc.meter[0])); place(l1, mx + 34, y0 + 4, 230);
    const l2 = mk("div", "abs", r, esc(sc.meter[1])); place(l2, mx + 34, y1 - 64, 230);
    [l1, l2].forEach((l) => { l.style.fontSize = "24px"; l.style.fontWeight = "700"; l.style.color = "#D6E0F5"; l.style.lineHeight = "1.25"; });
    const tm = times[0] + 0.3;
    tl.to(bar, { strokeDashoffset: 0, duration: 1.0, ease: "power2.inOut" }, tm);
    tl.from([hd1, hd2, l1, l2], { autoAlpha: 0, duration: 0.5, stagger: 0.1 }, tm + 0.6);
  };

  B.tiers = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const times = sc.items.map((_, i) => cue(S, String(i), S.first + 1 + i * 3));
    const ys = [410, 625, 840], ix = 330;
    const svg = svgLayer(r);
    const glows = [];
    sc.items.forEach((it, i) => {
      const y = ys[i];
      const node = mk("div", "abs", r); place(node, ix - 72, y - 72, 144, 144);
      const c = icirc(it.icon, 144, node);
      const g = mk("div", "abs", node); place(g, -8, -8, 160, 160);
      g.style.borderRadius = "50%"; g.style.border = `3px solid ${V.accent}`; g.style.boxShadow = `0 0 40px ${hexA(V.accent, .6)}`; g.style.opacity = 0;
      glows.push(g);
      const card = mk("div", "card", r); place(card, 470, y - 90, 1000, 180);
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 40px;gap:8px";
      const hd = mk("div", "", inner); hd.style.cssText = "display:flex;align-items:baseline;gap:18px";
      const lb = mk("div", "lbl", hd, esc(it.label)); lb.style.fontSize = "44px";
      const sb = mk("div", "mont", hd, esc(it.sub)); sb.style.cssText += `font-size:26px;font-weight:700;color:${V.accent}`;
      const wh = mk("div", "", inner, rich(it.where)); wh.style.fontSize = "28px"; wh.style.color = "#E2E9F8";
      const ds = mk("div", "desc", inner, rich(it.desc)); ds.style.fontSize = "25px";
      const t = times[i];
      tl.from(node, { scale: 0, autoAlpha: 0, duration: 0.6, ease: "back.out(2)" }, t);
      tl.from(card, { x: 60, autoAlpha: 0, duration: 0.7 }, t + 0.1);
      if (i > 0) {
        const p = svgEl(svg, "path", { d: `M${ix} ${ys[i] - 80} L${ix} ${ys[i - 1] + 80}`, stroke: hexA(V.accent, .6), "stroke-width": 4, "stroke-dasharray": "2 12", "stroke-linecap": "round", fill: "none" });
        tl.from(p, { autoAlpha: 0, duration: 0.4 }, t);
        flowDots(svg, p, t + 0.3, S.end, 3, 70, 5);
      }
    });
    activate(glows, times, S.end);
    // medidor de latencia
    const mx = 1640, y0 = ys[0] - 60, y1 = ys[2] + 60;
    const lat = mk("div", "abs", r);
    lat.style.cssText = `left:${mx - 20}px;top:${y0}px;width:40px;height:${y1 - y0}px;border-radius:20px;background:linear-gradient(180deg, #FB7185, #FBBF24 50%, #34D399);opacity:.9;box-shadow:0 0 30px rgba(0,0,0,.3)`;
    const lt = mk("div", "abs mont", r, "LATENCIA"); lt.style.cssText += `left:${mx - 100}px;top:${y0 - 56}px;width:200px;text-align:center;font-weight:800;font-size:22px;letter-spacing:.14em;color:var(--muted)`;
    const hi = mk("div", "abs", r, "Alta"); hi.style.cssText += `left:${mx + 34}px;top:${y0 + 6}px;font-size:22px;font-weight:700;color:#FDA4AF`;
    const lo = mk("div", "abs", r, "Mínima"); lo.style.cssText += `left:${mx + 34}px;top:${y1 - 36}px;font-size:22px;font-weight:700;color:#6EE7B7`;
    tl.from(lat, { scaleY: 0, transformOrigin: "50% 100%", duration: 0.9, ease: "power2.out" }, times[0] + 0.4);
    tl.from([lt, hi, lo], { autoAlpha: 0, duration: 0.5, stagger: 0.1 }, times[0] + 0.9);
    const marker = mk("div", "abs", r);
    marker.style.cssText = `left:${mx - 32}px;width:64px;height:12px;border-radius:6px;background:#fff;box-shadow:0 0 18px #fff`;
    every.push((t) => {
      if (t < times[0] + 0.9) { marker.style.opacity = 0; return; }
      let k = 0;
      times.forEach((tt, i) => { if (t >= tt) k = i; });
      const target = ys[k];
      marker.style.opacity = 1;
      marker.style.top = (target - 6) + "px";
    });
  };

  B.chain = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    const tb = cue(S, "b", S.first);
    const l0e = lineT(S, 0, "end");
    const N = 4, bw = 290, bh = 170, gap = 100, x0 = (W - (N * bw + (N - 1) * gap)) / 2, y = 330;
    const svg = svgLayer(r);
    const hashes = ["0000", "8f3a", "c71e", "5b90", "e2d4"];
    for (let i = 0; i < N; i++) {
      const x = x0 + i * (bw + gap);
      const card = mk("div", "card", r); place(card, x, y, bw, bh);
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 26px;gap:8px";
      const hd = mk("div", "", inner); hd.style.cssText = "display:flex;align-items:center;justify-content:space-between";
      const tt = mk("div", "mont", hd, `BLOQUE ${i + 1}`); tt.style.cssText += `font-weight:800;font-size:24px;color:${V.accent};letter-spacing:.08em`;
      const lk = ico("lock", "", hd); lk.style.width = lk.style.height = "30px"; lk.querySelector("svg").style.cssText = `stroke:${V.accent};stroke-width:2.2`;
      const h1 = mk("div", "mono", inner, `prev: ${hashes[i]}…`); h1.style.cssText += "font-size:20px;color:var(--muted)";
      const h2 = mk("div", "mono", inner, `hash: ${hashes[i + 1]}…`); h2.style.cssText += "font-size:20px;color:#E2E9F8";
      const t = tb + 0.2 + i * ((l0e - tb) * 0.7) / N;
      tl.from(card, { y: 50, autoAlpha: 0, duration: 0.6, ease: "back.out(1.6)" }, t);
      tl.from(lk, { scale: 0, rotation: -90, duration: 0.5, ease: "back.out(2.5)" }, t + 0.35);
      if (i > 0) {
        const xa = x - gap + 8, xb = x - 8, yy = y + bh / 2;
        const p = svgEl(svg, "path", { d: `M${xa} ${yy} L${xb} ${yy}`, stroke: `url(#${svg._gid})`, "stroke-width": 6, fill: "none", "stroke-linecap": "round" });
        drawable(p);
        const link = ico("link", "abs", r); place(link, xa + (xb - xa) / 2 - 22, yy - 22, 44, 44);
        link.querySelector("svg").style.cssText = `stroke:#fff;stroke-width:2.2`;
        link.style.background = "#0b1230"; link.style.borderRadius = "50%"; link.style.padding = "6px";
        tl.to(p, { strokeDashoffset: 0, duration: 0.4 }, t - 0.2);
        tl.from(link, { scale: 0, duration: 0.4, ease: "back.out(2)" }, t);
      }
    }
    // pilares
    const pw = 460, pgap = 50, px0 = (W - (3 * pw + 2 * pgap)) / 2, py = 580;
    const ptimes = sc.pillars.map((_, i) => cue(S, "p" + i, lineT(S, 1, "start") + i));
    const glows = [];
    sc.pillars.forEach((p, i) => {
      const card = mk("div", "card", r); place(card, px0 + i * (pw + pgap), py, pw, 150);
      glows.push(mk("div", "glow", card));
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;gap:26px;padding:0 34px";
      const c = icirc(p.icon, 92, inner);
      const lb = mk("div", "lbl", inner, esc(p.label)); lb.style.fontSize = "33px";
      tl.from(card, { y: 50, autoAlpha: 0, duration: 0.6, ease: "back.out(1.5)" }, ptimes[i]);
      tl.from(c, { scale: 0, duration: 0.5, ease: "back.out(2)" }, ptimes[i] + 0.12);
    });
    activate(glows, ptimes, cue(S, "e", S.end));
    // ejemplos
    const te = cue(S, "e", lineT(S, 2, "start"));
    const row = mk("div", "abs", r);
    row.style.cssText = "left:120px;right:120px;top:800px;display:flex;justify-content:center;align-items:center;gap:26px";
    const lab = mk("div", "mont", row, "LO USAN:"); lab.style.cssText += "font-weight:800;font-size:22px;letter-spacing:.14em;color:var(--muted)";
    tl.from(lab, { autoAlpha: 0, duration: 0.4 }, te);
    const exIcons = ["bitcoin", "apple", "heart-handshake"];
    sc.examples.forEach((ex, i) => {
      const c = mk("div", "chip", row, `${svgIcon(exIcons[i] || "circle")}<span>${esc(ex)}</span>`);
      c.querySelector("svg").style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.2;flex:none`;
      c.style.fontSize = "28px";
      tl.from(c, { y: 30, autoAlpha: 0, scale: 0.85, duration: 0.5, ease: "back.out(2)" }, te + 0.2 + i * 0.9);
    });
  };

  B.proscons = function (sc, S) {
    const r = sceneRoot(S);
    header(r, S, sc.kicker, sc.title);
    let top = 350;
    if (sc.quote) {
      const q = mk("div", "abs", r, `“${rich(sc.quote)}”`);
      q.style.cssText += `left:120px;width:1680px;top:272px;font-size:33px;font-style:italic;color:${V.accent};font-weight:600`;
      tl.from(q, { autoAlpha: 0, y: 20, duration: 0.7 }, cue(S, "q", S.first) - 0.1);
      top = 370;
    }
    const tP = cue(S, "P", S.first), tC = cue(S, "C", tP + 3);
    const nRows = Math.max(sc.pros.length, sc.cons.length);
    const colH = 190 + nRows * 70;
    const areaBot = 985;
    top = Math.round(top + Math.max(0, (areaBot - top - colH) / 2));
    const cols = [["Ventajas", "thumbs-up", "good", sc.pros, tP], [sc.quote ? "Riesgos" : "Inconvenientes", "triangle-alert", "warn", sc.cons, tC]];
    const glows = [];
    cols.forEach(([title, icon, kind, items, t0], k) => {
      const card = mk("div", "card", r); place(card, 120 + k * 860, top, 820, colH);
      const g = mk("div", "glow", card); glows.push(g);
      const col = kind === "good" ? "#34D399" : "#FB7185";
      g.style.borderColor = col; g.style.boxShadow = `0 0 44px ${hexA(col, .35)}`;
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;padding:38px 46px;display:flex;flex-direction:column;gap:20px";
      const hd = mk("div", "", inner); hd.style.cssText = "display:flex;align-items:center;gap:22px;margin-bottom:6px";
      const c = icirc(icon, 88, hd);
      c.style.background = `radial-gradient(circle at 32% 28%, ${hexA(col, .55)}, ${hexA(col, .15)} 70%)`; c.style.borderColor = hexA(col, .8); c.style.boxShadow = `0 0 30px ${hexA(col, .3)}`;
      const h = mk("div", "lbl", hd, esc(title)); h.style.fontSize = "42px";
      const rows = items.map((it) => {
        const row = mk("div", "row", inner);
        mk("div", "mk " + kind, row, svgIcon(kind === "good" ? "check" : "x"));
        mk("div", "", row, rich(it));
        return row;
      });
      tl.from(card, { y: 50, autoAlpha: 0, duration: 0.7, ease: "power3.out" }, t0 - 0.15);
      tl.from(c, { scale: 0, duration: 0.5, ease: "back.out(2)" }, t0);
      // cada fila aparece a lo largo de la frase (o en su marca c3, etc.)
      const lEnd = T.lines.find((l) => l.scene === S.index && l.start <= t0 + 0.01 && l.end >= t0);
      const span = lEnd ? Math.max(1.2, (lEnd.end - t0) * 0.85) : 2.5;
      rows.forEach((row, i) => {
        const tt = cue(S, (k === 1 ? "c" : "p") + i, t0 + 0.35 + (i * span) / rows.length);
        tl.from(row, { x: 30, autoAlpha: 0, duration: 0.45 }, tt);
      });
    });
    activate(glows, [tP, tC], S.end);
  };

  B.outro = function (sc, S) {
    const r = sceneRoot(S);
    const hit = T.hit;
    // «Ideas clave» se mantiene durante la última frase; la tarjeta final entra con el golpe musical
    const tEnd = hit - 0.3;
    // parte 1: ideas clave
    const p1 = mk("div", "abs", r); p1.style.cssText += "inset:0";
    const h = mk("div", "abs mont", p1);
    h.style.cssText += "left:0;right:0;top:185px;text-align:center;font-weight:800;font-size:70px";
    h.innerHTML = `<span class="grad">${esc(sc.title)}</span>`;
    tl.from(h, { y: 40, autoAlpha: 0, duration: 0.7 }, S.start + 0.15);
    sc.items.forEach((it, i) => {
      const x = 150 + (i % 2) * 830, y = 370 + Math.floor(i / 2) * 215;
      const card = mk("div", "card", p1); place(card, x, y, 790, 180);
      const inner = mk("div", "", card);
      inner.style.cssText = "position:absolute;inset:0;display:flex;align-items:center;gap:28px;padding:0 38px";
      const m = mk("div", "", inner, svgIcon("check"));
      m.style.cssText = `width:70px;height:70px;border-radius:50%;flex:none;display:grid;place-items:center;background:linear-gradient(135deg, ${V.accent}, ${V.accent2});box-shadow:0 0 30px ${hexA(V.accent, .5)}`;
      m.querySelector("svg").style.cssText = "width:38px;height:38px;stroke:#061018;stroke-width:3.2";
      const tx = mk("div", "lbl", inner, rich(it)); tx.style.fontSize = "31px"; tx.style.fontWeight = "700";
      const t = S.start + 0.35 + i * 0.3;
      tl.from(card, { y: 50, autoAlpha: 0, scale: 0.95, duration: 0.6, ease: "back.out(1.5)" }, t);
      tl.from(m, { scale: 0, rotation: -90, duration: 0.5, ease: "back.out(2.5)" }, t + 0.2);
    });
    tl.to(p1, { autoAlpha: 0, y: -40, duration: 0.5, ease: "power2.in" }, tEnd - 0.1);
    // parte 2: tarjeta final
    const p2 = mk("div", "abs", r); p2.style.cssText += "inset:0";
    const ex = 960, ey = 390;
    const rings = [150, 195, 245].map((rad, i) => {
      const g = mk("div", "abs", p2); place(g, ex - rad, ey - rad, rad * 2, rad * 2);
      g.style.borderRadius = "50%";
      g.style.border = i === 1 ? `2px dashed ${hexA(V.accent2, .55)}` : `1.5px solid ${hexA(V.accent, i === 0 ? .7 : .25)}`;
      return g;
    });
    const em = mk("div", "abs", p2); place(em, ex - 115, ey - 115, 230, 230);
    const c = icirc(V.icon, 230, em);
    const big = mk("div", "abs mont", p2);
    big.style.cssText += "left:0;right:0;top:680px;text-align:center;font-weight:900;font-size:76px;line-height:1.1";
    big.innerHTML = `¡Unidad ${esc(V.num)} <span class="grad">repasada!</span>`;
    const nx = mk("div", "abs", p2);
    nx.style.cssText += "left:0;right:0;top:810px;display:flex;justify-content:center";
    const nchip = mk("div", "chip", nx, V.next
      ? `${svgIcon("arrow-right")}<span>Próxima: ${esc(V.next)}</span>`
      : `${svgIcon("sparkles")}<span>¡Sigue aprendiendo!</span>`);
    nchip.querySelector("svg").style.cssText = `width:30px;height:30px;stroke:${V.accent};stroke-width:2.4;flex:none`;
    nchip.style.fontSize = "30px";
    const cr = mk("div", "abs", p2, `${esc(V.module)} · Curso 2026/2027`);
    cr.style.cssText += "left:0;right:0;top:940px;text-align:center;font-size:22px;color:var(--dim);letter-spacing:.06em";
    tl.from(rings, { scale: 0.5, autoAlpha: 0, duration: 1, stagger: 0.1, ease: "expo.out" }, tEnd + 0.1);
    tl.from(c, { scale: 0, rotation: -120, duration: 0.9, ease: "back.out(1.8)" }, tEnd + 0.15);
    tl.from(big, { y: 40, autoAlpha: 0, duration: 0.7, ease: "back.out(1.4)" }, tEnd + 0.35);
    tl.from(nchip, { y: 30, autoAlpha: 0, duration: 0.6, ease: "back.out(1.6)" }, tEnd + 0.7);
    tl.from(cr, { autoAlpha: 0, duration: 0.6 }, tEnd + 1.0);
    tl.to(c, { scale: 1.12, duration: 0.18, yoyo: true, repeat: 1, ease: "power2.out" }, hit);
    bursts.push({ t: tEnd + 0.15, x: ex, y: ey, n: 70, spread: 520 });
    bursts.push({ t: hit, x: ex, y: ey, n: 120, spread: 900 });
    every.push((t) => {
      if (t < tEnd) return;
      rings[1].style.transform = `rotate(${t * 20}deg)`;
      rings[2].style.transform = `scale(${1 + 0.04 * Math.sin(t * 2.4)})`;
    });
  };

  // ───────────────────────────── cromo (marca + capítulos) y transiciones
  function buildChrome() {
    const b = mk("div", "brand", chrome);
    mk("div", "ut", b, esc(V.id));
    mk("div", "mod", b, esc(V.module));
    const ch = mk("div", "chapters", chrome);
    const content = T.scenes.filter((s) => s.type !== "intro" && s.type !== "outro");
    const segs = content.map(() => mk("i", "", mk("div", "seg", ch)));
    const lbl = mk("div", "lbl", ch);
    const t0 = T.scenes[1].start, t1 = T.scenes[T.scenes.length - 1].start;
    tl.fromTo([b, ch], { autoAlpha: 0, y: -24 }, { autoAlpha: 1, y: 0, duration: 0.7, stagger: 0.1 }, t0 + 0.05);
    tl.to(ch, { autoAlpha: 0, y: -24, duration: 0.5 }, t1 + 0.05);
    tl.to(b, { autoAlpha: 0, duration: 0.6 }, T.hit - 0.4);
    every.push((t) => {
      let cur = -1;
      content.forEach((s, i) => {
        const k = clamp((t - s.start) / (s.end - s.start), 0, 1);
        segs[i].style.transform = `scaleX(${k.toFixed(4)})`;
        if (t >= s.start && t < s.end) cur = i;
      });
      lbl.textContent = cur >= 0 ? `${String(cur + 1).padStart(2, "0")} / ${String(content.length).padStart(2, "0")}` : "";
    });
    const sweep = document.getElementById("sweep");
    gsap.set(sweep, { rotation: 12, x: -900, opacity: 0 });
    T.scenes.slice(1).forEach((s) => {
      tl.fromTo(sweep, { x: -900, opacity: 1 }, { x: 2500, opacity: 1, duration: 0.95, ease: "power2.inOut", immediateRender: false }, s.start - 0.35);
      tl.set(sweep, { opacity: 0 }, s.start + 0.62);
    });
    const fade = document.getElementById("fade");
    tl.fromTo(fade, { opacity: 1 }, { opacity: 0, duration: 0.5, ease: "none" }, 0);
    tl.to(fade, { opacity: 1, duration: 0.9, ease: "none" }, T.duration - 0.9);
  }

  // ───────────────────────────── fondo (canvas)
  const canvas = document.getElementById("bg");
  canvas.width = W; canvas.height = H;
  const ctx = canvas.getContext("2d");
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const rnd = mulberry32(20262027);
  const nodes = Array.from({ length: 64 }, () => ({
    x: rnd() * W, y: rnd() * H, ax: 40 + rnd() * 90, ay: 30 + rnd() * 70,
    fx: 0.012 + rnd() * 0.03, fy: 0.012 + rnd() * 0.03, px: rnd() * 6.283, py: rnd() * 6.283, r: 1.2 + rnd() * 1.8, c: rnd(),
  }));
  const blobs = [
    { c: V.accent, r: 780, x: 0.2, y: 0.25, ax: 0.1, ay: 0.08, f: 0.018, a: 0.17 },
    { c: V.accent2, r: 860, x: 0.82, y: 0.75, ax: 0.09, ay: 0.1, f: 0.014, a: 0.16 },
    { c: "#6D28D9", r: 700, x: 0.72, y: 0.16, ax: 0.12, ay: 0.06, f: 0.011, a: 0.11 },
  ];
  const burstParts = new Map();
  function drawBg(t) {
    ctx.globalCompositeOperation = "source-over";
    const g = ctx.createRadialGradient(960, 470, 60, 960, 540, 1250);
    g.addColorStop(0, "#0d1537"); g.addColorStop(0.55, "#070b1f"); g.addColorStop(1, "#02030a");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";
    for (const b of blobs) {
      const x = (b.x + b.ax * Math.sin(t * b.f * 6.283 + b.x * 10)) * W;
      const y = (b.y + b.ay * Math.cos(t * b.f * 6.283 * 1.3 + b.y * 7)) * H;
      const rg = ctx.createRadialGradient(x, y, 0, x, y, b.r);
      rg.addColorStop(0, hexA(b.c, b.a)); rg.addColorStop(1, hexA(b.c, 0));
      ctx.fillStyle = rg; ctx.fillRect(x - b.r, y - b.r, 2 * b.r, 2 * b.r);
    }
    ctx.globalCompositeOperation = "source-over";
    for (let gx = 24; gx < W; gx += 48) {
      for (let gy = 24; gy < H; gy += 48) {
        const w = Math.cos((gx * 0.8 + gy) / 240 - t * 0.9);
        const a = 0.05 + 0.13 * Math.pow(Math.max(0, w), 14);
        ctx.fillStyle = `rgba(170,195,255,${a.toFixed(3)})`;
        ctx.fillRect(gx - 1, gy - 1, 2, 2);
      }
    }
    const P = nodes.map((n) => [n.x + n.ax * Math.sin(t * n.fx * 6.283 + n.px), n.y + n.ay * Math.cos(t * n.fy * 6.283 + n.py)]);
    ctx.lineWidth = 1;
    const acc = hexA(V.accent, 1).match(/\d+/g).slice(0, 3).join(",");
    for (let i = 0; i < P.length; i++) {
      for (let j = i + 1; j < P.length; j++) {
        const dx = P[i][0] - P[j][0], dy = P[i][1] - P[j][1];
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < 210) {
          ctx.strokeStyle = `rgba(${acc},${((1 - d / 210) * 0.2).toFixed(3)})`;
          ctx.beginPath(); ctx.moveTo(P[i][0], P[i][1]); ctx.lineTo(P[j][0], P[j][1]); ctx.stroke();
        }
      }
    }
    for (let i = 0; i < P.length; i++) {
      ctx.fillStyle = nodes[i].c > 0.6 ? hexA(V.accent, 0.8) : "rgba(220,230,255,0.55)";
      ctx.beginPath(); ctx.arc(P[i][0], P[i][1], nodes[i].r, 0, 6.283); ctx.fill();
    }
    // explosiones de partículas
    ctx.globalCompositeOperation = "lighter";
    for (const b of bursts) {
      const dt = t - b.t;
      if (dt < 0 || dt > 2.4) continue;
      if (!burstParts.has(b)) {
        const r2 = mulberry32(Math.floor(b.t * 1000) + 7);
        burstParts.set(b, Array.from({ length: b.n }, () => ({ a: r2() * 6.283, s: 0.25 + r2() * 0.75, z: 1 + r2() * 2.5, c: r2() })));
      }
      const k = 1 - Math.exp(-dt * 2.6);
      const fade = Math.pow(1 - dt / 2.4, 1.6);
      for (const p of burstParts.get(b)) {
        const d = b.spread * p.s * k;
        const x = b.x + Math.cos(p.a) * d, y = b.y + Math.sin(p.a) * d;
        ctx.fillStyle = p.c > 0.5 ? hexA(V.accent, 0.9 * fade) : hexA(V.accent2, 0.9 * fade);
        ctx.beginPath(); ctx.arc(x, y, p.z, 0, 6.283); ctx.fill();
      }
    }
    ctx.globalCompositeOperation = "source-over";
    const v = ctx.createRadialGradient(960, 540, 520, 960, 540, 1180);
    v.addColorStop(0, "rgba(0,0,0,0)"); v.addColorStop(1, "rgba(0,0,0,0.6)");
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  }

  // ───────────────────────────── construcción
  function build() {
    T.scenes.forEach((S, i) => {
      const sc = V.scenes[i];
      const f = B[sc.type];
      if (!f) throw new Error("tipo de escena desconocido: " + sc.type);
      f(sc, S);
    });
    buildChrome();
    (window.__post || []).forEach((fn) => fn());
    window.renderFrame(0);
    window.ENGINE_READY = true;
  }
  window.renderFrame = function (t) {
    tl.seek(t, false);
    for (const f of every) f(t);
    drawBg(t);
  };
  window.DURATION = T.duration;
  document.fonts.ready.then(() => {
    Promise.all(["800 66px Montserrat", "900 66px Montserrat", "700 30px Montserrat", "500 30px Inter", "600 30px Inter", "700 30px Inter"].map((f) => document.fonts.load(f)))
      .then(() => { try { build(); } catch (e) { window.ENGINE_ERROR = String(e && e.stack || e); throw e; } });
  });
})();
