/* Justin Dental and Braces — EN/ES text toggle.
   Swaps textContent in place (no page duplication) and persists the choice.
   NAP, brand name, and doctor names are intentionally left untranslated. */
(function () {
  'use strict';

  var ES = {
    'skip': 'Ir al contenido principal',
    'header.spanish': 'Hablamos Español',
    'header.schedule': 'Programar Cita',
    'header.callnow': 'Llamar Ahora',
    'trustbar.text': 'Más de 1,000+ ⭐⭐⭐⭐⭐ Reseñas de Google',

    'hero.h1': 'Su Dentista de Confianza en Justin, TX',
    'hero.sub': 'Atención dental familiar enfocada en su comodidad, sus metas y la salud de su boca a largo plazo.',
    'hero.cta1': 'Programe Su Cita',
    'hero.cta2': 'Llame (940) 242-2022',
    'hero.reviews': 'Más de 1,000+ ⭐⭐⭐⭐⭐ Reseñas de Google',
    'hero.spanish': 'HABLAMOS ESPAÑOL',
    'hero.online': 'Programación de Citas en Línea las 24 Horas',
    'hero.trust1': 'Consultorio Familiar',
    'hero.trust2': 'Pacientes Nuevos Bienvenidos',
    'hero.trust3': 'Opciones de Pago Flexibles',
    'hero.trust4': 'Aceptamos Seguro Dental',
    'hero.cardh': '¿Necesita una Cita?',
    'hero.cardp': 'Reserve en línea en menos de un minuto, día o noche.',
    'hero.cardcta': 'Programar en Línea',

    'quick.h2': '¿Listo Para Dar el Siguiente Paso?',
    'quick.call': 'Llámenos',
    'quick.schedule': 'Programar en Línea',
    'quick.scheduleSub': 'Reserve su cita cuando quiera',
    'quick.spanish': 'Hablamos Español',
    'quick.spanishSub': 'Se Habla Español',

    'why.eyebrow': 'Por Qué Confían en Nosotros',
    'why.h2': 'Por Qué las Familias de Justin Nos Eligen',
    'why.c1h': 'Atención Familiar',
    'why.c1p': 'Atención dental personalizada de un consultorio local — no una cadena corporativa.',
    'why.c2h': 'Enfoque en el Paciente',
    'why.c2p': 'Nos enfocamos en lo que es correcto para usted y recomendamos tratamiento según sus necesidades.',
    'why.c3h': 'Tecnología Moderna',
    'why.c3p': 'La tecnología dental avanzada nos ayuda a brindar atención precisa y eficiente.',
    'why.c4h': 'Opciones de Pago Flexibles',
    'why.c4p': 'Múltiples opciones de pago y financiamiento para facilitar el costo del tratamiento.',
    'why.c5h': 'Horarios Convenientes',
    'why.c5p': 'Programe su cita en línea y reciba la atención que su familia necesita cuando le convenga.',
    'why.c6h': 'Ambiente Cómodo',
    'why.c6p': 'Una experiencia relajada y familiar, diseñada pensando en su comodidad.',

    'svc.eyebrow': 'Nuestros Servicios',
    'svc.h2': 'Atención Dental Completa Para Su Familia',
    'svc.sub': 'Desde cuidado preventivo hasta odontología restaurativa y ortodoncia, nuestro equipo ofrece atención dental completa bajo un mismo techo.',
    'svc.learnmore': 'Más Información',
    'svc.callnow': 'Llamar Ahora',
    'svc.consult': 'Programar Consulta',
    'svc.gd.h': 'Odontología General', 'svc.gd.l1': 'Limpiezas', 'svc.gd.l2': 'Exámenes', 'svc.gd.l3': 'Empastes', 'svc.gd.l4': 'Coronas y Puentes',
    'svc.em.h': 'Emergencias Dentales', 'svc.em.l1': 'Dolor de dientes', 'svc.em.l2': 'Dientes rotos', 'svc.em.l3': 'Emergencias dentales',
    'svc.rd.h': 'Odontología Restaurativa', 'svc.rd.l1': 'Coronas', 'svc.rd.l2': 'Puentes', 'svc.rd.l3': 'Endodoncias', 'svc.rd.l4': 'Dentaduras',
    'svc.cd.h': 'Odontología Cosmética', 'svc.cd.l1': 'Mejora de sonrisa', 'svc.cd.l2': 'Tratamiento cosmético', 'svc.cd.l3': 'Transformación de sonrisa',
    'svc.ortho.h': 'Ortodoncia', 'svc.ortho.l1': 'Brackets', 'svc.ortho.l2': 'Invisalign', 'svc.ortho.l3': 'Alineadores transparentes',
    'svc.ws.h': 'Muelas del Juicio / Cirugía Oral', 'svc.ws.l1': 'Evaluación de muelas del juicio', 'svc.ws.l2': 'Extracción de muelas del juicio', 'svc.ws.l3': 'Cirugía oral',

    'emg.h2': '¿Tiene un Problema Dental Que No Puede Esperar?',
    'emg.p': 'No ignore un dolor de muelas severo, un diente roto, hinchazón, u otra urgencia dental.',
    'emg.call': 'Llame Ahora (940) 242-2022',
    'emg.request': 'Solicitar una Cita',

    'docs.eyebrow': 'Conozca al Equipo',
    'docs.h2': 'Conozca a Su Equipo Dental en Justin',
    'docs.amee.role': 'Dentista General',
    'docs.amee.bio': 'Más de 12 años de experiencia en odontología. Enfocada en la atención familiar, la comodidad del paciente y el tratamiento personalizado.',
    'docs.amee.t1': '12+ Años de Experiencia', 'docs.amee.t2': 'Boston University',
    'docs.andy.role': 'Ortodoncista',
    'docs.andy.bio': 'Ortodoncista especializado en brackets. Más de 10 años de experiencia en el área metropolitana. Enfocado en brackets, Invisalign y atención centrada en el paciente.',
    'docs.andy.t1': '10+ Años de Experiencia', 'docs.andy.t2': 'St. Louis University',
    'docs.quote': 'Un Equipo Que Cuida a Su Familia',

    'rev.count': 'Más de 1,000+ Reseñas de Google',
    'rev.h2': 'Lo Que Dicen Nuestros Pacientes',
    'rev.src': 'Reseña de Google',
    'rev.name2': 'Dr. Green’s C.',
    'rev.q1': '“El Dr. Shah y su equipo son muy conocedores. Tuvimos una gran experiencia y agradecimos el trato que recibimos. El horario de la oficina es de gran ayuda para padres ocupados. Recomiendo ampliamente Justin Dental and Braces.”',
    'rev.q2': '“Nuestra hija tuvo dos fases de brackets con resultados excelentes, y sus visitas regulares de limpieza siempre son fantásticas. Ambos Dr. Shah realmente se preocupan por nuestra hija. Recomendamos ampliamente Justin Dental and Braces a quien busque atención dental superior con opciones de pago flexibles.”',
    'rev.q3': '“Me hice mi tratamiento de Invisalign aquí y estoy muy contento con los resultados. El Dr. Shah realmente cambió mi sonrisa y mi confianza. Lo recomiendo ampliamente a mis amigos y familia.”',
    'rev.more': 'Ver Más Reseñas de Google',

    'es.eyebrow': 'Atención en Español',
    'es.h2': '¿Habla Español? Estamos Aquí Para Ayudarle.',
    'es.p': 'Nuestro equipo está disponible para ayudarle a entender sus opciones de tratamiento y hacer que su experiencia dental sea cómoda y sencilla.',
    'es.cta1': 'Programar una Cita',
    'es.cta2': 'Llámenos: (940) 242-2022',
    'es.badge': 'Se Habla Español',

    'fin.eyebrow': 'Financiamiento',
    'fin.h2': 'Haga Que Su Cuidado Dental Sea Más Accesible',
    'fin.p': 'Las opciones flexibles de pago y financiamiento pueden ayudarle a manejar el costo del tratamiento mientras recibe la atención que necesita.',
    'fin.p1': 'Múltiples opciones de pago disponibles en el consultorio',
    'fin.p2': 'Varias opciones de financiamiento dental para su presupuesto',
    'fin.p3': 'Aceptamos los principales planes de seguro dental',
    'fin.talk': 'Hable Con Nuestro Equipo',
    'fin.talk2': 'Hable Con Nuestro Equipo',
    'fin.fine': 'El financiamiento está sujeto a la aprobación del prestamista. Aplican términos y condiciones. Precalificar no garantiza la aprobación.',
    'fin.cherryp': 'Vea cuánto podría precalificar con Cherry — una forma flexible de pagar su tratamiento con el tiempo.',
    'fin.check': 'Vea Sus Opciones de Financiamiento',
    'fin.subject': 'Sujeto a aprobación del prestamista. Vea sus opciones disponibles.',

    'ins.eyebrow': 'Seguro Dental',
    'ins.h2': 'Atención Dental Compatible con Su Seguro',
    'ins.p': 'Nuestro equipo puede ayudarle a entender sus beneficios, verificar su cobertura y facilitar el proceso con el seguro.',
    'ins.cta': 'Verificar Mi Seguro',
    'ins.cardh': 'Trabajamos con la mayoría de los planes dentales principales',
    'ins.other': 'La mayoría de los planes dentales PPO',
    'ins.note': '¿No está seguro de su plan? Llame a nuestra oficina y nuestro equipo le ayudará a verificar sus beneficios antes de su visita.',

    'sav.eyebrow': '¿Sin Seguro? No Hay Problema',
    'sav.h2': '¿Sin Seguro? Tenemos Opciones.',
    'sav.p': 'Nuestro Plan de Ahorros Dental es una opción de membresía diseñada para ayudar a pacientes sin seguro a recibir atención de calidad a un precio accesible — sin limitaciones por condiciones preexistentes, sin límite anual y sin períodos de espera.',
    'sav.p1': 'Incluye exámenes, limpiezas y radiografías regulares',
    'sav.p2': 'Beneficios para tratamiento adicional según sea necesario',
    'sav.p3': 'Sin condiciones preexistentes, sin límite anual, sin períodos de espera',
    'sav.cta': 'Conozca Nuestro Plan de Ahorros',
    'sav.asidep': 'Llame a nuestra oficina para conocer el precio actual de la membresía para su familia.',
    'sav.call': '(940) 242-2022',

    'local.eyebrow': 'Sirviendo a Justin, TX y Más Allá',
    'local.h2': 'Su Dentista Local en Justin, TX',
    'local.p': 'Convenientemente ubicado en 815 W 1st St Ste B, Justin Dental and Braces atiende con orgullo a pacientes y familias en Justin y las comunidades vecinas.',

    'map.h2': 'Visítenos en Justin',
    'map.hours': 'Lun – Vie: 9:00 AM – 6:00 PM',
    'map.hoursweekend': 'Sábado y Domingo: Cerrado',
    'map.directions': 'Cómo Llegar',

    'faq.eyebrow': 'Preguntas Frecuentes',
    'faq.h2': 'Preguntas Frecuentes',
    'faq.q1': '¿Aceptan pacientes nuevos?',
    'faq.a1': 'Sí — Justin Dental and Braces recibe con gusto a pacientes nuevos de todas las edades.',
    'faq.q2': '¿Aceptan seguro dental?',
    'faq.a2': 'Sí, trabajamos con la mayoría de los planes de seguro dental, incluyendo Aetna. Llame a nuestra oficina y nuestro equipo le ayudará a verificar sus beneficios específicos.',
    'faq.q3': '¿Ofrecen financiamiento?',
    'faq.a3': 'Sí, ofrecemos múltiples opciones de pago y financiamiento, incluyendo financiamiento con Cherry, para facilitar el presupuesto de su tratamiento. Aplican términos y condiciones, sujeto a aprobación del prestamista.',
    'faq.q4': '¿Puedo precalificar para financiamiento?',
    'faq.a4': 'Muchas de nuestras opciones de financiamiento le permiten ver para cuánto podría precalificar. Precalificar no garantiza la aprobación. Llame a nuestro equipo y le explicaremos sus opciones disponibles.',
    'faq.q5': '¿Hablan español?',
    'faq.a5': 'Sí, hablamos español. Nuestro equipo está disponible para ayudarle a entender sus opciones de tratamiento en español.',
    'faq.q6': '¿Puedo programar una cita en línea?',
    'faq.a6': 'Sí, ofrecemos programación de citas en línea las 24 horas, para que pueda solicitar una visita cuando le convenga.',
    'faq.q7': '¿Qué servicios dentales ofrecen?',
    'faq.a7': 'Ofrecemos odontología general, odontología restaurativa, odontología cosmética, ortodoncia (brackets e Invisalign), atención dental de emergencia, y muelas del juicio / cirugía oral.',
    'faq.q8': '¿Ofrecen brackets?',
    'faq.a8': 'Sí, el Dr. Ankit "Andy" Shah es nuestro ortodoncista especializado en brackets, con más de 10 años de experiencia en el área metropolitana.',
    'faq.q9': '¿Ofrecen Invisalign?',
    'faq.a9': 'Sí, el tratamiento con Invisalign y alineadores transparentes está disponible como alternativa a los brackets tradicionales.',
    'faq.q10': '¿Dónde está ubicado Justin Dental and Braces?',
    'faq.a10': 'Estamos ubicados en 815 W 1st St Ste B, Justin, TX 76247, sirviendo a Justin y comunidades vecinas incluyendo Rhome, Ponder, Northlake, Boyd, Newark, Haslet y Decatur.',
    'faq.q11': '¿Qué debo hacer si tengo una emergencia dental?',
    'faq.a11': 'Llame a nuestra oficina de inmediato al (940) 242-2022. No ignore un dolor de muelas severo, un diente roto o hinchazón — nuestro equipo le ayudará a atenderlo lo antes posible.',
    'faq.q12': '¿Qué opciones de pago tienen disponibles?',
    'faq.a12': 'Ofrecemos múltiples opciones de pago, financiamiento dental incluyendo Cherry, la mayoría de los seguros dentales principales, y un Plan de Ahorros Dental en el consultorio para pacientes sin seguro.',

    'form.eyebrow': 'Solicitar una Cita',
    'form.h2': 'Cuéntenos Cómo Podemos Ayudarle',
    'form.sub': 'Complete el siguiente formulario y nuestro equipo se comunicará con usted para confirmar los detalles de su cita.',
    'form.first': 'Nombre', 'form.last': 'Apellido', 'form.phone': 'Teléfono', 'form.email': 'Correo Electrónico',
    'form.date': 'Fecha Preferida de la Cita', 'form.insurance': 'Proveedor de Seguro (opcional)', 'form.reason': 'Motivo de la Visita',
    'form.consent': 'Acepto que me contacten sobre mi solicitud de cita.',
    'form.submit': 'Solicitar Mi Cita',
    'form.note': '¿Prefiere hablar ahora? Llámenos al (940) 242-2022.',
    'form.thanksh': 'Solicitud Recibida',
    'form.thanksp': '¡Gracias! Un miembro de nuestro equipo se comunicará con usted en breve para confirmar su cita.',

    'final.eyebrow': 'Justin Dental and Braces',
    'final.h2': '¿Listo Para Sentirse Mejor Con Su Cuidado Dental?',
    'final.p': 'Ya sea que necesite un chequeo, tenga dolor de dientes, quiera mejorar su sonrisa, o busque atención para su familia, estamos aquí para ayudarle.',
    'final.cta1': 'Programe Su Cita',
    'final.cta2': 'Llame (940) 242-2022',
    'final.reviews': 'Más de 1,000+ Reseñas de Google',
    'final.spanish': 'HABLAMOS ESPAÑOL',

    'footer.hours': 'Horario',
    'footer.mon': 'Lunes: 9 AM – 6 PM', 'footer.tue': 'Martes: 9 AM – 6 PM', 'footer.wed': 'Miércoles: 9 AM – 6 PM',
    'footer.thu': 'Jueves: 9 AM – 6 PM', 'footer.fri': 'Viernes: 9 AM – 6 PM', 'footer.sat': 'Sábado: Cerrado', 'footer.sun': 'Domingo: Cerrado',
    'footer.links': 'Enlaces Rápidos', 'footer.privacy': 'Política de Privacidad', 'footer.accessibility': 'Accesibilidad',
    'footer.sitemap': 'Mapa del Sitio', 'footer.insurance': 'Seguro',
    'footer.more': 'Más', 'footer.financing': 'Financiamiento', 'footer.savings': 'Plan de Ahorros Dental', 'footer.contact': 'Contacto',
    'footer.rights': 'Todos los derechos reservados.',
    'footer.tagline': 'Confianza • Integridad • Compasión',

    'floating.h': '¿Necesita una Cita?',
    'floating.cta': 'Programar en Línea',
    'mobile.call': 'Llamar', 'mobile.schedule': 'Programar', 'mobile.es': 'English'
  };

  var EN = {};
  document.querySelectorAll('[data-i18n]').forEach(function (el) {
    EN[el.getAttribute('data-i18n')] = el.textContent;
  });

  function apply(lang) {
    var dict = lang === 'es' ? ES : EN;
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key] != null) el.textContent = dict[key];
    });
    document.documentElement.lang = lang === 'es' ? 'es' : 'en';
    document.querySelectorAll('.lang-switch button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
    });
    // "We speak Spanish" chip in the header is redundant once the whole page is
    // already in Spanish, so it only ever shows for English-reading visitors.
    document.querySelectorAll('.header__spanish').forEach(function (el) {
      el.style.display = lang === 'es' ? 'none' : '';
    });
    try { localStorage.setItem('jdb-lang', lang); } catch (e) {}
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-lang]');
    if (!btn) return;
    apply(btn.getAttribute('data-lang'));
    if (typeof window.gtag === 'function' && btn.getAttribute('data-lang') === 'es') {
      window.gtag('event', 'language_es');
    }
    (window.dataLayer = window.dataLayer || []).push({ event: 'language_' + btn.getAttribute('data-lang') });
  });

  // the mobile sticky bar's "Español" button is a quick toggle, not a link
  document.addEventListener('click', function (e) {
    var el = e.target.closest('.mobilebar a[data-track="language_es"]');
    if (!el) return;
    var current = document.documentElement.lang === 'es' ? 'en' : 'es';
    if (current === 'es' || current === 'en') { e.preventDefault(); apply(current); }
  });

  var saved = null;
  try { saved = localStorage.getItem('jdb-lang'); } catch (e) {}
  if (saved === 'es') apply('es');
}());
