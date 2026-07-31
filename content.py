# -*- coding: utf-8 -*-
"""
All landing-page copy, in one place.

Sourced from everythingteethmiami.com (services, doctor bios, team, offers,
Premium Patient Program, insurance/financing, first-visit steps) and from the
practice's public Google Business Profile (5.0 rating, 640+ reviews).

Rule for strings used inside HTML attributes (form messages, open/closed
status, map title): no double quotes. Use typographic quotes in body copy.
"""

# ==========================================================================
#  ENGLISH — shared blocks
# ==========================================================================
EN_DAYS = {
    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
    "fri": "Friday", "sat": "Saturday", "sun": "Sunday", "closed": "Closed",
}

EN_DOCTORS = {
    "docs_script": "Meet the",
    "docs_title": "Faces Behind Your Smile",
    "docs_sub": "A brother-and-sister doctor duo who bring both skill and genuine compassion to every visit.",
    "omar_role": "Co-Founder &middot; General, Implant &amp; Surgical Dentistry",
    "omar_bio": ("Dr. Omar opened his own practice immediately after dental school — an uncommon achievement in "
                 "dentistry — and founded Everything Teeth with his sister to bring high-quality care to their own "
                 "Miami neighborhood."),
    "diana_role": "Co-Founder &middot; General, Invisalign &amp; Botox",
    "diana_bio": ("With over a decade of experience, Dr. Diana focuses on getting to know her patients well and "
                  "helping them smile confidently — treating decay, gum disease, missing teeth and alignment "
                  "concerns with compassion."),
    "edu_fiu": "Undergraduate: Florida International University",
    "edu_lecom": "DMD: Lake Erie College of Osteopathic Medicine (LECOM)",
    "omar_extra": "Advanced training in bone regeneration, dental implants and wisdom tooth extractions",
    "diana_extra": "Extensive study in Invisalign clear aligner therapy and BOTOX",
}

EN_REVIEWS_CORE = {
    "review_source": "Verified patient review",
    "reviews_kicker": "What Our Patients Are Saying",
    "reviews_count": "640+ verified reviews",
    "reviews_meta": "Rated 5.0 on Google by our Miami patients",
    "reviews_cta": "Read Reviews on Google",
}

EN_LOCATION = {
    "loc_title": "Visit Us in Miami",
    "directions": "Get Directions",
    "call_or_text": "Call us",
    "office_hours": "Office hours",
    "open_now": "Open now — call us and we will get you scheduled",
    "closed_now": "Currently closed — send your request and we will call you back",
    "map_title": "Map to Everything Teeth Family Dental, 12819 SW 42nd St, Miami, FL 33175",
    "hours_note": ("Dental emergencies are seen during office hours — call as early in the day as you can. "
                   "If we are closed, leave a message or submit the form and we will reach out as soon as we open."),
}

EN_PAYMENT = {
    "pay_kicker": "Easy Payment Options for Every Smile",
    "pay_title": "Simple, Transparent Savings",
    "pay_sub": "No insurance needed. Pick what fits your family — a new patient offer, a membership plan, or monthly financing.",
    "per_year": "/year",
    "ppp_title": "Premium Patient Program",
    "ppp_lede": "No insurance? Get more from your dental care with a membership built around your needs — one flat yearly fee.",
    "ppp_adult": "Adults",
    "ppp_child": "Children under 14",
    "ppp_family": "Each additional family member",
    "ppp_cta": "Join the Program",
    "ppp_included": "Included at no additional cost",
    "ppp_includes": [
        "<strong>2 cleanings per year</strong> — dental or periodontal maintenance",
        "<strong>Unlimited X-rays</strong> — diagnostic imaging with no annual cap",
        "<strong>Unlimited emergency exams</strong> — whenever you need them",
        "<strong>Oral cancer screenings</strong> — included with your visits",
    ],
    "ppp_discount_head": "25% – 40% off all treatment",
    "ppp_discount_body": ("Applies to restorative &amp; prosthetic work (implants, crowns, bridges, dentures, "
                          "fillings) and specialty &amp; surgical care (endodontics, oral surgery, periodontal treatment)."),
    "ppp_fine": "Excludes periodontal scaling and root planing (deep cleaning).",
    "ins_title": "All PPO Insurance Welcome",
    "ins_copy": "We are an insurance-friendly office and welcome all PPO dental plans. Typical PPO coverage:",
    "cov_prev": "100% Preventive",
    "cov_minor": "80% Minor Restorative",
    "cov_major": "50% Major Restorative",
    "fin_title": "CareCredit® Financing",
    "fin_copy": ("Flexible financing with low- or no-interest plans for qualified applicants — start treatment now "
                 "and pay over time."),
    "inhouse_title": "In-House Options",
    "inhouse_copy": ("In-house financing and our Premium Patient Program keep quality care accessible — "
                     "no dental insurance required."),
    "pay_disclaimer": ("Please call our office to confirm your specific plan is accepted. Offers cannot be combined "
                       "with insurance benefits. Financing subject to credit approval."),
}

EN_FORM = {
    "language": "Language",
    "header_call_label": "Call our Miami office",
    "call_now": "Call Now",
    "call_display": "Call (305) 404-6659",
    "header_book": "Book Appointment",
    "mobile_book": "Book Appointment",
    "err_required": "This field is required.",
    "err_phone": "Please enter a valid phone number.",
    "err_email": "Please enter a valid email address.",
    "form_sending": "Sending…",
    "f_name": "Full name",
    "f_name_ph": "Your name",
    "f_phone": "Phone number",
    "f_email": "Email",
    "f_email_ph": "you@email.com",
    "f_service": "What do you need?",
    "f_service_ph": "Select a service…",
    "rights": "All rights reserved.",
    "legal": ("Offers cannot be combined with insurance benefits. Financing subject to credit approval. "
              "This page is an advertisement and is not a substitute for professional dental advice."),
    "hours_short": "Mon/Wed/Thu 10:30–6:30 &middot; Fri 7:30–3:30",
}

# ==========================================================================
#  SPANISH — shared blocks
# ==========================================================================
ES_DAYS = {
    "mon": "Lunes", "tue": "Martes", "wed": "Miércoles", "thu": "Jueves",
    "fri": "Viernes", "sat": "Sábado", "sun": "Domingo", "closed": "Cerrado",
}

