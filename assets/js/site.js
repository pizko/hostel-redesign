/* Like Home — интерактив без библиотек. Всё работает и без JS: содержимое видно, форма отправляется обычным POST. */
(() => {
  document.documentElement.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Шапка: плотный фон после начала прокрутки; мобильная панель звонка — после первого экрана
  const hdr = document.querySelector('[data-hdr]');
  const dock = document.querySelector('[data-dock]');
  const onScroll = () => {
    const y = window.scrollY;
    hdr?.classList.toggle('is-solid', y > 24);
    dock?.classList.toggle('is-on', y > window.innerHeight * 0.6);
  };
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  // Меню
  const burger = document.querySelector('[data-burger]');
  const menu = document.querySelector('[data-menu]');
  const setMenu = open => {
    burger?.setAttribute('aria-expanded', String(open));
    if (menu) menu.hidden = !open;
    document.body.style.overflow = open ? 'hidden' : '';
  };
  burger?.addEventListener('click', () => setMenu(burger.getAttribute('aria-expanded') !== 'true'));
  menu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  addEventListener('keydown', ev => { if (ev.key === 'Escape' && menu && !menu.hidden) { setMenu(false); burger?.focus(); } });

  // Появление блоков
  const targets = document.querySelectorAll('[data-reveal], .stop, [data-split], [data-mask], .route-box, [data-line]');
  if (reduce || !('IntersectionObserver' in window)) {
    targets.forEach(t => t.classList.add('is-in'));
  } else {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
    }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(t => io.observe(t));
  }

  // Переключатель комнат 8 / 10 / 12
  const tabs = [...document.querySelectorAll('[data-room]')];
  tabs.forEach(tab => tab.addEventListener('click', () => {
    tabs.forEach(t => {
      const on = t === tab;
      t.classList.toggle('is-on', on);
      t.setAttribute('aria-selected', String(on));
      const pane = document.getElementById('rm-' + t.dataset.room);
      if (pane) { pane.hidden = !on; pane.classList.toggle('is-on', on); }
    });
  }));
  tabs.forEach((tab, i) => tab.addEventListener('keydown', ev => {
    if (ev.key !== 'ArrowRight' && ev.key !== 'ArrowLeft') return;
    const next = tabs[(i + (ev.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
    next.focus(); next.click();
  }));

  // Карта грузится по клику — не тянет сторонний скрипт на первом экране
  document.querySelectorAll('[data-map]').forEach(box => {
    box.querySelector('.map-load')?.addEventListener('click', () => {
      const f = document.createElement('iframe');
      f.src = box.dataset.src; f.title = 'Like Home на карте'; f.loading = 'lazy'; f.allowFullscreen = true;
      box.innerHTML = ''; box.appendChild(f);
    });
  });

  // Форма: тот же обработчик, что на боевом сайте (/send_booking.php). Успех — только по ответу {ok:true}.
  const form = document.querySelector('[data-form]');
  if (form) {
    const msg = form.querySelector('[data-msg]');
    const preview = /github\.io$|localhost|127\.0\.0\.1/.test(location.hostname);
    const tel = document.querySelector('.big-tel')?.textContent || '';
    const today = new Date(); today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    const inp = form.querySelector('[name="checkin"]');
    if (inp) inp.min = today.toISOString().slice(0, 10);
    const say = (text, ok) => { msg.textContent = text; msg.className = 'form-msg ' + (ok ? 'is-ok' : 'is-err'); };
    form.addEventListener('submit', async ev => {
      ev.preventDefault();
      let bad = null;
      form.querySelectorAll('input[required]').forEach(i => {
        const invalid = !i.checkValidity();
        i.setAttribute('aria-invalid', String(invalid));
        if (invalid && !bad) bad = i;
      });
      if (bad) { bad.focus(); say('Проверьте отмеченные поля.', false); return; }
      if (preview) { say(`Это предпросмотр: отправка заявок работает на боевом сайте. Позвоните: ${tel}`, false); return; }
      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      try {
        const res = await fetch(form.getAttribute('action'), { method: 'POST', body: new FormData(form) });
        const data = await res.json().catch(() => null);
        if (!res.ok || !data || !data.ok) throw new Error(data && data.error ? data.error : '');
        form.reset(); say('Заявка отправлена. Мы свяжемся с вами.', true);
      } catch (err) {
        say((err.message ? err.message + ' ' : 'Не удалось отправить заявку. ') + `Позвоните: ${tel}`, false);
      } finally { btn.disabled = false; }
    });
  }

  // Кнопки «Заявка» плавно ведут к форме и ставят фокус в первое поле
  document.querySelectorAll('[data-to-form]').forEach(a => a.addEventListener('click', ev => {
    const f = document.getElementById('zayavka');
    if (!f) return;
    ev.preventDefault();
    f.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    setTimeout(() => f.querySelector('input')?.focus({ preventScroll: true }), reduce ? 0 : 600);
  }));
})();
