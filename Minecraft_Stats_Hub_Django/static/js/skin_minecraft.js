/* Recrea la vista FRONTAL del personaje a partir del PNG original de Mojang.
   No usa Crafatar, no depende de renders que puedan devolver Alex por defecto. */
(() => {
  'use strict';
  const visor = document.querySelector('[data-skin-url]');
  if (!visor) return;
  const cuerpo = visor.querySelector('.mc-skin-body');
  const cara = document.querySelector('.mc-skin-face');
  const estado = visor.querySelector('.mc-skin-status');
  if (!cuerpo || !cara) return;

  const img = new Image();
  img.onload = () => {
    if (img.width !== 64 || ![32, 64].includes(img.height)) {
      estado.textContent = 'El formato de la textura no es compatible.';
      return;
    }
    const classic = !visor.dataset.skinModel.startsWith('Slim');
    const newSkin = img.height === 64;
    const armWidth = classic ? 4 : 3;
    const ctx = cuerpo.getContext('2d');
    const faceCtx = cara.getContext('2d');
    if (!ctx || !faceCtx) {
      estado.textContent = 'El navegador no puede dibujar la textura.';
      return;
    }
    ctx.imageSmoothingEnabled = false;
    faceCtx.imageSmoothingEnabled = false;
    ctx.clearRect(0, 0, 16, 32);
    faceCtx.clearRect(0, 0, 8, 8);

    // Cada parte se copia desde su zona original del skin atlas de Minecraft.
    function draw(sx, sy, w, h, dx, dy) {
      ctx.drawImage(img, sx, sy, w, h, dx, dy, w, h);
    }
    function mirror(sx, sy, w, h, dx, dy) {
      ctx.save();
      ctx.translate(dx + w, dy);
      ctx.scale(-1, 1);
      ctx.drawImage(img, sx, sy, w, h, 0, 0, w, h);
      ctx.restore();
    }
    // Base frontal (cabeza, torso, brazos y piernas).
    draw(8, 8, 8, 8, 4, 0);
    draw(20, 20, 8, 12, 4, 8);
    draw(44, 20, armWidth, 12, classic ? 0 : 1, 8);
    if (newSkin) draw(36, 52, armWidth, 12, 12, 8);
    else mirror(44, 20, 4, 12, 12, 8);
    draw(4, 20, 4, 12, 4, 20);
    if (newSkin) draw(20, 52, 4, 12, 8, 20);
    else mirror(4, 20, 4, 12, 8, 20);
    // Segunda capa, si existe; en skins 64x32 sólo el casco.
    if (newSkin) {
      draw(20, 36, 8, 12, 4, 8);
      draw(44, 36, armWidth, 12, classic ? 0 : 1, 8);
      draw(52, 52, armWidth, 12, 12, 8);
      draw(4, 36, 4, 12, 4, 20);
      draw(4, 52, 4, 12, 8, 20);
    }
    draw(40, 8, 8, 8, 4, 0);
    faceCtx.drawImage(img, 8, 8, 8, 8, 0, 0, 8, 8);
    faceCtx.drawImage(img, 40, 8, 8, 8, 0, 0, 8, 8);
    cuerpo.hidden = false;
    cara.hidden = false;
    estado.textContent = 'Vista frontal de la skin oficial de Mojang.';
  };
  img.onerror = () => {
    estado.textContent = 'No se pudo cargar la textura oficial ahora. Probá de nuevo más tarde.';
  };
  img.src = visor.dataset.skinUrl;
})();