ES_DOCTORS = {
    "docs_script": "Conozca a",
    "docs_title": "Quienes Cuidan Su Sonrisa",
    "docs_sub": "Un dúo de hermanos dentistas que aportan destreza y una compasión genuina en cada visita.",
    "omar_role": "Cofundador &middot; Odontología General, Implantes y Cirugía",
    "omar_bio": ("El Dr. Omar abrió su propia clínica inmediatamente después de graduarse — algo poco común en la "
                 "odontología — y fundó Everything Teeth junto a su hermana para llevar atención de alta calidad a "
                 "su propio vecindario de Miami."),
    "diana_role": "Cofundadora &middot; Odontología General, Invisalign y Botox",
    "diana_bio": ("Con más de una década de experiencia, la Dra. Diana se enfoca en conocer bien a sus pacientes y "
                  "ayudarlos a sonreír con confianza — tratando caries, enfermedad de las encías, dientes faltantes "
                  "y problemas de alineación con mucha compasión."),
    "edu_fiu": "Licenciatura: Florida International University",
    "edu_lecom": "DMD: Lake Erie College of Osteopathic Medicine (LECOM)",
    "omar_extra": "Formación avanzada en regeneración ósea, implantes dentales y extracción de muelas del juicio",
    "diana_extra": "Amplia formación en alineadores transparentes Invisalign y BOTOX",
}

ES_REVIEWS_CORE = {
    "review_source": "Reseña verificada de paciente",
    "reviews_kicker": "Lo Que Dicen Nuestros Pacientes",
    "reviews_count": "Más de 640 reseñas verificadas",
    "reviews_meta": "Calificación 5.0 en Google por nuestros pacientes de Miami",
    "reviews_cta": "Ver Reseñas en Google",
}

ES_LOCATION = {
    "loc_title": "Visítenos en Miami",
    "directions": "Cómo Llegar",
    "call_or_text": "Llámenos",
    "office_hours": "Horario de atención",
    "open_now": "Abierto ahora — llámenos y le damos una cita",
    "closed_now": "Cerrado en este momento — envíe su solicitud y le llamamos",
    "map_title": "Mapa hacia Everything Teeth Family Dental, 12819 SW 42nd St, Miami, FL 33175",
    "hours_note": ("Atendemos emergencias dentales durante el horario de oficina — llame lo más temprano posible. "
                   "Si estamos cerrados, deje un mensaje o envíe el formulario y le contactaremos al abrir."),
}

ES_PAYMENT = {
    "pay_kicker": "Opciones de Pago Fáciles para Cada Sonrisa",
    "pay_title": "Ahorros Simples y Transparentes",
    "pay_sub": "No necesita seguro. Elija lo que mejor le convenga: una oferta de paciente nuevo, un plan de membresía o financiamiento mensual.",
    "per_year": "/año",
    "ppp_title": "Programa de Paciente Premium",
    "ppp_lede": "¿Sin seguro dental? Aproveche más su atención con una membresía hecha a su medida — una sola cuota anual.",
    "ppp_adult": "Adultos",
    "ppp_child": "Niños menores de 14 años",
    "ppp_family": "Cada familiar adicional",
    "ppp_cta": "Únase al Programa",
    "ppp_included": "Incluido sin costo adicional",
    "ppp_includes": [
        "<strong>2 limpiezas al año</strong> — limpieza dental o mantenimiento periodontal",
        "<strong>Radiografías ilimitadas</strong> — sin límite anual de imágenes diagnósticas",
        "<strong>Exámenes de emergencia ilimitados</strong> — cuando los necesite",
        "<strong>Detección de cáncer oral</strong> — incluida en sus visitas",
    ],
    "ppp_discount_head": "25% – 40% de descuento en todo tratamiento",
    "ppp_discount_body": ("Aplica a trabajos restaurativos y protésicos (implantes, coronas, puentes, dentaduras, "
                          "empastes) y a atención especializada y quirúrgica (endodoncia, cirugía oral, tratamiento periodontal)."),
    "ppp_fine": "No incluye raspado y alisado radicular (limpieza profunda).",
    "ins_title": "Aceptamos Todos los Seguros PPO",
    "ins_copy": "Somos una oficina amigable con los seguros y aceptamos todos los planes dentales PPO. Cobertura PPO típica:",
    "cov_prev": "100% Preventivo",
    "cov_minor": "80% Restaurativo Menor",
    "cov_major": "50% Restaurativo Mayor",
    "fin_title": "Financiamiento CareCredit®",
    "fin_copy": ("Financiamiento flexible con planes de bajo o cero interés para solicitantes calificados — "
                 "comience su tratamiento hoy y pague poco a poco."),
    "inhouse_title": "Opciones Internas",
    "inhouse_copy": ("Nuestro financiamiento interno y el Programa de Paciente Premium hacen accesible la atención "
                     "de calidad — sin necesidad de seguro dental."),
    "pay_disclaimer": ("Por favor llame a la oficina para confirmar que su plan es aceptado. Las ofertas no se pueden "
                       "combinar con beneficios de seguro. El financiamiento está sujeto a aprobación de crédito."),
}

ES_FORM = {
    "language": "Idioma",
    "header_call_label": "Llame a nuestra oficina",
    "call_now": "Llamar Ahora",
    "call_display": "Llame al (305) 404-6659",
    "header_book": "Pedir Cita",
    "mobile_book": "Pedir Cita",
    "err_required": "Este campo es obligatorio.",
    "err_phone": "Por favor ingrese un número de teléfono válido.",
    "err_email": "Por favor ingrese un correo electrónico válido.",
    "form_sending": "Enviando…",
    "f_name": "Nombre completo",
    "f_name_ph": "Su nombre",
    "f_phone": "Número de teléfono",
    "f_email": "Correo electrónico",
    "f_email_ph": "usted@correo.com",
    "f_service": "¿Qué necesita?",
    "f_service_ph": "Seleccione un servicio…",
    "rights": "Todos los derechos reservados.",
    "legal": ("Las ofertas no se pueden combinar con beneficios de seguro. Financiamiento sujeto a aprobación de "
              "crédito. Esta página es un anuncio publicitario y no sustituye el consejo dental profesional."),
    "hours_short": "Lun/Mié/Jue 10:30–6:30 &middot; Vie 7:30–3:30",
}

# ==========================================================================
#  Real patient reviews (from the practice website + Google Business Profile)
# ==========================================================================
REVIEWS_EN = [
    ("Teagan A.",
     "“This place is amazing!! I haven’t been to the dentist in over two years due to anxiety. I went to a place down "
     "the street and they told me it was going to be over 1,000 dollars and scared me. So I came here today instead, "
     "everyone I met was so so nice and kind. The hygienist explained everything to me and told me I could take breaks "
     "if needed. No one made me feel bad or discouraged me. I would recommend this place over and over again!”"),
    ("Linda Y.",
     "“Had a wonderful experience at ‘Everything Teeth!’ Staff is so caring &amp; welcoming. Loved that everyone "
     "explained all my options. Had a cleaning &amp; bonding. Dr Omar did an awesome job. Felt very confident in his "
     "hands. Excellent job! Thank you Doctor &amp; awesome staff. I will recommend your practice with 5 stars!”"),
    ("Armando V.",
     "“I was looking for a new dentist because my previous office was just not up to the standards I expect from a "
     "healthcare provider. The team at Everything Teeth was everything I expected and more. From the receptionist to "
     "Tanya the hygienist and Dr. Diana Morell were all kind and knowledgeable.”"),
]

REVIEWS_ES = [
    ("María Castellanos",
     "“Muy buen trato y profesionales de excelencia. Quedé muy satisfecha.”"),
    ("Alexander Monje",
     "“Everything Teeth provides great care and has great patient service. Definitely recommend.” "
     "<em>(Everything Teeth brinda excelente atención y un gran servicio al paciente. Lo recomiendo totalmente.)</em>"),
    ("Teagan A.",
     "“Este lugar es increíble. Llevaba más de dos años sin ir al dentista por ansiedad. Aquí todos fueron muy "
     "amables. La higienista me explicó todo y me dijo que podía tomar descansos si los necesitaba. Nadie me hizo "
     "sentir mal. Lo recomendaría una y otra vez.” <em>(Traducido de la reseña original en inglés.)</em>"),
]

# ==========================================================================
#  GENERAL DENTIST — ENGLISH
# ==========================================================================
GENERAL_EN = {
    **EN_FORM, **EN_DAYS, **EN_DOCTORS, **EN_REVIEWS_CORE, **EN_LOCATION, **EN_PAYMENT,

    "title": "General Dentist in Miami, FL | $159 New Patient Visit | Everything Teeth Family Dental",
    "description": ("Complete general dentistry in Miami, FL — cleanings, fillings, crowns, implants and more, all "
                    "under one roof. $159 new patient exam &amp; X-rays. 5.0 stars from 640+ patients. Se habla "
                    "español. Call (305) 404-6659."),

    # ---- Hero ----
    "hero_eyebrow": "General &amp; Family Dentistry &middot; Miami, FL 33175",
    "hero_h1": "All Your Family’s Dental Care",
    "hero_h1_accent": "Under One Roof",
    "hero_sub": ("From routine cleanings to fillings, crowns, implants and Invisalign — Dr. Omar and Dr. Diana Morell "
                 "deliver comprehensive dentistry in a warm, judgment-free office. No running across town. "
                 "No unnecessary referrals."),
    "hero_points": [
        "Comprehensive care — no referrals needed",
        "All PPO dental insurance welcome",
        "Implants &amp; Invisalign from $199/month",
        "Se habla español — fully bilingual team",
    ],
    "hero_cta": "Request My Appointment",
    "hero_offer_title": "New Patient Visit",
    "hero_offer_copy": "Exam &amp; X-rays included — plus a free cleaning for qualifying patients.",
    "hero_rating": "from 640+ verified patient reviews",

    # ---- Form ----
    "form_title": "Request Your Appointment",
    "form_note": "We just need to ask you a few quick questions — our team calls you back to confirm.",
    "form_ok": "Thank you! Your request has been received — our team will call you shortly to confirm your appointment.",
    "form_fallback": "Thanks! To lock in the soonest appointment, please call us now at (305) 404-6659.",
    "form_legal": "By submitting you agree to be contacted by phone, text or email about your appointment. Prefer to talk now? Call",
    "f_submit": "Get My Appointment Time",
    "form_options": [
        "New patient exam &amp; cleaning", "Teeth cleaning / check-up", "Fillings or tooth pain",
        "Crowns, bridges or dentures", "Dental implants", "Root canal treatment",
        "Wisdom teeth removal", "Invisalign / clear aligners", "Teeth whitening / veneers",
        "Children’s dentistry", "Something else",
    ],

    # ---- Trust ----
    "trust": [
        ("star", "5.0 Star Rated", "640+ patient reviews"),
        ("users", "Brother &amp; Sister Doctors", "Dr. Omar &amp; Dr. Diana Morell"),
        ("card", "All PPO Insurance", "Plus CareCredit® financing"),
        ("clock", "Early &amp; Late Hours", "Built around your schedule"),
        ("globe", "Se Habla Español", "Bilingual team, English &amp; Spanish"),
    ],

    # ---- Services ----
    "svc_kicker": "Complete General Dentistry",
    "svc_title": "Comprehensive Dental Care for Every Smile",
    "svc_sub": "Quality dental services for patients of all ages, all under one roof — so you never get referred out unnecessarily.",
    "svc_cta": "Book My Visit",
    "service_groups": [
        {
            "icon": "icon-preventive-care.svg",
            "title": "Preventive Dentistry",
            "blurb": "Protect your oral health with regular exams, cleanings and preventive treatments to keep your smile healthy.",
            "items": [
                ("Teeth Cleaning", "Gentle professional cleanings that remove plaque and tartar buildup."),
                ("Dental Sealants", "A protective barrier that shields molars from decay — ideal for kids."),
                ("Gum Disease Treatment", "Targeted periodontal therapy to stop bleeding, swollen gums."),
                ("Oral Cancer Screenings", "Quick, painless screening included with your routine exam."),
                ("Children’s Dentist", "Friendly, patient care that helps kids feel safe in the chair."),
                ("Family Dentist", "One office for every generation — book the whole family together."),
            ],
        },
        {
            "icon": "img-Dental-Implants.svg",
            "title": "Restorative Dentistry",
            "blurb": "Restore damaged or missing teeth with personalized treatments that improve function, health and appearance.",
            "items": [
                ("Dental Fillings", "Tooth-coloured fillings that repair cavities and blend right in."),
                ("Dental Implants", "Permanent tooth replacement — as low as $199/month."),
                ("Root Canal Treatment", "Save an infected tooth and end the pain, comfortably."),
                ("Dental Bridges", "Close the gap and restore your bite with a fixed bridge."),
                ("Dentures", "Natural-looking full and partial dentures made to fit you."),
                ("Wisdom Teeth Removal", "In-house extractions — no referral to an outside surgeon."),
            ],
        },
        {
            "icon": "img-Invisalign.svg",
            "title": "Cosmetic Dentistry",
            "blurb": "Enhance your smile with treatments designed to improve the appearance of your teeth and boost confidence.",
            "items": [
                ("Invisalign®", "Clear aligners that straighten discreetly — from $199/month."),
                ("Teeth Whitening", "Professional whitening for a noticeably brighter smile."),
                ("Porcelain Veneers", "Reshape chipped, stained or uneven teeth beautifully."),
                ("Metal-Free Crowns", "Strong, natural-looking crowns with no dark metal line."),
                ("Dental Bonding", "Fast, affordable repair for small chips and gaps."),
                ("Botox®", "Administered by Dr. Diana, who studied BOTOX extensively."),
            ],
        },
        {
            "icon": "img-Emergency-Care.svg",
            "title": "Comfort &amp; Urgent Care",
            "blurb": "Sedation options for anxious patients, plus prompt help when something goes wrong.",
            "items": [
                ("Sedation Dentistry", "Relax during treatment with safe sedation designed to reduce anxiety."),
                ("Emergency Dentistry", "Prompt care for toothaches, broken teeth and dental injuries."),
                ("Digital X-Rays &amp; Scans", "Digital imaging and impressions — less radiation, no goopy moulds."),
            ],
        },
    ],

    # ---- Why us ----
    "why_kicker": "How We Are Different",
    "why_title": "Excellence in Dentistry, Right Here in Miami",
    "why_sub": "Everything Teeth was built around one idea — treat every patient the way we would treat family.",
    "why": [
        ("Everything Under One Roof", "From cleanings to implants to cosmetics — so you never get referred out unnecessarily."),
        ("A Judgment-Free Office", "A warm environment where patients are treated like family from the moment they walk in."),
        ("Hours That Fit Your Life", "Extended hours designed around your schedule, not ours — including early Friday mornings."),
        ("Transparent Treatment Plans", "We explain everything clearly before we begin — no surprise costs at checkout."),
        ("Care, Not Upselling", "Patient-centred care that prioritises your long-term oral health, not unnecessary procedures."),
        ("Modern Technology", "Digital X-rays with reduced radiation and digital impressions for accurate 3D models."),
    ],

    # ---- Team ----
    "team_kicker": "Our Team",
    "team_title": "Rockstars Committed to Your Oral Health",
    "team_sub": "A support team that knows your name, your history and your comfort level.",
    "team_photo_alt": "The Everything Teeth Family Dental team in Miami",
    "team": [
        ("Tanya", "Registered Dental Hygienist — licensed from the University of Florida"),
        ("Leyanis", "Dental Assistant — helps patients overcome dental anxiety"),
        ("Yanet", "Dental Assistant — with the office since it opened"),
        ("Tania Torno", "Patient Care Coordinator &amp; Dental Assistant"),
        ("Elsie", "Scheduling Coordinator — your first friendly hello"),
        ("Bilingual Team", "Every team member speaks English and Spanish"),
    ],

    # ---- Offers ----
    "offers": [
        {"title": "New Patient Visit", "amount": "159", "featured": True, "tag": "Most Popular",
         "copy": "Exam &amp; X-rays — plus a free cleaning for qualifying patients.",
         "cta": "Claim Offer", "fine": "New patients only."},
        {"title": "Limited Exam", "amount": "75",
         "copy": "A focused exam on one problem area — perfect if something specific hurts.",
         "cta": "Book Exam", "fine": "Problem-focused visit."},
        {"title": "Dental Implants", "amount": "199", "per": "/mo",
         "copy": "Replace missing teeth for good — starting with a free consultation.",
         "cta": "Free Consult", "fine": "Credit approval required."},
        {"title": "Invisalign®", "amount": "199", "per": "/mo",
         "copy": "Straighten your smile discreetly — free consultation included.",
         "cta": "Free Consult", "fine": "Credit approval required."},
    ],

    "reviews": REVIEWS_EN,
    "reviews_title": "640+ Miami Neighbours, 5.0 Stars",

    # ---- First visit ----
    "steps_kicker": "New Patients Welcome",
    "steps_title": "What Your First Visit Looks Like",
    "steps_sub": "Simple, unhurried and fully explained — here’s exactly what to expect.",
    "steps": [
        ("Warm Welcome", "We greet you before having you fill out your new patient paperwork — or complete it at home to save time."),
        ("X-Rays &amp; History", "We escort you to the treatment room and capture digital X-rays while discussing your oral health history."),
        ("Meet Your Dentist", "Dr. Omar or Dr. Diana performs a thorough examination and explains everything clearly before anything begins."),
        ("Your Cleaning", "Your hygienist completes the appointment with a gentle cleaning — take breaks any time you need one."),
    ],

    "loc_cta": "Request an Appointment",

    # ---- Final CTA ----
    "final_title": "Ready for a Dentist Who Treats You Like Family?",
    "final_copy": ("New patients and emergency appointments are always welcome. Start with a $159 new patient visit — "
                   "exam and X-rays included, plus a free cleaning for qualifying patients."),
    "final_points": [
        "All PPO dental insurance welcome",
        "Premium Patient Program from $175/year",
        "Implants &amp; Invisalign from $199/month",
        "Se habla español — bilingual team",
    ],
    "final_secondary": "Request Online",
}

# ==========================================================================
#  GENERAL DENTIST — SPANISH
# ==========================================================================
GENERAL_ES = {
    **ES_FORM, **ES_DAYS, **ES_DOCTORS, **ES_REVIEWS_CORE, **ES_LOCATION, **ES_PAYMENT,

    "title": "Dentista General en Miami, FL | Visita de Paciente Nuevo $159 | Everything Teeth",
    "description": ("Odontología general completa en Miami, FL — limpiezas, empastes, coronas, implantes y más, todo "
                    "bajo un mismo techo. Examen y radiografías por $159. 5.0 estrellas de más de 640 pacientes. "
                    "Se habla español. Llame al (305) 404-6659."),

    "hero_eyebrow": "Odontología General y Familiar &middot; Miami, FL 33175",
    "hero_h1": "Toda la Atención Dental de Su Familia",
    "hero_h1_accent": "Bajo un Mismo Techo",
    "hero_sub": ("Desde limpiezas de rutina hasta empastes, coronas, implantes e Invisalign — el Dr. Omar y la Dra. "
                 "Diana Morell ofrecen odontología integral en un ambiente cálido y sin juicios. Sin manejar por toda "
                 "la ciudad. Sin referencias innecesarias."),
    "hero_points": [
        "Atención integral — sin referencias a otras clínicas",
        "Aceptamos todos los seguros dentales PPO",
        "Implantes e Invisalign desde $199 al mes",
        "Equipo totalmente bilingüe — se habla español",
    ],
    "hero_cta": "Solicitar Mi Cita",
    "hero_offer_title": "Visita de Paciente Nuevo",
    "hero_offer_copy": "Incluye examen y radiografías — más una limpieza gratis para pacientes que califiquen.",
    "hero_rating": "de más de 640 reseñas verificadas de pacientes",

    "form_title": "Solicite Su Cita",
    "form_note": "Solo necesitamos hacerle unas preguntas rápidas — nuestro equipo le llama para confirmar.",
    "form_ok": "¡Gracias! Hemos recibido su solicitud — nuestro equipo le llamará en breve para confirmar su cita.",
    "form_fallback": "¡Gracias! Para asegurar la cita más pronta, llámenos ahora al (305) 404-6659.",
    "form_legal": "Al enviar acepta ser contactado por teléfono, mensaje o correo sobre su cita. ¿Prefiere hablar ahora? Llame al",
    "f_submit": "Reservar Mi Cita",
    "form_options": [
        "Examen y limpieza de paciente nuevo", "Limpieza dental / chequeo", "Empastes o dolor de muela",
        "Coronas, puentes o dentaduras", "Implantes dentales", "Tratamiento de conducto",
        "Extracción de muelas del juicio", "Invisalign / alineadores transparentes",
        "Blanqueamiento / carillas", "Odontología infantil", "Otra cosa",
    ],

    "trust": [
        ("star", "Calificación 5.0", "Más de 640 reseñas"),
        ("users", "Dentistas Hermanos", "Dr. Omar y Dra. Diana Morell"),
        ("card", "Seguros PPO", "Más financiamiento CareCredit®"),
        ("clock", "Horarios Amplios", "Pensados para su agenda"),
        ("globe", "Se Habla Español", "Equipo bilingüe, inglés y español"),
    ],

    "svc_kicker": "Odontología General Completa",
    "svc_title": "Atención Dental Integral para Cada Sonrisa",
    "svc_sub": "Servicios dentales de calidad para pacientes de todas las edades, todo bajo un mismo techo — para que nunca lo refieran innecesariamente.",
    "svc_cta": "Reservar Mi Visita",
    "service_groups": [
        {
            "icon": "icon-preventive-care.svg",
            "title": "Odontología Preventiva",
            "blurb": "Proteja su salud bucal con exámenes regulares, limpiezas y tratamientos preventivos que mantienen su sonrisa sana.",
            "items": [
                ("Limpieza Dental", "Limpiezas profesionales y suaves que eliminan placa y sarro."),
                ("Selladores Dentales", "Una barrera protectora que resguarda las muelas de las caries — ideal para niños."),
                ("Tratamiento de Encías", "Terapia periodontal para detener el sangrado y la inflamación."),
                ("Detección de Cáncer Oral", "Evaluación rápida e indolora incluida en su examen de rutina."),
                ("Dentista Infantil", "Atención amable y paciente que ayuda a los niños a sentirse seguros."),
                ("Dentista Familiar", "Una sola oficina para toda la familia — agenden juntos."),
            ],
        },
        {
            "icon": "img-Dental-Implants.svg",
            "title": "Odontología Restaurativa",
            "blurb": "Restaure dientes dañados o faltantes con tratamientos personalizados que mejoran la función, la salud y la apariencia.",
            "items": [
                ("Empastes Dentales", "Empastes del color del diente que reparan caries y pasan desapercibidos."),
                ("Implantes Dentales", "Reemplazo permanente de dientes — desde $199 al mes."),
                ("Tratamiento de Conducto", "Salve un diente infectado y termine con el dolor, cómodamente."),
                ("Puentes Dentales", "Cierre el espacio y recupere su mordida con un puente fijo."),
                ("Dentaduras", "Dentaduras completas y parciales de apariencia natural, hechas a su medida."),
                ("Muelas del Juicio", "Extracciones en la misma oficina — sin referirlo a un cirujano externo."),
            ],
        },
        {
            "icon": "img-Invisalign.svg",
            "title": "Odontología Cosmética",
            "blurb": "Realce su sonrisa con tratamientos diseñados para mejorar la apariencia de sus dientes y aumentar su confianza.",
            "items": [
                ("Invisalign®", "Alineadores transparentes que enderezan con discreción — desde $199 al mes."),
                ("Blanqueamiento Dental", "Blanqueamiento profesional para una sonrisa notablemente más brillante."),
                ("Carillas de Porcelana", "Transforme dientes astillados, manchados o desiguales."),
                ("Coronas Sin Metal", "Coronas resistentes y naturales, sin línea metálica oscura."),
                ("Resinas Estéticas", "Reparación rápida y económica de pequeñas fracturas y espacios."),
                ("Botox®", "Aplicado por la Dra. Diana, con amplia formación en BOTOX."),
            ],
        },
        {
            "icon": "img-Emergency-Care.svg",
            "title": "Comodidad y Urgencias",
            "blurb": "Opciones de sedación para pacientes con ansiedad, más atención pronta cuando algo sale mal.",
            "items": [
                ("Sedación Dental", "Relájese durante el tratamiento con sedación segura que reduce la ansiedad."),
                ("Odontología de Emergencia", "Atención pronta para dolores de muela, dientes rotos y lesiones dentales."),
                ("Radiografías Digitales", "Imágenes y moldes digitales — menos radiación, sin pastas incómodas."),
            ],
        },
    ],

    "why_kicker": "Lo Que Nos Hace Diferentes",
    "why_title": "Excelencia en Odontología, Aquí Mismo en Miami",
    "why_sub": "Everything Teeth nació de una sola idea: tratar a cada paciente como trataríamos a nuestra propia familia.",
    "why": [
        ("Todo Bajo un Mismo Techo", "Desde limpiezas hasta implantes y estética — para que nunca lo refieran innecesariamente."),
        ("Una Oficina Sin Juicios", "Un ambiente cálido donde tratamos a los pacientes como familia desde que entran por la puerta."),
        ("Horarios Que Se Ajustan a Usted", "Horarios amplios pensados para su agenda, no la nuestra — incluidas las mañanas del viernes."),
        ("Planes de Tratamiento Claros", "Le explicamos todo con claridad antes de empezar — sin costos sorpresa al final."),
        ("Cuidado, No Ventas", "Atención centrada en su salud bucal a largo plazo, no en procedimientos innecesarios."),
        ("Tecnología Moderna", "Radiografías digitales con menos radiación e impresiones digitales para modelos 3D precisos."),
    ],

    "team_kicker": "Nuestro Equipo",
    "team_title": "Un Equipo Comprometido con Su Salud Bucal",
    "team_sub": "Un equipo que conoce su nombre, su historia y su nivel de comodidad.",
    "team_photo_alt": "El equipo de Everything Teeth Family Dental en Miami",
    "team": [
        ("Tanya", "Higienista Dental Registrada — titulada por la University of Florida"),
        ("Leyanis", "Asistente Dental — ayuda a los pacientes a superar la ansiedad dental"),
        ("Yanet", "Asistente Dental — con la oficina desde que abrió"),
        ("Tania Torno", "Coordinadora de Atención al Paciente y Asistente Dental"),
        ("Elsie", "Coordinadora de Citas — su primer saludo amable"),
        ("Equipo Bilingüe", "Todo el equipo habla inglés y español"),
    ],

    "offers": [
        {"title": "Visita de Paciente Nuevo", "amount": "159", "featured": True, "tag": "Más Popular",
         "copy": "Examen y radiografías — más limpieza gratis para pacientes que califiquen.",
         "cta": "Aprovechar Oferta", "fine": "Solo pacientes nuevos."},
        {"title": "Examen Limitado", "amount": "75",
         "copy": "Examen enfocado en una sola área con problema — ideal si algo específico le duele.",
         "cta": "Reservar Examen", "fine": "Visita enfocada al problema."},
        {"title": "Implantes Dentales", "amount": "199", "per": "/mes",
         "copy": "Reemplace dientes faltantes de forma definitiva — con consulta gratuita.",
         "cta": "Consulta Gratis", "fine": "Sujeto a aprobación de crédito."},
        {"title": "Invisalign®", "amount": "199", "per": "/mes",
         "copy": "Enderece su sonrisa con discreción — consulta gratuita incluida.",
         "cta": "Consulta Gratis", "fine": "Sujeto a aprobación de crédito."},
    ],

    "reviews": REVIEWS_ES,
    "reviews_title": "Más de 640 Vecinos de Miami, 5.0 Estrellas",

    "steps_kicker": "Pacientes Nuevos Bienvenidos",
    "steps_title": "Cómo Es Su Primera Visita",
    "steps_sub": "Sencilla, sin prisas y totalmente explicada — esto es exactamente lo que puede esperar.",
    "steps": [
        ("Bienvenida Cálida", "Lo recibimos antes de llenar su documentación de paciente nuevo — o complétela en casa para ahorrar tiempo."),
        ("Radiografías e Historial", "Lo acompañamos a la sala de tratamiento y tomamos radiografías digitales mientras conversamos sobre su historial bucal."),
        ("Conozca a Su Dentista", "El Dr. Omar o la Dra. Diana realiza un examen completo y le explica todo con claridad antes de comenzar."),
        ("Su Limpieza", "Su higienista termina la cita con una limpieza suave — puede tomar descansos cuando lo necesite."),
    ],

    "loc_cta": "Solicitar una Cita",

    "final_title": "¿Listo para un Dentista Que lo Trate Como Familia?",
    "final_copy": ("Siempre damos la bienvenida a pacientes nuevos y citas de emergencia. Comience con la visita de "
                   "paciente nuevo por $159 — incluye examen y radiografías, más limpieza gratis para quienes califiquen."),
    "final_points": [
        "Aceptamos todos los seguros dentales PPO",
        "Programa de Paciente Premium desde $175 al año",
        "Implantes e Invisalign desde $199 al mes",
        "Se habla español — equipo bilingüe",
    ],
    "final_secondary": "Solicitar en Línea",
}

# ==========================================================================
#  EMERGENCY DENTIST — ENGLISH
# ==========================================================================
EMERGENCY_EN = {
    **EN_FORM, **EN_DAYS, **EN_DOCTORS, **EN_REVIEWS_CORE, **EN_LOCATION, **EN_PAYMENT,

    "title": "Emergency Dentist in Miami, FL | Same-Day Tooth Pain Relief | Call (305) 404-6659",
    "description": ("In pain right now? Emergency dentist in Miami, FL for toothaches, broken and knocked-out teeth, "
                    "swelling and lost crowns. $75 limited exam. 5.0 stars, 640+ reviews. Se habla español. "
                    "Call (305) 404-6659."),

    # ---- Hero ----
    "hero_eyebrow": "Emergency Dental Care &middot; Miami, FL 33175",
    "hero_h1": "Dental Emergency in Miami?",
    "hero_h1_accent": "Call Us Now.",
    "hero_sub": ("Severe toothache, broken tooth, swelling or a knocked-out tooth — don’t wait it out. Call and we "
                 "will work you into the schedule as quickly as possible. Emergency appointments are always welcome, "
                 "and our whole team speaks Spanish."),
    "hero_points": [
        "Emergency exams the same day when you call early",
        "Sedation available for anxious patients",
        "$75 limited exam on the problem area",
        "All PPO insurance &amp; CareCredit® accepted",
    ],
    "hero_call_cta": "Call (305) 404-6659",
    "hero_cta2": "Request a Callback",
    "hero_offer_title": "Emergency Limited Exam",
    "hero_offer_copy": "A focused exam and diagnosis on the tooth that hurts — so we can stop the pain fast.",
    "hero_rating": "from 640+ verified patient reviews",

    # ---- Form ----
    "form_title": "Need Help Fast?",
    "form_note": "Send this and we call you back — or skip the form and call (305) 404-6659 now.",
    "form_ok": "Got it — we have your request. Our team is calling you back shortly. If the pain is severe, call us now at (305) 404-6659.",
    "form_fallback": "For the fastest help with a dental emergency, please call us right now at (305) 404-6659.",
    "form_legal": "By submitting you agree to be contacted by phone, text or email. For urgent pain, calling is fastest —",
    "f_submit": "Call Me Back Now",
    "f_service": "What is happening?",
    "f_service_ph": "Select what is happening…",
    "form_options": [
        "Severe toothache", "Broken or chipped tooth", "Knocked-out tooth", "Lost filling or crown",
        "Swelling or abscess", "Wisdom tooth pain", "Bleeding gums", "Broken denture",
        "Injury from an accident", "Something else",
    ],

    # ---- Trust ----
    "trust": [
        ("bolt", "Emergency Appointments", "Welcome every day we are open"),
        ("star", "5.0 Star Rated", "640+ patient reviews"),
        ("shield", "Sedation Available", "Comfortable care for anxious patients"),
        ("card", "All PPO Insurance", "Plus CareCredit® financing"),
        ("globe", "Se Habla Español", "Bilingual team, English &amp; Spanish"),
    ],

    # ---- Conditions ----
    "cond_kicker": "We Treat Every Dental Emergency",
    "cond_title": "What Brought You Here Today?",
    "cond_sub": "Get prompt care for toothaches, broken teeth, dental injuries and other urgent dental emergencies — all treated in-house.",
    "conditions": [
        ("bolt", "Severe Toothache", "Throbbing, constant pain or sensitivity that keeps you up at night."),
        ("tooth", "Broken or Chipped Tooth", "A cracked, fractured or chipped tooth — we repair and protect it."),
        ("warning", "Knocked-Out Tooth", "Time matters. Keep the tooth moist and call us immediately."),
        ("shield", "Lost Filling or Crown", "An exposed tooth is vulnerable — we re-seal it before it worsens."),
        ("hospital", "Abscess or Swelling", "A dental infection needs treatment fast. Do not wait this one out."),
        ("tooth", "Wisdom Tooth Pain", "Impacted or infected wisdom teeth removed in-house, no outside referral."),
        ("drop", "Bleeding Gums", "Persistent bleeding or gum pain assessed and treated the same visit."),
        ("kit", "Broken Denture", "Cracked, loose or broken dentures repaired so you can eat and speak again."),
    ],

    # ---- First aid ----
    "fa_kicker": "While You Are on Your Way",
    "fa_title": "What To Do Right Now",
    "fa_sub": "A few simple steps can protect the tooth and take the edge off the pain before you reach us.",
    "firstaid": [
        ("Call Us First", "Call (305) 404-6659 and describe what happened. That lets us prepare the room before you arrive."),
        ("Ease the Pain", "Rinse gently with warm salt water and hold a cold compress against the outside of your cheek — 15 minutes on, 15 minutes off."),
        ("Protect the Tooth", "If a tooth was knocked out, handle it by the crown, never the root, and keep it in milk or saliva until you reach us."),
        ("Come Straight In", "Head to 12819 SW 42nd St, Miami. We keep time open for emergencies and will take it from there."),
    ],
    "fa_warning": ("<strong>When to go to the ER instead:</strong> if you have swelling that affects your breathing or "
                   "swallowing, uncontrolled bleeding, a possible broken jaw, or trauma from a serious accident, go to "
                   "the nearest hospital emergency room or call 911 first — then call us for the dental follow-up."),

    # ---- Why us ----
    "why_kicker": "Why Miami Trusts Us in an Emergency",
    "why_title": "Relief First. Answers Second. No Judgment, Ever.",
    "why_sub": "We know a dental emergency is stressful. Here is how we make it easier.",
    "why": [
        ("Seen, Not Shuffled", "We hold time in the schedule for urgent patients — call early in the day for the best chance of being seen the same day."),
        ("Treated In-House", "Extractions, root canals, crowns and implants are all done here — no waiting on an outside specialist referral."),
        ("Sedation for Anxiety", "Safe sedation options designed to reduce anxiety and improve comfort during urgent treatment."),
        ("The Price Before We Start", "Transparent treatment planning — we explain what it costs and what it involves before we begin."),
        ("Payment That Works", "All PPO insurance, CareCredit® financing and in-house options so cost never delays your care."),
        ("Bilingual Team", "Every member of our team speaks English and Spanish — explain your pain in the words you think in."),
    ],

    "reviews": REVIEWS_EN,
    "reviews_title": "Patients Who Came In Hurting — and Left Smiling",

    # ---- Offers (emergency-first ordering) ----
    "pay_title": "Emergency Care You Can Afford",
    "pay_sub": "Pain should not wait for payday. These are all the ways we make urgent treatment affordable.",
    "offers": [
        {"title": "Emergency Limited Exam", "amount": "75", "featured": True, "tag": "Start Here", "call": True,
         "copy": "A focused exam and diagnosis on the tooth that is hurting.",
         "cta": "Call to Book", "fine": "Problem-focused visit."},
        {"title": "New Patient Visit", "amount": "159",
         "copy": "Full exam &amp; X-rays — plus a free cleaning for qualifying patients.",
         "cta": "Claim Offer", "fine": "New patients only."},
        {"title": "Dental Implants", "amount": "199", "per": "/mo",
         "copy": "Lost a tooth for good? Replace it permanently — free consultation.",
         "cta": "Free Consult", "fine": "Credit approval required."},
        {"title": "Invisalign®", "amount": "199", "per": "/mo",
         "copy": "Once you are out of pain, straighten your smile discreetly.",
         "cta": "Free Consult", "fine": "Credit approval required."},
    ],

    "loc_cta": "Call (305) 404-6659",

    "final_title": "Don’t Wait Out the Pain.",
    "final_copy": ("Dental problems rarely fix themselves — and they get more expensive the longer they wait. "
                   "One call gets you an answer, a plan and relief."),
    "final_points": [
        "Emergency appointments always welcome",
        "$75 limited exam on the problem area",
        "Sedation available for anxious patients",
        "Se habla español — bilingual team",
    ],
    "final_secondary": "Request a Callback",
}

# ==========================================================================
#  EMERGENCY DENTIST — SPANISH
# ==========================================================================
EMERGENCY_ES = {
    **ES_FORM, **ES_DAYS, **ES_DOCTORS, **ES_REVIEWS_CORE, **ES_LOCATION, **ES_PAYMENT,

    "title": "Dentista de Emergencia en Miami, FL | Alivio del Dolor el Mismo Día | (305) 404-6659",
    "description": ("¿Con dolor ahora mismo? Dentista de emergencia en Miami, FL para dolor de muela, dientes rotos "
                    "o caídos, hinchazón y coronas perdidas. Examen limitado por $75. 5.0 estrellas, más de 640 "
                    "reseñas. Se habla español. Llame al (305) 404-6659."),

    "hero_eyebrow": "Atención Dental de Emergencia &middot; Miami, FL 33175",
    "hero_h1": "¿Emergencia Dental en Miami?",
    "hero_h1_accent": "Llámenos Ahora.",
    "hero_sub": ("Dolor de muela intenso, diente roto, hinchazón o un diente caído por un golpe — no espere a que "
                 "pase. Llame y lo acomodamos en la agenda lo antes posible. Las citas de emergencia siempre son "
                 "bienvenidas y todo nuestro equipo habla español."),
    "hero_points": [
        "Exámenes de emergencia el mismo día si llama temprano",
        "Sedación disponible para pacientes con ansiedad",
        "Examen limitado por $75 sobre el área afectada",
        "Aceptamos seguros PPO y financiamiento CareCredit®",
    ],
    "hero_call_cta": "Llame al (305) 404-6659",
    "hero_cta2": "Solicitar Llamada",
    "hero_offer_title": "Examen Limitado de Emergencia",
    "hero_offer_copy": "Examen y diagnóstico enfocados en el diente que le duele — para detener el dolor rápido.",
    "hero_rating": "de más de 640 reseñas verificadas de pacientes",

    "form_title": "¿Necesita Ayuda Rápido?",
    "form_note": "Envíe esto y le devolvemos la llamada — o llame directamente al (305) 404-6659.",
    "form_ok": "Listo — recibimos su solicitud. Nuestro equipo le llamará en breve. Si el dolor es intenso, llámenos ahora al (305) 404-6659.",
    "form_fallback": "Para atención más rápida en una emergencia dental, llámenos ahora mismo al (305) 404-6659.",
    "form_legal": "Al enviar acepta ser contactado por teléfono, mensaje o correo. Para dolor urgente, llamar es lo más rápido —",
    "f_submit": "Llámenme Ahora",
    "f_service": "¿Qué está pasando?",
    "f_service_ph": "Seleccione qué está pasando…",
    "form_options": [
        "Dolor de muela intenso", "Diente roto o astillado", "Diente caído por un golpe",
        "Empaste o corona perdida", "Hinchazón o absceso", "Dolor de muela del juicio",
        "Encías sangrantes", "Dentadura rota", "Lesión por un accidente", "Otra cosa",
    ],

    "trust": [
        ("bolt", "Citas de Emergencia", "Bienvenidas todos los días que abrimos"),
        ("star", "Calificación 5.0", "Más de 640 reseñas"),
        ("shield", "Sedación Disponible", "Atención cómoda para pacientes con ansiedad"),
        ("card", "Seguros PPO", "Más financiamiento CareCredit®"),
        ("globe", "Se Habla Español", "Equipo bilingüe, inglés y español"),
    ],

    "cond_kicker": "Atendemos Toda Emergencia Dental",
    "cond_title": "¿Qué lo Trae Hoy?",
    "cond_sub": "Atención pronta para dolores de muela, dientes rotos, lesiones dentales y otras urgencias — todo tratado en nuestra propia oficina.",
    "conditions": [
        ("bolt", "Dolor de Muela Intenso", "Dolor punzante, constante o sensibilidad que no lo deja dormir."),
        ("tooth", "Diente Roto o Astillado", "Un diente fracturado o astillado — lo reparamos y lo protegemos."),
        ("warning", "Diente Caído por Golpe", "El tiempo importa. Mantenga el diente húmedo y llámenos de inmediato."),
        ("shield", "Corona o Empaste Perdido", "Un diente expuesto es vulnerable — lo sellamos antes de que empeore."),
        ("hospital", "Absceso o Hinchazón", "Una infección dental necesita tratamiento rápido. No espere con esta."),
        ("tooth", "Dolor de Muela del Juicio", "Muelas retenidas o infectadas extraídas aquí mismo, sin referencias."),
        ("drop", "Encías Sangrantes", "Sangrado persistente o dolor de encías evaluado y tratado en la misma visita."),
        ("kit", "Dentadura Rota", "Dentaduras rotas, flojas o partidas reparadas para que vuelva a comer y hablar."),
    ],

    "fa_kicker": "Mientras Viene en Camino",
    "fa_title": "Qué Hacer Ahora Mismo",
    "fa_sub": "Unos pasos sencillos pueden proteger el diente y aliviar el dolor antes de que llegue a la clínica.",
    "firstaid": [
        ("Llámenos Primero", "Llame al (305) 404-6659 y cuéntenos qué pasó. Así preparamos la sala antes de que llegue."),
        ("Calme el Dolor", "Enjuáguese suavemente con agua tibia con sal y aplique una compresa fría por fuera de la mejilla — 15 minutos sí, 15 minutos no."),
        ("Proteja el Diente", "Si se le cayó un diente, tómelo por la corona, nunca por la raíz, y consérvelo en leche o saliva hasta llegar."),
        ("Venga Directo", "Diríjase al 12819 SW 42nd St, Miami. Reservamos tiempo para emergencias y nosotros nos encargamos del resto."),
    ],
    "fa_warning": ("<strong>Cuándo ir a la sala de emergencias:</strong> si tiene hinchazón que le dificulta respirar o "
                   "tragar, sangrado incontrolable, una posible fractura de mandíbula o una lesión por un accidente "
                   "grave, acuda al hospital más cercano o llame al 911 primero — luego llámenos para el seguimiento dental."),

    "why_kicker": "Por Qué Miami Confía en Nosotros",
    "why_title": "Primero el Alivio. Después las Respuestas. Nunca Juicios.",
    "why_sub": "Sabemos que una emergencia dental es estresante. Así se la hacemos más llevadera.",
    "why": [
        ("Lo Atendemos, No lo Pasamos", "Reservamos espacio en la agenda para pacientes urgentes — llame temprano para tener la mejor oportunidad de ser visto el mismo día."),
        ("Todo Aquí Mismo", "Extracciones, endodoncias, coronas e implantes se hacen en nuestra oficina — sin esperar la referencia a un especialista externo."),
        ("Sedación para la Ansiedad", "Opciones de sedación seguras diseñadas para reducir la ansiedad y mejorar su comodidad durante el tratamiento urgente."),
        ("El Precio Antes de Empezar", "Planes de tratamiento transparentes — le explicamos el costo y lo que implica antes de comenzar."),
        ("Formas de Pago Que Sirven", "Seguros PPO, financiamiento CareCredit® y opciones internas para que el costo nunca retrase su atención."),
        ("Equipo Bilingüe", "Todo nuestro equipo habla inglés y español — explique su dolor en el idioma en que piensa."),
    ],

    "reviews": REVIEWS_ES,
    "reviews_title": "Pacientes Que Llegaron con Dolor — y Salieron Sonriendo",

    "pay_title": "Atención de Emergencia a Su Alcance",
    "pay_sub": "El dolor no debería esperar al día de pago. Estas son todas las formas en que hacemos accesible el tratamiento urgente.",
    "offers": [
        {"title": "Examen Limitado de Emergencia", "amount": "75", "featured": True, "tag": "Empiece Aquí", "call": True,
         "copy": "Examen y diagnóstico enfocados en el diente que le está doliendo.",
         "cta": "Llamar para Reservar", "fine": "Visita enfocada al problema."},
        {"title": "Visita de Paciente Nuevo", "amount": "159",
         "copy": "Examen completo y radiografías — más limpieza gratis para quienes califiquen.",
         "cta": "Aprovechar Oferta", "fine": "Solo pacientes nuevos."},
        {"title": "Implantes Dentales", "amount": "199", "per": "/mes",
         "copy": "¿Perdió un diente definitivamente? Reemplácelo — consulta gratuita.",
         "cta": "Consulta Gratis", "fine": "Sujeto a aprobación de crédito."},
        {"title": "Invisalign®", "amount": "199", "per": "/mes",
         "copy": "Cuando ya no tenga dolor, enderece su sonrisa con discreción.",
         "cta": "Consulta Gratis", "fine": "Sujeto a aprobación de crédito."},
    ],

    "loc_cta": "Llame al (305) 404-6659",

    "final_title": "No Aguante el Dolor.",
    "final_copy": ("Los problemas dentales casi nunca se resuelven solos — y se vuelven más costosos mientras más "
                   "espera. Una llamada le da una respuesta, un plan y alivio."),
    "final_points": [
        "Citas de emergencia siempre bienvenidas",
        "Examen limitado por $75 sobre el área afectada",
        "Sedación disponible para pacientes con ansiedad",
        "Se habla español — equipo bilingüe",
    ],
    "final_secondary": "Solicitar Llamada",
}


CONTENT = {
    "general-dentist": {"en": GENERAL_EN, "es": GENERAL_ES},
    "emergency-dentist": {"en": EMERGENCY_EN, "es": EMERGENCY_ES},
}
