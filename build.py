#!/usr/bin/env python3
"""Builds the static SDA AI Services website into ./site.

Edit content in this file (SERVICES, USE_CASES, page functions), then run:
    python3 build.py
Change SITE_URL and EMAIL before going live.
"""
import json, shutil, html, re, posixpath, datetime
from pathlib import Path

SITE_URL = "https://sda-services.ai"      # Live domain (Cloudflare Pages custom domain).
EMAIL = "yigit@sda-services.ai"
BRAND = "SDA AI Services"
# Fill these in when ready. Empty values are simply left out of the pages and the structured data.
PHONE = ""        # e.g. "+971 50 123 4567" (shown as click-to-call and in the schema)
WHATSAPP = "971542377342"            # digits only incl. country code (adds WhatsApp buttons)
WHATSAPP_DISPLAY = "+971 54 237 7342" # how the number is shown on the pages
WHATSAPP_TEXT = "Hello SDA AI Services, I would like to talk about a project."  # pre-filled first message
# Google Calendar booking page (yigit@sda-services.ai, "Free 30-minute discovery call", Mon–Fri 9–17 Dubai time)
BOOKING_URL = "https://calendar.google.com/calendar/appointments/schedules/AcZssZ0NwR_cV6fana6F9QDSuWfoKAGoRw3_kfl0jSYuho7E-LeVSI1pGvLhfV6qC5lEAHz7iyCo_OBK"
SOCIAL = []       # profile URLs, e.g. ["https://www.linkedin.com/company/sda-ai-services"] (schema sameAs + footer)
LICENSE_NO = "2204440.01"  # trade licence number (legal notice, footer, structured data)
FORMATION_NO = "2204440"   # company formation number (legal notice, structured data)
ANALYTICS = True  # Cloudflare Web Analytics is on (automatic setup, visitors outside the EU); adds the note to the privacy policy
HOURS = "Monday to Friday, 9:00 to 17:00 (Dubai time, GST)"
# Search engine ownership tags (meta tag method; the page must stay online for verification to remain valid)
GOOGLE_VERIFY = "W83usJuTZkKzF4BUP-gteEH0HNXG2-AM-9VH7z4Hkew"
BING_VERIFY = "A49E1DBA8571BB0CC90A93CFF3947ACC"
ROOT = Path(__file__).parent
OG_IMAGE = "https://sda-services.ai/assets/brand/og-image.jpg"
# Cache-busting: a short hash of the CSS and JS goes into every asset URL,
# so browsers fetch new files right after each deploy.
import hashlib as _hl
ASSET_V = _hl.sha1(b"".join(p.read_bytes() for p in sorted([*(ROOT / "src" / "assets").glob("*.css"), *(ROOT / "src" / "assets").glob("*.js"), *(ROOT / "src" / "demos").rglob("*.*")]) if p.suffix in (".css", ".js", ".py"))).hexdigest()[:8]
OUT = ROOT / "site"

from urllib.parse import quote as _quote
WA_URL = f"https://wa.me/{WHATSAPP}?text={_quote(WHATSAPP_TEXT)}" if WHATSAPP else ""
WA_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.6c-4.85 0-8.7 3.45-8.7 7.8 0 2.3 1.05 4.35 2.75 5.8l-.75 3.2 3.5-1.75c1 .35 2.05.55 3.2.55 4.85 0 8.7-3.45 8.7-7.8S16.85 3.6 12 3.6Z" '
           'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="8.4" cy="11.4" r="1.1" fill="currentColor"/>'
           '<circle cx="12" cy="11.4" r="1.1" fill="currentColor"/><circle cx="15.6" cy="11.4" r="1.1" fill="currentColor"/></svg>')
LIC_NOTE = f" · Trade licence no. {LICENSE_NO}" if LICENSE_NO else ""
CHECK_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="m4.5 10.5 3.5 3.5 7.5-8" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

e = html.escape

def book_btn(r, cls="btn btn-primary", label="Book a discovery call"):
    """Primary call-to-action: opens the booking page, falls back to the contact page."""
    if BOOKING_URL:
        return f'<a class="{cls}" href="{BOOKING_URL}" target="_blank" rel="noopener">{label} <span class="arr">→</span></a>'
    return f'<a class="{cls}" href="{r}contact.html">{label} <span class="arr">→</span></a>'

def lc(t):
    """Lower-case the first letter for use mid-sentence, but keep acronyms such as AI, HR or SAP."""
    return t if len(t) > 1 and t[1].isupper() else t[:1].lower() + t[1:]

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------
ICONS = {
  "agents": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="4" y="7" width="16" height="12" rx="3"/><path d="M12 3v4M9 12h.01M15 12h.01M9 16h6"/></svg>',
  "flow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 7h10M4 12h16M4 17h7"/><circle cx="18" cy="7" r="2"/><circle cx="15" cy="17" r="2"/></svg>',
  "web": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M3 9h18M8 21h8"/></svg>',
  "mobile": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/></svg>',
  "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
  "data": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><ellipse cx="12" cy="5.5" rx="7.5" ry="3"/><path d="M4.5 5.5v6.5c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V5.5M4.5 12v6.5c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V12"/></svg>',
  "plug": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 7 3 12l5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>',
}

SERVICES = [
  dict(slug="ai-agents", icon="agents", name="AI agents & assistants",
    title="AI Agent Development & Custom AI Assistants",
    meta="We build custom AI agents and chat assistants that answer from your documents and act in your tools. RAG, tool calling, guardrails and secure hosting.",
    h1="AI agents that answer, decide and act.",
    lede="We build assistants that answer from your own knowledge and agents that complete tasks in your systems, with guardrails and human approval where it matters.",
    short="Assistants that answer from your documents and agents that take actions in your tools, with guardrails and human approval.",
    chips=["RAG", "Tool calling", "Chat & voice"],
    facts=[("Typical first release", "4–8 weeks"), ("Hosting", "Your cloud or ours"), ("Models", "Claude, GPT, Gemini, open source"), ("Channels", "Web, Teams, Slack, phone")],
    intro=["An AI agent is software that understands a request in plain language, looks up the right information and carries out the next step. A support agent can read a ticket, check the order in your ERP and draft the reply. An internal assistant can answer policy questions with a link to the source.",
           "We design the agent around one measurable job, connect it to your data with retrieval-augmented generation (RAG), and add the controls an enterprise needs: permissions, logging, evaluation and a clear hand-off to people."],
    deliver=[("Knowledge assistants", "Chat over manuals, policies, contracts and wikis, with citations so users can check every answer."),
             ("Customer support agents", "Agents that resolve common tickets, update CRM records and escalate the rest with a summary."),
             ("Task agents", "Agents that call your APIs to create orders, book appointments or update records, with approval steps."),
             ("Voice & chat channels", "Deploy on your website, Microsoft Teams, Slack, WhatsApp or the phone."),
             ("Evaluation & guardrails", "Test sets, accuracy tracking, PII redaction and topic limits before and after launch."),
             ("Agent operations", "Monitoring, cost tracking and continuous improvement once the agent is live.")],
    examples=[("Customer service", "Resolve order-status and returns questions automatically, 24/7."),
              ("Internal helpdesk", "Answer IT and HR questions from your handbook with source links."),
              ("Sales", "Qualify inbound leads and prepare meeting briefs from CRM data."),
              ("Procurement", "Compare supplier offers and flag contract risks.")],
    faq=[("What is the difference between a chatbot and an AI agent?", "A chatbot answers questions. An AI agent can also take actions, such as looking up an order, updating a record or sending an email, using tools you give it access to."),
         ("Can the AI use our internal documents securely?", "Yes. We use retrieval-augmented generation, so documents stay in your storage and the agent only sees what the user is allowed to see. Your data is not used to train public models."),
         ("Which AI model do you use?", "We choose per project based on accuracy, cost and data-protection needs. We work with Claude, GPT, Gemini and open-source models that can run in your own cloud."),
         ("How do you prevent wrong answers?", "We build a test set from real questions, measure accuracy before launch, require citations, and route uncertain cases to a person.")],
    usecase="hr-tool"),
  dict(slug="workflow-automation", icon="flow", name="Workflow automation",
    title="AI Workflow Automation & Business Process Automation",
    meta="Automate approvals, document processing, complaints and reporting with AI. We map your processes and automate them end to end with clear human hand-offs.",
    h1="Automate the work nobody should do by hand.",
    lede="We find the repetitive steps in approvals, documents, complaints and reporting, and automate them end to end with clear hand-offs to your team.",
    short="Approvals, complaints, reporting and data entry, automated end to end with clear hand-offs to people.",
    chips=["Process mining", "Document AI", "Approvals"],
    facts=[("Typical first release", "3–6 weeks"), ("Works with", "ERP, CRM, email, SharePoint"), ("Approach", "Measure, automate, report"), ("Support", "Ongoing optimisation")],
    intro=["Most companies run on processes that move data between emails, PDFs, spreadsheets and business systems. Each step is small, but together they cost hours every day and cause delays and errors.",
           "We map the process with the people who run it, decide which steps AI can handle reliably, and build the automation with exception queues, audit trails and dashboards so you can see the time saved."],
    deliver=[("Process discovery", "Workshops and data analysis to find the steps with the highest automation value."),
             ("Document processing", "Read invoices, delivery notes, forms and contracts and extract the data into your systems."),
             ("Smart routing", "Classify emails, tickets and complaints and send them to the right team with a priority."),
             ("Approval workflows", "Digital approvals with rules, reminders, escalation and full history."),
             ("Report automation", "Recurring reports generated and sent automatically, with AI-written summaries."),
             ("Monitoring", "Dashboards for volumes, processing times and exceptions.")],
    examples=[("Accounts payable", "Capture invoices, match them to orders and route exceptions."),
              ("Complaints", "Classify incoming complaints and draft responses for review."),
              ("Order entry", "Turn customer emails and PDFs into ERP sales orders."),
              ("Facility requests", "Triage maintenance tickets and dispatch the right team.")],
    faq=[("Which processes are best to automate first?", "High-volume, rule-based processes with digital inputs, such as invoice capture, ticket routing or order entry. We usually start with one process and measure the result."),
         ("Do we need to replace our existing systems?", "No. We connect to the systems you already use through APIs, email, file shares or, where needed, robotic process automation."),
         ("What happens when the AI is unsure?", "Uncertain cases go to an exception queue where a person decides. Their decisions can be used to improve the automation over time."),
         ("How do we measure success?", "We agree on a baseline before we start, such as hours per week or processing time, and report against it after launch.")],
    usecase="facility-management"),
  dict(slug="web-applications", icon="web", name="Custom web applications",
    title="Custom Web Application Development with AI",
    meta="Custom web apps, portals and SaaS products with AI built in. React, Next.js and Python, delivered fast, accessible and maintainable.",
    h1="Web applications with AI built in.",
    lede="Portals, internal tools and SaaS products, designed around your users and delivered as fast, accessible web apps your team can maintain.",
    short="Portals, internal tools and SaaS products with AI built in, delivered as fast, maintainable web apps.",
    chips=["React / Next.js", "APIs", "Cloud native"],
    facts=[("Typical MVP", "6–12 weeks"), ("Frontend", "React, Next.js, TypeScript"), ("Backend", "Node.js, Python, PostgreSQL"), ("Hosting", "AWS, Azure, GCP")],
    intro=["Off-the-shelf software rarely fits how your business actually works. A custom web application can match your process exactly, connect to your existing systems and include AI features where they add real value.",
           "We take a product from first concept through design, development and launch, with automated tests, CI/CD and documentation so your team or ours can keep improving it."],
    deliver=[("Product discovery", "User interviews, scope and a clickable prototype before development starts."),
             ("UX/UI design", "Clean, accessible interfaces that follow WCAG and your brand."),
             ("Full-stack development", "TypeScript frontends, robust APIs and well-modelled databases."),
             ("AI features", "Search, summaries, document upload, recommendations and assistants inside your app."),
             ("Customer & partner portals", "Secure self-service portals with single sign-on and role-based access."),
             ("DevOps & hosting", "CI/CD pipelines, monitoring, backups and cloud infrastructure as code.")],
    examples=[("Supplier portal", "Suppliers upload documents, confirm orders and see their scorecard."),
              ("Internal tools", "Replace spreadsheets with a proper app for planning or approvals."),
              ("SaaS MVP", "Launch a new AI product to your first customers."),
              ("Customer portal", "Let customers track orders, tickets and invoices online.")],
    faq=[("How long does it take to build a web application?", "A focused MVP usually takes 6 to 12 weeks. We deliver in two-week sprints so you see working software early and can adjust priorities."),
         ("Who owns the code?", "You do. All source code, designs and documentation are transferred to you."),
         ("Can you take over an existing application?", "Yes. We start with a code and architecture review, then stabilise and extend the application."),
         ("Do you provide support after launch?", "Yes. We offer maintenance and further development packages with agreed response times.")],
    usecase="vendor-management"),
  dict(slug="mobile-apps", icon="mobile", name="Mobile & field apps",
    title="Mobile App & Field Service App Development",
    meta="iOS, Android and progressive web apps for field teams: job reports, photos, GPS, signatures and offline capture that syncs back to your systems.",
    h1="Apps for teams that work on the move.",
    lede="Mobile apps for technicians, inspectors and sales teams: capture photos, GPS and signatures on site, work offline, and sync to the office in real time.",
    short="Apps for teams on the move: job reports, photos, GPS and offline capture with instant sync to the office.",
    chips=["iOS & Android", "Offline-first", "PWA"],
    facts=[("Typical first release", "8–12 weeks"), ("Platforms", "iOS, Android, web"), ("Tech", "Flutter, React Native, PWA"), ("Works offline", "Yes")],
    intro=["Field teams still lose time with paper forms, phone calls and re-typing data back at the office. A well-designed mobile app removes that work and gives managers a live view of what is happening.",
           "We build cross-platform apps that are simple enough to use with gloves on, work without a signal and connect to your ERP, CRM or maintenance system. AI features such as photo recognition and voice notes speed up reporting further."],
    deliver=[("Field service apps", "Job lists, checklists, time tracking, photos and customer signatures."),
             ("Inspection & audit apps", "Digital checklists with photo evidence and automatic PDF reports."),
             ("Offline sync", "Reliable offline mode that syncs as soon as a connection is available."),
             ("AI on the device", "Voice-to-text reports, photo classification and damage detection."),
             ("Back-office web app", "Planning, dispatch and reporting for the office team."),
             ("App store release", "Publishing, updates and device management for your company.")],
    examples=[("Maintenance", "Technicians close jobs on site with photos and signatures."),
              ("Facility rounds", "Guided inspection rounds with automatic defect tickets."),
              ("Construction", "Daily site reports with GPS-tagged photos."),
              ("Sales visits", "Visit reports and orders captured in the field.")],
    faq=[("Native app or progressive web app?", "A progressive web app is faster and cheaper to roll out. Native or cross-platform apps make sense when you need offline mode, camera features or app store distribution. We advise per project."),
         ("Does the app work without internet?", "Yes. We design offline-first, so data is stored on the device and synced when a connection returns."),
         ("Can the app connect to our ERP?", "Yes, we connect it to your ERP and other business systems."),
         ("How do you handle data protection?", "Data is encrypted on the device and in transit, and we follow GDPR requirements for location and photo data.")],
    usecase="field-service"),
  dict(slug="data-management", icon="data", name="Data management",
    title="Data Management Services for AI: Integration, Quality & Governance",
    meta="Get your data ready for AI. We connect, clean and govern data from ERP, CRM and files, and build the pipelines, master data and knowledge bases your AI can trust.",
    h1="Clean, connected data your AI can trust.",
    lede="AI is only as good as the data behind it. We connect your sources, fix quality issues and set up the pipelines, master data and governance that keep your data reliable.",
    short="Connect, clean and govern data from all your systems so AI and reporting can rely on it.",
    chips=["Data pipelines", "Data quality", "Governance"],
    facts=[("Typical first release", "3–6 weeks"), ("Sources", "ERP, CRM, files, APIs"), ("Storage", "Warehouse, lakehouse, vector DB"), ("Focus", "Quality & governance")],
    intro=["Most AI projects that stall do so because of data, not models. Customer records exist three times, supplier names are spelled five ways, and the documents an assistant needs are scattered across drives and inboxes.",
           "We bring your data into shape: we connect the sources, clean and deduplicate records, define who owns what, and build pipelines that keep everything current. The result is a reliable foundation for AI agents, automation and reporting."],
    deliver=[("Data integration", "Reliable pipelines from ERP, CRM, databases, files and APIs into one governed platform."),
             ("Data quality & cleansing", "Find and fix duplicates, gaps and inconsistencies, with AI-assisted matching."),
             ("Master data management", "One trusted record for customers, suppliers, materials and products."),
             ("Knowledge bases for AI", "Prepare documents and records for retrieval, with vector search and access rules."),
             ("Governance & access", "Ownership, data catalog, lineage and role-based access, documented and auditable."),
             ("Reporting foundation", "Clean, modelled data that feeds your BI tools and management reports.")],
    examples=[("Supplier master data", "Merge duplicate suppliers and keep certifications and contracts current."),
              ("Customer 360", "Combine CRM, orders and support history into one customer view."),
              ("Document knowledge base", "Turn manuals, policies and contracts into a searchable source for AI assistants."),
              ("System migration", "Cleanse and validate data before moving to a new ERP or CRM.")],
    faq=[("Why does data quality matter for AI?", "AI agents and forecasts repeat whatever is in your data. Duplicates, gaps and outdated records lead directly to wrong answers and bad decisions."),
         ("Do we need a data warehouse first?", "Not necessarily. We start with the data the first use case needs and grow the platform when volume or complexity requires it."),
         ("How do you handle sensitive data?", "We apply role-based access, encryption and masking, and keep data in the environment you choose."),
         ("Can you work with our existing tools?", "Yes. We build on the databases, cloud platforms and BI tools you already use wherever that makes sense.")],
    usecase="vendor-management"),
  dict(slug="sap-integration", icon="plug", name="Enterprise & SAP integration",
    title="SAP AI Integration, SAP BTP Extensions & ERP Integration",
    meta="Connect AI to SAP S/4HANA, SAP BTP, CRMs and legacy systems. Side-by-side extensions, APIs and middleware without disrupting operations.",
    h1="Bring AI to the systems you already run.",
    lede="We connect AI agents, apps and dashboards to SAP S/4HANA, SAP BTP, CRMs and legacy databases, safely and without disrupting daily operations.",
    short="Connect AI to SAP S/4HANA, SAP BTP extensions, CRMs and legacy databases without disrupting operations.",
    chips=["SAP BTP", "S/4HANA", "Middleware"],
    facts=[("Systems", "SAP ECC, S/4HANA, BTP"), ("Also", "Dynamics, Salesforce, custom DBs"), ("Approach", "Clean core, side-by-side"), ("Integration", "APIs, events, middleware")],
    intro=["Your ERP holds the data that makes AI useful: orders, materials, suppliers, quality records and customers. The challenge is connecting to it securely without modifying the core system.",
           "We build side-by-side extensions on SAP BTP and integration layers that expose the right data to AI applications through governed APIs. That keeps your SAP core clean and upgrade-safe."],
    deliver=[("Integration architecture", "Target architecture, API strategy and security concept."),
             ("SAP BTP extensions", "Side-by-side apps with SAP Build, CAP and Fiori."),
             ("AI on ERP data", "Agents and assistants that read and write SAP data through approved APIs."),
             ("API & middleware", "SAP Integration Suite, REST and OData services, event-driven integration."),
             ("Legacy integration", "Connect older databases and file-based interfaces safely."),
             ("Data migration support", "Data cleansing and validation with AI for S/4HANA projects.")],
    examples=[("Quality management", "Summarise inspection results and suggest usage decisions."),
              ("Purchasing", "Draft purchase orders and flag supplier risks from SAP data."),
              ("Sales", "Turn customer emails into sales orders in S/4HANA."),
              ("Maintenance", "Create maintenance notifications from mobile reports.")],
    faq=[("Can you connect AI to SAP?", "Yes, we connect AI to SAP and other ERP systems through secure, approved APIs."),
         ("Will the integration disrupt daily operations?", "No. We build alongside your existing systems and roll out in steps, with testing before anything goes live."),
         ("Can AI write data back into our systems?", "Yes, with permission checks, and with a human approval step for critical transactions."),
         ("Which other systems can you integrate?", "CRMs, document management, databases and most systems with an API, including older file-based interfaces.")],
    usecase="vendor-management"),
]

# Demos live in src/demos/<slug>/ (meta.py: page content, markup.py: HTML, demo.js, demo.css).
# The order here is the order on the site.
import importlib.util as _ilu
DEMO_DIR = ROOT / "src" / "demos"
DEMO_ORDER = ["workflow-management", "field-service", "hr-tool", "real-estate", "freight-forwarding", "construction", "dashboard", "vendor-management", "facility-management"]
DEMO_ORDER = [s for s in DEMO_ORDER if (ROOT / "src" / "demos" / s / "demo.js").exists()]  # skip demos still in progress
def _load(slug, name):
    spec = _ilu.spec_from_file_location(f"demo_{slug.replace('-', '_')}_{name}", DEMO_DIR / slug / f"{name}.py")
    mod = _ilu.module_from_spec(spec); spec.loader.exec_module(mod); return mod
USE_CASES, UC_ICONS, DEMOS = [], {}, {}
for _slug in DEMO_ORDER:
    _meta = _load(_slug, "meta")
    USE_CASES.append(_meta.USE_CASE); UC_ICONS[_slug] = _meta.ICON; DEMOS[_slug] = _load(_slug, "markup").markup
_lp_spec = _ilu.spec_from_file_location("landing", ROOT / "src" / "landing.py")
_LP = _ilu.module_from_spec(_lp_spec); _lp_spec.loader.exec_module(_LP)
LANDING, HUBS = _LP.PAGES, _LP.HUBS
_in_spec = _ilu.spec_from_file_location("insights", ROOT / "src" / "insights.py")
_IN = _ilu.module_from_spec(_in_spec); _in_spec.loader.exec_module(_IN)
POSTS = sorted(_IN.POSTS, key=lambda x: x["date"], reverse=True)
LP_BY_KIND = {k: [x for x in LANDING if x["kind"] == k] for k in HUBS}
IND_ICON = lambda d: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
INDUSTRIES = [
  dict(slug="manufacturing", name="Manufacturing",
    icon=IND_ICON('<path d="M3 21V10l6 4V10l6 4V6l6-3v18H3z"/><path d="M7 17h2M12 17h2M17 17h1"/>'),
    line="Supplier quality, complaints and production data in one connected flow.",
    links=[("Vendor management demo", "use-cases/vendor-management.html"), ("SAP integration", "services/sap-integration.html")]),
  dict(slug="logistics", name="Logistics & wholesale",
    icon=IND_ICON('<path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17.5" cy="18" r="2"/>'),
    line="Order intake, proof of delivery and customer updates without manual steps.",
    links=[("Field service demo", "use-cases/field-service.html"), ("Workflow automation", "services/workflow-automation.html")]),
  dict(slug="construction", name="Construction & field service",
    icon=IND_ICON('<path d="M4 18h16M6 18v-3a6 6 0 0 1 12 0v3M12 9V5M9 6l3-1 3 1"/>'),
    line="Jobs, photos, timesheets and signatures from the site straight to the invoice.",
    links=[("Field service demo", "use-cases/field-service.html"), ("Mobile & field apps", "services/mobile-apps.html")]),
  dict(slug="real-estate", name="Real estate & facilities",
    icon=IND_ICON('<path d="M4 21V5l8-3v19M12 9h8v12M7.5 8h1M7.5 12h1M7.5 16h1M15.5 13h1M15.5 17h1M2 21h20"/>'),
    line="Tickets, assets, inspections and service partners under one roof.",
    links=[("Facility management demo", "use-cases/facility-management.html"), ("Custom web apps", "services/web-applications.html")]),
  dict(slug="professional-services", name="Professional services",
    icon=IND_ICON('<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>'),
    line="Documents, knowledge and client requests answered in minutes, not days.",
    links=[("AI agents & assistants", "services/ai-agents.html"), ("Data management", "services/data-management.html")]),
  dict(slug="energy", name="Energy & utilities",
    icon=IND_ICON('<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>'),
    line="Field crews, asset data and maintenance plans connected to your core systems.",
    links=[("Mobile & field apps", "services/mobile-apps.html"), ("SAP integration", "services/sap-integration.html")]),
]

def industries_block(r):
    cards = "".join(f"""<article class="ind glass" id="ind-{i['slug']}"><span class="ind-ic" aria-hidden="true">{i['icon']}</span><h3>{e(i['name'])}</h3><p>{e(i['line'])}</p><div class="ind-links">{"".join(f'<a href="{r}{h}">{e(t)} <span class="arr">→</span></a>' for t, h in [(f"AI for {i['name'].lower()}", f"industries/{i['slug']}.html")] + i['links'])}</div></article>""" for i in INDUSTRIES)
    return f"""<div class="sec-head"><h2>Built for your industry</h2><p>The same building blocks, shaped around the processes, data and rules of your sector. <a class="link" href="{r}industries/index.html">All industries <span class="arr">→</span></a></p></div><div class="inds">{cards}</div>"""

SVC = {s["slug"]: s for s in SERVICES}
UC = {u["slug"]: u for u in USE_CASES}

# --------------------------------------------------------------------------
# SEO: search titles (max ~60 chars) and descriptions (max ~160 chars)
# --------------------------------------------------------------------------
GCC = ["United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "Bahrain", "Oman"]
SEO = {
  "home": ("SDA AI Services | AI Automation & Software in Dubai, UAE",
           "Dubai-based AI agency building AI agents, workflow automation and custom web and mobile apps for companies in the UAE and GCC. Free pilot project."),
  "services": ("AI Development Services in Dubai, UAE | SDA AI Services",
               "AI agents, workflow automation, web and mobile apps, data management and SAP integration for UAE and GCC companies. From prototype to production."),
  "use-cases": ("AI Software Demos: Try {n} Live Use Cases | SDA AI Services",
                "Try {n} interactive demos of AI business software: workflows, field service, HR, real estate, freight forwarding, construction, dashboards and more."),
  "pricing": ("AI Development Pricing in the UAE (AED) | SDA AI Services",
              "Free pilot project and unlimited revisions. Typical UAE prices in AED for AI agents, workflow automation, dashboards, web and mobile apps."),
  "contact": ("Contact SDA AI Services | AI Agency in Dubai",
              "Talk to our Dubai team about your AI, automation, web or app project. We reply within one business day with first ideas and a free pilot proposal."),
  "ai-agents": ("AI Agent Development in Dubai | SDA AI Services",
                "Custom AI agents and chatbots for UAE businesses: answers from your documents, actions in your systems, on WhatsApp, web and voice. Free pilot."),
  "workflow-automation": ("AI Workflow Automation in Dubai, UAE | SDA AI Services",
                          "Automate approvals, invoices, documents and reporting with AI. End-to-end process automation for UAE and GCC companies, with a free pilot."),
  "web-applications": ("Custom Web App Development Dubai | SDA AI Services",
                       "Custom web applications, portals and SaaS products with AI built in, for companies in Dubai, the UAE and GCC. Fixed prices and a free pilot."),
  "mobile-apps": ("Mobile App Development in Dubai | SDA AI Services",
                  "iOS, Android and offline field service apps for UAE teams: photos, GPS, signatures and checklists synced to your back office. Free pilot."),
  "data-management": ("Data Management & AI Dashboards Dubai | SDA AI Services",
                      "Clean, connected data and live KPI dashboards for UAE companies: data integration, master data and governance that your AI can rely on."),
  "sap-integration": ("SAP AI Integration & SAP BTP in Dubai | SDA AI Services",
                      "Connect AI to SAP S/4HANA, SAP BTP, CRMs and legacy systems in the UAE. Clean-core extensions, secure APIs and middleware without downtime."),
  "construction": ("Construction Site Report & Snag App Demo | SDA AI Services",
                   "Interactive construction and fit-out demo: daily site reports, snag lists, permits and claims in one app for contractors in the UAE."),
  "dashboard": ("AI Management Dashboard Demo | SDA AI Services",
                "Interactive KPI dashboard demo with drilldowns, AI-written summaries and report export. See what a custom management dashboard can do."),
  "facility-management": ("AI Facility Management Software Demo | SDA AI Services",
                          "Try a facility management demo: maintenance tickets, technician app, sensor alerts and documents in one system for property teams."),
  "field-service": ("Field Service App Demo | SDA AI Services",
                    "Interactive field service app demo: GPS check-in, photos, customer signatures and proof of delivery, synced to the office in real time."),
  "freight-forwarding": ("Freight Forwarding Software Demo UAE | SDA AI Services",
                         "Freight forwarding and customs clearance software demo for UAE forwarders: shipments, documents, customs status and customer updates."),
  "hr-tool": ("AI HR Software Demo: Recruiting & Leave | SDA AI Services",
              "Try an AI HR tool: emails become candidates, CVs are matched to jobs, leave is approved with a coverage check and HR questions get answered."),
  "real-estate": ("Real Estate CRM Demo: Leads & Viewings | SDA AI Services",
                  "Interactive real estate CRM demo: listings, leads, viewings, sales pipeline and contracts in one system for brokers and developers."),
  "vendor-management": ("AI Vendor Management Software Demo | SDA AI Services",
                        "Try a vendor management demo: RFQs, AI quote comparison, 8D complaints, approvals and supplier documents in one place."),
  "workflow-management": ("Workflow Management Software Demo | SDA AI Services",
                          "Interactive workflow management demo: tasks, approvals, process templates and document management for teams that want less email."),
}

def clean_url(path):
    """Cloudflare Pages serves /x.html as /x and /dir/index.html as /dir/. Use those URLs everywhere."""
    if path.endswith("index.html"):
        return path[:-len("index.html")]
    if path.endswith(".html"):
        return path[:-len(".html")]
    return path

def abs_url(path):
    return SITE_URL + "/" + clean_url(path)

def clean_links(doc, page_path):
    """Rewrite internal .html links to the clean URLs Cloudflare serves, so no click hits a redirect."""
    base = posixpath.dirname(page_path)
    def rep(m):
        href = m.group(1)
        if re.match(r"^(https?:|mailto:|tel:|#|data:|/api/)", href):
            return m.group(0)
        p, _, frag = href.partition("#")
        if not p.endswith(".html"):
            return m.group(0)
        target = p.lstrip("/") if p.startswith("/") else posixpath.normpath(posixpath.join(base, p))
        return 'href="/' + clean_url(target) + ("#" + frag if frag else "") + '"'
    return re.sub(r'href="([^"]+)"', rep, doc)
# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
SPARK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0c.6 5.8 3.4 9.9 12 12-8.6 2.1-11.4 6.2-12 12-.6-5.8-3.4-9.9-12-12 8.6-2.1 11.4-6.2 12-12z" fill="currentColor"/></svg>'
# gradient sparkle for headings + logo (teal -> coral), ids made unique per use
_spark_n = [0]
def spark_g():
    _spark_n[0] += 1
    i = f"sg{_spark_n[0]}"
    return (f'<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="{i}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" style="stop-color:var(--teal-2)"/><stop offset="1" style="stop-color:var(--coral)"/></linearGradient></defs>'
            f'<path d="M12 0c.6 5.8 3.4 9.9 12 12-8.6 2.1-11.4 6.2-12 12-.6-5.8-3.4-9.9-12-12 8.6-2.1 11.4-6.2 12-12z" fill="url(#{i})"/></svg>')
def SPG():
    return f'<span class="sp">{spark_g()}</span>'
SP = '<span class="sp" style="color:var(--teal-2)">' + SPARK + '</span>'
CHECK = '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7.2" fill="currentColor" opacity=".16"/><path d="M4.8 8.3 7 10.4l4.2-4.6" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def logo_svg(cls="logo-svg"):
    """Brand logo (prompt mark + SDA / AI SERVICES), inlined from src/assets/brand/logo.svg."""
    s = (ROOT / "src" / "assets" / "brand" / "logo.svg").read_text().strip()
    s = re.sub(r'<title>.*?</title>', '', s)
    s = re.sub(r'^<svg [^>]*?(viewBox="[^"]+")[^>]*>', lambda m: f'<svg class="{cls}" {m.group(1)} role="img" aria-label="{BRAND}">', s)
    return s

def logo(r):
    return f'<a class="logo" href="{r}index.html" aria-label="{BRAND} home">{logo_svg()}</a>'

def head(r, path, title, meta, schema=None, demo=False, noindex=False):
    url = abs_url(path)
    full_title = title if BRAND in title else f"{title} | {BRAND}"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1"
    ld = ""
    for s in (schema or []):
        ld += '<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + "</script>\n"
    og_type = "article" if path.startswith("insights/") and not path.endswith("index.html") else "website"
    return f"""<title>{e(full_title)}</title>
<meta name="description" content="{e(meta)}">
<meta name="robots" content="{robots}">
{f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">' + chr(10) if GOOGLE_VERIFY and path in ("", "index.html") else ""}{f'<meta name="msvalidate.01" content="{BING_VERIFY}">' + chr(10) if BING_VERIFY and path in ("", "index.html") else ""}<meta name="theme-color" content="#F7F9F9">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="en_AE">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(meta)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{BRAND}: AI agents, automation and custom software from Dubai">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(meta)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<link rel="icon" href="/assets/brand/logo-mark.svg" type="image/svg+xml">
<link rel="icon" href="/assets/brand/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/brand/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">{chr(10) + f'<link rel="stylesheet" href="/assets/demos.css?v={ASSET_V}">' if demo else ""}
{ld}"""

BURGER = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 6.5h14M3 13.5h14" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>'

def nav(r, active):
    drop = "".join(f'<li><a href="{r}services/{s["slug"]}.html"><span class="d-ic" aria-hidden="true">{ICONS[s["icon"]]}</span><span class="d-tx"><b>{e(s["name"])}</b><span>{e(", ".join(s["chips"]))}</span></span></a></li>' for s in SERVICES)
    drop += f'<li class="d-feature"><a href="{r}services/index.html"><span class="d-kick">All services</span><b>From first prototype to production</b><span>See how we design, build and run AI software for your team.</span><span class="d-go">Explore services <span class="arr">→</span></span></a></li>'
    cur = lambda k: ' aria-current="page"' if active == k else ""
    return f"""<div class="aurora" aria-hidden="true"><i class="a1"></i><i class="a2"></i><i class="a3"></i></div><div class="grain" aria-hidden="true"></div>
<a class="skip" href="#main">Skip to content</a>
<nav class="nav" aria-label="Main">
  <div class="nav-in glass-strong">
    {logo(r)}
    <ul class="menu">
      <li class="m-ind" aria-hidden="true"></li>
      <li><a href="{r}index.html"{cur("home")}>Home</a></li>
      <li class="has-drop"><a href="{r}services/index.html"{cur("services")}>Services <svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 4.5 6 7.5 9 4.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></a><ul class="drop mega glass-strong">{drop}</ul></li>
      <li><a href="{r}use-cases/index.html"{cur("use-cases")}><i class="pulse-dot" aria-hidden="true"></i>Live demos</a></li>
      <li><a href="{r}pricing.html"{cur("pricing")}>Pricing</a></li>
      <li><a href="{r}insights/index.html"{cur("insights")}>Insights</a></li>
      <li><a href="{r}contact.html"{cur("contact")}>Contact</a></li>
      <li class="m-cta"><a class="btn btn-primary" href="{r}contact.html">Start a project <span class="arr">→</span></a></li>
    </ul>
    <div class="nav-cta">
      <a class="btn btn-primary btn-sm btn-shine" href="{r}contact.html">Start a project <span class="arr">→</span></a>
      <button class="burger" type="button" aria-label="Open menu" aria-expanded="false">{BURGER}</button>
    </div>
  </div>
</nav>"""

def footer(r, demo=False):
    svc = "".join(f'<li><a href="{r}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in SERVICES)
    svc += "".join(f'<li><a href="{r}solutions/{x["slug"]}.html">{e(x["name"])}</a></li>' for x in LP_BY_KIND["solutions"])
    inds = "".join(f'<li><a href="{r}industries/{i["slug"]}.html">{e(i["name"])}</a></li>' for i in INDUSTRIES)
    regs = "".join(f'<li><a href="{r}locations/{x["slug"]}.html">{e(x["name"])}</a></li>' for x in LP_BY_KIND["locations"])
    demo_js = f'\n<script src="/assets/demos.js?v={ASSET_V}"></script>' if demo else ""
    contact_li = f'<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>'
    if PHONE: contact_li += f'<li><a href="tel:{PHONE.replace(" ", "")}">{e(PHONE)}</a></li>'
    if WHATSAPP: contact_li += f'<li><a href="{WA_URL}" target="_blank" rel="noopener">WhatsApp</a></li>'
    social = "".join(f'<li><a href="{u}" rel="noopener me">{e(_social_name(u))}</a></li>' for u in SOCIAL)
    wa_float = (f'\n<a class="wa-float" href="{WA_URL}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp ({WHATSAPP_DISPLAY})">'
                f'{WA_ICON}<span>WhatsApp</span></a>') if WHATSAPP else ""
    return f"""<footer>
  <div class="wrap">
    <div class="foot glass">
      <div>{logo(r)}<p>AI software, web and app development for companies that want working systems in production. Based in Dubai, serving clients across the UAE and GCC.</p><p class="note">SDA SERVICES L.L.C-FZ{LIC_NOTE} · Meydan Grandstand, 6th floor, Meydan Road, Nad Al Sheba, Dubai, UAE</p></div>
      <div><h4>Services</h4><ul>{svc}</ul></div>
      <div><h4>Industries</h4><ul>{inds}</ul></div>
      <div><h4>Regions</h4><ul>{regs}</ul></div>
      <div><h4>Company</h4><ul><li><a href="{r}about.html">About us</a></li><li><a href="{r}insights/index.html">Insights</a></li><li><a href="{r}pricing.html">Pricing</a></li><li><a href="{r}index.html#process">Process</a></li><li><a href="{r}contact.html">Contact</a></li>{contact_li}{social}</ul></div>
    </div>
    <div class="foot-base"><span>© <span id="yr">2026</span> {BRAND}</span><span><a href="{r}privacy.html">Privacy policy</a> · <a href="{r}legal-notice.html">Legal notice</a></span></div>
  </div>
</footer>{wa_float}
<script src="/assets/main.js?v={ASSET_V}"></script>{demo_js}"""

def cta_band(r, h="Ready to put AI to work?", p="Tell us about your process. We reply within one business day with first ideas and a proposed next step."):
    return f"""<section class="block" style="padding-top:0"><div class="wrap"><div class="cta-card glass-strong"><h2>{h}</h2><p>{p}</p>
<div class="cta-row">{book_btn(r)}<a class="btn btn-glass" href="{r}use-cases/index.html">Try the live demos</a></div></div></div></section>"""

def crumbs(r, items):
    home_ic = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 9 10 3.5 16.5 9v7.5h-4.5V12H8v4.5H3.5z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'
    li = "".join((f'<li><a href="{r}{href}">{home_ic if n == "Home" else ""}<span>{e(n)}</span></a></li>' if href else f'<li aria-current="page"><span>{e(n)}</span></li>') for n, href in items)
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{li}</ol></nav>'

def crumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p or "")} for i, (n, p) in enumerate(items)]}

def _social_name(u):
    for k, n in (("linkedin", "LinkedIn"), ("instagram", "Instagram"), ("x.com", "X"), ("twitter", "X"), ("facebook", "Facebook"), ("youtube", "YouTube"), ("tiktok", "TikTok")):
        if k in u: return n
    return u.split("//")[-1].split("/")[0]

ORG_ID = SITE_URL + "/#organization"
ORG_LD = {"@context": "https://schema.org", "@type": "ProfessionalService", "@id": ORG_ID, "name": BRAND,
          "alternateName": ["Software, Development, Applications & AI Services", "SDA SERVICES L.L.C-FZ"],
          "legalName": "SDA SERVICES L.L.C-FZ",
          "url": SITE_URL + "/", "email": EMAIL,
          "logo": {"@type": "ImageObject", "url": SITE_URL + "/assets/brand/logo.png"}, "image": OG_IMAGE,
          "description": "Dubai-based AI agency: AI agents, workflow automation, custom web and mobile apps, data management and SAP integration for companies in the UAE and GCC.",
          "address": {"@type": "PostalAddress", "streetAddress": "Meydan Grandstand, 6th floor, Meydan Road, Nad Al Sheba",
                      "addressLocality": "Dubai", "addressRegion": "Dubai", "addressCountry": "AE"},
          "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "17:00"}],
          "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "email": EMAIL, "areaServed": ["AE", "SA", "QA", "KW", "BH", "OM"], "availableLanguage": ["English", "Arabic"]}],
          "areaServed": [{"@type": "Country", "name": c} for c in GCC],
          "knowsLanguage": ["en", "ar"], "priceRange": "AED 10,900+",
          "knowsAbout": ["AI agents", "Workflow automation", "Custom web applications", "Mobile apps", "Data management", "SAP integration"]}
if PHONE:
    ORG_LD["telephone"] = PHONE; ORG_LD["contactPoint"][0]["telephone"] = PHONE
if LICENSE_NO or FORMATION_NO:
    ORG_LD["identifier"] = ([{"@type": "PropertyValue", "propertyID": "Trade licence number", "value": LICENSE_NO}] if LICENSE_NO else []) + \
                           ([{"@type": "PropertyValue", "propertyID": "Formation number", "value": FORMATION_NO}] if FORMATION_NO else [])
if SOCIAL:
    ORG_LD["sameAs"] = SOCIAL
WEBSITE_LD = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE_URL + "/#website", "name": BRAND, "url": SITE_URL + "/",
              "inLanguage": "en", "publisher": {"@id": ORG_ID}}

# ---- small visuals for the bento tiles ----
_I = lambda p: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'
VIS = {
  "ai-agents": '''<div class="chatv" aria-hidden="true">
    <div class="bub u">Where is order 4471, and can I change the delivery address?</div>
    <div class="bub a">It shipped this morning and arrives Thursday. I updated the address to Harbour Street 12 and sent you a new tracking link.<small>Checked: order system · carrier API</small></div>
    <div class="bub u">Great. Can you also send me the invoice?</div>
    <div class="typing-dots"><i></i><i></i><i></i></div></div>''',
  "workflow-automation": '<div aria-hidden="true"><div class="flowv"><span>' + _I('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>') + '</span><span>' + _I('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>') + '</span><span>' + _I('<path d="M20 6 9 17l-5-5"/>') + '</span><span>' + _I('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/>') + '</span><i class="pulse"></i></div><div class="flowv-l"><span>Email</span><span>Extract</span><span>Approve</span><span>ERP</span></div></div>',
  "data-management": '<div class="dedupe" aria-hidden="true"><span><s>NORDWERK METALS GMBH</s></span><span><s>Nordwerk Metal</s></span><span class="keep">Nordwerk Metals</span></div>',
  "web-applications": '<div class="appv" aria-hidden="true"><div class="appv-bar"><i></i><i></i><i></i><span>portal.yourcompany.com</span></div><div class="appv-bd"><div class="appv-nav"><b class="on">Orders</b><b>Invoices</b><b>Support</b></div><div class="appv-main"><div class="appv-h"><span>Your orders</span><em>+ New request</em></div><div class="appv-row"><span><b>#4471</b> 40 units</span><i class="st ok">Shipped</i></div><div class="appv-row"><span><b>#4468</b> 12 units</span><i class="st">Delivered</i></div><div class="appv-row"><span><b>#4502</b> Quote ready</span><i class="st act">Approve</i></div></div></div></div>',
  "mobile-apps": '<div class="phonev" aria-hidden="true"><span class="ok"><i></i>Photo added</span><span class="ok"><i></i>GPS confirmed</span><span class="ok"><i></i>Checklist done</span><span><i></i>Customer signature</span></div>',
  "sap-integration": '''<svg class="hubv" viewBox="0 0 300 110" aria-hidden="true">
    <defs><linearGradient id="hl" x1="0" x2="1"><stop offset="0" style="stop-color:var(--teal-glow)"/><stop offset="1" style="stop-color:var(--coral-glow)"/></linearGradient></defs>
    <path d="M150 55 L40 22 M150 55 L40 88 M150 55 L260 22 M150 55 L260 88" stroke="url(#hl)" stroke-width="2" fill="none" stroke-dasharray="4 5"/>
    <circle cx="150" cy="55" r="22" style="fill:var(--ink)"/><path d="M150 43c.3 3.1 1.8 5.3 6.5 7-4.7 1.7-6.2 3.9-6.5 7-.3-3.1-1.8-5.3-6.5-7 4.7-1.7 6.2-3.9 6.5-7z" style="fill:var(--coral-glow)" transform="translate(0 5)"/>
    <g font-family="Geist, system-ui" font-size="12" fill="#243640" text-anchor="middle">
      <rect x="10" y="10" width="60" height="24" rx="12" fill="#fff" stroke="rgba(14,27,34,.12)"/><text x="40" y="26">ERP</text>
      <rect x="10" y="76" width="60" height="24" rx="12" fill="#fff" stroke="rgba(14,27,34,.12)"/><text x="40" y="92">CRM</text>
      <rect x="230" y="10" width="60" height="24" rx="12" fill="#fff" stroke="rgba(14,27,34,.12)"/><text x="260" y="26">Docs</text>
      <rect x="230" y="76" width="60" height="24" rx="12" fill="#fff" stroke="rgba(14,27,34,.12)"/><text x="260" y="92">APIs</text></g></svg>''',
}
TILE_CLASS = {"ai-agents": "t-agents"}

def bento(r):
    out = []
    for s in SERVICES:
        cls = TILE_CLASS.get(s["slug"], "")
        out.append(f"""<a class="tile glass {cls}" href="{r}services/{s['slug']}.html">
  <div class="tile-vis">{VIS[s['slug']]}</div>
  <h3>{e(s['name'])}</h3><p>{e(s['short'])}</p>
  <span class="link">Explore {e(lc(s['name']))} <span class="arr">→</span></span></a>""")
    return '<div class="bento">' + "".join(out) + "</div>"

def svc_card(r, s, i):
    return f"""<a class="tile glass" href="{r}services/{s['slug']}.html">
  <div class="tile-vis">{VIS[s['slug']]}</div>
  <h3>{e(s['name'])}</h3><p>{e(s['short'])}</p>
  <span class="link">Explore {e(lc(s['name']))} <span class="arr">→</span></span></a>"""


def uc_switch(r):
    tabs = "".join(f'<button type="button" role="tab" id="uct-{u["slug"]}" aria-controls="ucp-{u["slug"]}" aria-selected="{"true" if i == 0 else "false"}"{"" if i == 0 else " tabindex=\"-1\""}><span class="uct-ic" aria-hidden="true">{UC_ICONS[u["slug"]]}</span><span class="uct-tx"><b>{e(u["name"])}</b><small>{e(u["label"])}</small></span></button>' for i, u in enumerate(USE_CASES))
    panels = ""
    for i, u in enumerate(USE_CASES):
        panels += f"""<div class="uc-panel" role="tabpanel" id="ucp-{u['slug']}" aria-labelledby="uct-{u['slug']}"{"" if i == 0 else " hidden"}>
  <div class="uc-copy"><div><h3>{e(u['name'])}</h3><p>{e(u['lede'])}</p></div><a class="btn btn-glass btn-sm" href="{r}use-cases/{u['slug']}.html">Open the {e(lc(u['name']))} demo <span class="arr">→</span></a></div>
  {DEMOS[u['slug']]()}
</div>"""
    return f'<div class="uc-switch"><div class="uc-tabs glass-strong" role="tablist" aria-label="Live demos">{tabs}</div>{panels}</div>'

def uc_card(r, u):
    return f"""<a class="related glass-card" href="{r}use-cases/{u['slug']}.html"><b>{e(u['name'])} demo</b><span>{e(u['card'])}</span></a>"""

PROCESS = """<div class="steps">
  <div class="step glass"><div class="step-dot">1</div><h3>Discover</h3><div class="dur">About 1 week</div><p>We map the process, the data and the success metric, and agree on what to build first.</p></div>
  <div class="step glass"><div class="step-dot">2</div><h3>Prototype</h3><div class="dur">2–3 weeks</div><p>A working prototype on your real data that proves the idea before larger spend.</p></div>
  <div class="step glass"><div class="step-dot">3</div><h3>Build</h3><div class="dur">Two-week sprints</div><p>Production code with a demo at the end of every sprint.</p></div>
  <div class="step glass"><div class="step-dot">4</div><h3>Integrate</h3><div class="dur">In parallel</div><p>Connections to your business systems, plus security review and user testing.</p></div>
  <div class="step glass"><div class="step-dot">5</div><h3>Operate</h3><div class="dur">Ongoing</div><p>Monitoring, model evaluation and support, so quality holds up after launch.</p></div>
</div>"""

def contact_block(heading_tag="h2"):
    opts = "".join(f"<option>{e(s['name'])}</option>" for s in SERVICES) + "<option>Not sure yet</option>"
    wa = f'<a class="btn btn-wa btn-sm" href="{WA_URL}" target="_blank" rel="noopener">Chat on WhatsApp</a>' if WHATSAPP else ""
    tel = f'\n      <li><b>Phone</b><a href="tel:{PHONE.replace(" ", "")}">{e(PHONE)}</a></li>' if PHONE else ""
    if WHATSAPP: tel += f'\n      <li><b>WhatsApp</b><a href="{WA_URL}" target="_blank" rel="noopener">{e(WHATSAPP_DISPLAY)}</a></li>'
    book = book_btn("", "btn btn-primary btn-sm", "Book a free 30-min call") if BOOKING_URL else ""
    if BOOKING_URL: tel = f'\n      <li><b>Discovery call</b><a href="{BOOKING_URL}" target="_blank" rel="noopener">Book a free 30-minute video call</a> at a time that suits you</li>' + tel
    return f"""<div class="contact">
  <div class="contact-copy">
    <{heading_tag}>Have a process that <em>should</em> run itself?</{heading_tag}>
    <p>Tell us what you want to automate or build. We reply within one business day with first ideas and a proposed next step.</p>
    <div class="mail"><code id="mail">{EMAIL}</code><button class="btn btn-glass btn-sm" id="copy" type="button">Copy email</button>{wa}{book}</div>
    <ul class="info-list">
      <li><b>Office</b>SDA SERVICES L.L.C-FZ, Meydan Grandstand, 6th floor, Meydan Road, Nad Al Sheba, Dubai, UAE</li>
      <li><b>Hours</b>{HOURS}</li>
      <li><b>Response time</b>Within one business day, with first ideas and a proposed next step</li>{tel}
    </ul>
  </div>
  <form class="lead glass-strong" method="POST" action="/api/contact" novalidate data-mail="{EMAIL}">
    <p hidden><label>Leave this empty<input name="company-website" tabindex="-1" autocomplete="off"></label></p>
    <div class="row2">
      <label for="f-name">Name<input id="f-name" name="name" autocomplete="name" placeholder="Jane Doe"></label>
      <label for="f-email">Work email<input id="f-email" name="email" type="email" autocomplete="email" placeholder="jane@company.com"></label>
    </div>
    <label for="f-company">Company<input id="f-company" name="company" autocomplete="organization" placeholder="Acme Inc."></label>
    <label for="f-topic">What do you need?<select id="f-topic" name="topic">{opts}</select></label>
    <label for="f-msg">Project details<textarea id="f-msg" name="message" placeholder="What process, which systems, and what would success look like?"></textarea></label>
    <button class="btn btn-primary" type="submit" style="justify-self:start">Send request <span class="arr">→</span></button>
    <p class="note" id="note" role="status">We use your details only to reply to this request.</p>
  </form>
</div>"""

def related_reading(r, slugs):
    """Links to insights articles whose topics match any of the given page slugs."""
    # the page's own slug counts most, then the number of shared topics; two cards fit the two-column grid
    hits = sorted((x for x in POSTS if set(x["topics"]) & set(slugs)),
                  key=lambda x: (slugs[0] in x["topics"], len(set(x["topics"]) & set(slugs))), reverse=True)[:2]
    if not hits:
        return ""
    cards = "".join(f'<a class="glass" href="{r}insights/{x["slug"]}.html"><small>Guide</small><b>{e(x["h1"])}</b><span>{e(x["lede"])}</span></a>' for x in hits)
    return f"""<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Related reading</h2><p>Practical guides from our <a class="link" href="{r}insights/index.html">insights</a>.</p></div>
  <div class="posts">{cards}</div>
</div></section>"""

def page(r, path, title, meta, active, body, schema=None, demo=False, noindex=False):
    return head(r, path, title, meta, schema, demo, noindex) + nav(r, active) + f'\n<main id="main">\n{body}\n</main>\n' + footer(r, demo)

def page_hero(r, items, h1, lede, extra="", side=""):
    solo = "" if side else " solo"
    return f"""<header class="page-hero{solo}"><div class="wrap">
  <div>{crumbs(r, items)}<h1>{h1}{SPG()}</h1><p class="lede">{lede}</p>{extra}</div>{side}
</div></header>"""

# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
PROMPTS = [
  dict(q="Automate our invoice approvals", title="An invoice agent that reads, matches and routes", slug="workflow-automation",
       steps=["Read invoices from the inbox and extract line items", "Match each invoice to its purchase order and contract price", "Post clean invoices to your ERP and route exceptions to Finance"],
       time="Prototype in 3–4 weeks"),
  dict(q="Answer customer questions 24/7", title="A support agent that knows your orders and policies", slug="ai-agents",
       steps=["Connect the agent to your help center, orders and CRM", "Answer routine questions and take simple actions, with sources", "Hand complex cases to your team with a summary"],
       time="Prototype in 4–6 weeks"),
  dict(q="Clean up our supplier data", title="One trusted record for every supplier", slug="data-management",
       steps=["Find and merge duplicate suppliers across systems", "Fill gaps such as certificates, contacts and contract dates", "Keep the record current with automatic quality checks"],
       time="First results in 3 weeks"),
  dict(q="Give our technicians a mobile app", title="A field app with photo proof and offline mode", slug="mobile-apps",
       steps=["Job lists, checklists, photos, GPS and signatures on the phone", "Works without signal and syncs when back online", "Reports flow straight into your back office"],
       time="First release in 8–12 weeks"),
]
ASK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0c.6 5.8 3.4 9.9 12 12-8.6 2.1-11.4 6.2-12 12-.6-5.8-3.4-9.9-12-12 8.6-2.1 11.4-6.2 12-12z" fill="currentColor"/></svg>'
SEND_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 16V4M4.5 9.5 10 4l5.5 5.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def answer_html(p, r=""):
    steps = "".join(f"<li><b>Step {i+1}</b>{e(t)}</li>" for i, t in enumerate(p["steps"]))
    return f"""<div class="answer-h"><span class="orb"></span><span>Here is how we would build it</span></div>
<h2>{e(p['title'])}</h2><ol class="answer-steps">{steps}</ol>
<div class="answer-foot"><span class="tag"><i></i>{e(p['time'])} · {e(SVC[p['slug']]['name'])}</span><a class="link" href="{r}services/{p['slug']}.html">See the service <span class="arr">→</span></a></div>"""

def home():
    r = ""
    chips = "".join(f'<button type="button" data-i="{i}">{e(p["q"])}</button>' for i, p in enumerate(PROMPTS))
    pdata = json.dumps([dict(q=p["q"], title=p["title"], steps=p["steps"], time=p["time"], slug=p["slug"], svc=SVC[p["slug"]]["name"]) for p in PROMPTS])
    body = f"""<header class="hero"><div class="wrap">
  <p class="kicker rise">{SP}AI agency in Dubai for the UAE &amp; GCC</p>
  <h1 class="rise">AI that takes <span class="soft">manual work</span> off your team{SPG()}</h1>
  <p class="lede rise d1">From Dubai, SDA AI Services designs, builds and runs <b>AI agents, automation and custom software</b> for companies across the UAE and GCC that want working systems in production, not slide decks.</p>
  <div class="cta-row rise d2">{book_btn(r)}<a class="btn btn-glass" href="use-cases/index.html">Try the live demos</a></div>
  <ul class="hero-trust rise d2" aria-label="Why it is low risk"><li>{CHECK_ICON}<span><b>Free pilot</b>, no obligation</span></li><li>{CHECK_ICON}<span>Fixed prices</span></li><li>{CHECK_ICON}<span>Reply within one business day</span></li></ul>
  <div class="ask rise d3" id="prompt">
    <form class="ask-bar" id="ask-form" role="search" aria-label="Describe what you want to automate">
      <div class="ask-in">{ASK_ICON}<label for="ask-q" class="skip" style="position:absolute;left:-999px">What should AI do for you?</label>
        <input id="ask-q" name="q" autocomplete="off" placeholder="What should AI do for your business?">
        <button class="ask-go" type="submit" aria-label="Show how we would build it">{SEND_ICON}</button></div>
    </form>
    <div class="ask-chips">{chips}</div>
    <div class="answer glass-strong" id="answer" aria-live="polite">{answer_html(PROMPTS[0])}</div>
    <script type="application/json" id="ask-data">{pdata}</script>
  </div>
</div></header>

<section class="video-sec" aria-label="Video: our services in 35 seconds"><div class="wrap"><figure class="video-wide"><video src="/assets/media/sda-ai-services.mp4" poster="/assets/media/sda-ai-services.jpg" width="1920" height="1080" muted loop playsinline autoplay controls preload="metadata" aria-label="Video: our services in 35 seconds"></video><figcaption><i class="pulse-dot" aria-hidden="true"></i>Our services in 35 seconds</figcaption></figure></div></section>

<section class="block" id="services"><div class="wrap">
  <div class="sec-head"><h2>Six ways we put AI to work</h2><p>Each engagement goes from first prototype to production code, with the integrations, security and monitoring an operations team needs.</p></div>
  {bento(r)}
</div></section>

<section class="block" id="use-cases" style="padding-top:20px"><div class="wrap">
  <div class="sec-head"><h2>Try it before you talk to us</h2><p>{["Four","Five","Six","Seven","Eight","Nine","Ten"][len(USE_CASES)-4] if 4 <= len(USE_CASES) <= 10 else len(USE_CASES)} working demos of the kind of software we build. Pick one, switch between the roles and click through it: everything runs in your browser on example data.</p></div>
  {uc_switch(r)}
</div></section>

<section class="block" id="industries" style="padding-top:20px"><div class="wrap">{industries_block(r)}</div></section>

<section class="block" id="process" style="padding-top:20px"><div class="wrap">
  <div class="sec-head"><h2>From idea to production in five steps</h2><p>Short cycles, working software at every checkpoint, and a fixed scope for each phase so budget and timeline stay predictable.</p></div>
  {PROCESS}
</div></section>

<section class="block" id="stack" style="padding-top:20px"><div class="wrap">
  <div class="sec-head"><h2>Built to last, not just to demo</h2><p>We pick models and infrastructure by cost, accuracy and data-protection needs, and we build so your team can run it. <a class="link" href="about.html">More about us <span class="arr">→</span></a></p></div>
  <div class="trust">
    <div class="princ glass">
      <div><span class="pi">{_I('<path d="M12 3 4 6v6c0 4.4 3.4 8.3 8 9 4.6-.7 8-4.6 8-9V6z"/>')}</span><h3>Enterprise experience</h3><p>Our team has delivered large enterprise projects, so we plan for security, compliance and change management from day one.</p></div>
      <div><span class="pi">{_I('<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>')}</span><h3>Your data stays yours</h3><p>Privacy-first architecture, hosting in the environment you choose, and no training on your data without your consent.</p></div>
      <div><span class="pi">{_I('<path d="M4 19V9M10 19V5M16 19v-6M22 19H2"/>')}</span><h3>Measured results</h3><p>Every project starts with a metric, such as hours saved or response time, and we report against it.</p></div>
      <div><span class="pi">{_I('<path d="M8 7 3 12l5 5M16 7l5 5-5 5"/>')}</span><h3>Built to hand over</h3><p>Clean code, documentation and training, so your team can own and extend what we build.</p></div>
    </div>
    <div class="stackc glass"><h3>Proven tools, chosen per project</h3><p>Models, frameworks and platforms we work with every day.</p>
      <ul class="cloud">{''.join(f'<li class="{"k" if k else ""}">{t}</li>' for t, k in [("Claude",1),("GPT",1),("Gemini",1),("Llama",0),("Mistral",0),("RAG",1),("MCP",0),("Vector databases",0),("Evals & tracing",0),("TypeScript",0),("React",0),("Next.js",0),("Python",0),("FastAPI",0),("Flutter",0),("AWS",0),("Azure",0),("Google Cloud",0),("SAP BTP",0),("Docker",0),("Kubernetes",0)])}</ul></div>
  </div>
</div></section>

<section class="block" style="padding-top:20px"><div class="wrap">
  <div class="sec-head"><h2>Insights for UAE and GCC companies</h2><p>Practical guides on AI costs, e-invoicing, data protection and automation. <a class="link" href="insights/index.html">All insights <span class="arr">→</span></a></p></div>
  <div class="posts">{"".join(f'<a class="glass" href="insights/{x["slug"]}.html"><small>Guide</small><b>{e(x["h1"])}</b><span>{e(x["lede"])}</span></a>' for x in POSTS[:4])}</div>
</div></section>
<section class="block" id="contact" style="padding-top:20px"><div class="wrap">{contact_block()}</div></section>"""
    video_ld = {"@context": "https://schema.org", "@type": "VideoObject", "name": "SDA AI Services in 35 seconds",
                "description": "AI agents, workflow automation and custom software for companies in the UAE and GCC, built by SDA AI Services in Dubai.",
                "thumbnailUrl": SITE_URL + "/assets/media/sda-ai-services.jpg", "contentUrl": SITE_URL + "/assets/media/sda-ai-services.mp4",
                "uploadDate": "2026-11-10", "duration": "PT35S", "inLanguage": "en", "publisher": {"@id": ORG_ID}}
    return page(r, "", *SEO["home"], "home", body, [ORG_LD, WEBSITE_LD, video_ld], demo=True)

def services_hub():
    r = "../"
    body = page_hero(r, [("Home", "index.html"), ("Services", None)], "AI software and app development services",
                     "From AI agents to enterprise integration, we cover the full path from idea to production software. Pick a service to see what we deliver, typical projects and answers to common questions.") + f"""
<section class="block" style="padding-top:20px"><div class="wrap">{bento(r)}</div></section>
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Focused solutions</h2><p>Proven setups for the requests we hear most often in the UAE and GCC.</p></div>
  <div class="related">{"".join(f'<a class="glass" href="{r}solutions/{x["slug"]}.html"><b>{e(x["name"])}</b><span>{e(x["meta"])}</span></a>' for x in LP_BY_KIND["solutions"])}</div>
  <p class="note" style="margin-top:22px">Looking for your sector or country? See <a class="link" href="{r}industries/index.html">AI by industry</a> and <a class="link" href="{r}locations/index.html">AI across the GCC</a>.</p>
</div></section>
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>One process for every service</h2><p>Short cycles and working software at every checkpoint.</p></div>{PROCESS}
</div></section>
{cta_band(r)}"""
    ld = [crumb_ld([("Home", ""), ("Services", "services/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": abs_url(f"services/{s['slug']}.html"), "name": s["name"]} for i, s in enumerate(SERVICES)]}]
    return page(r, "services/", *SEO["services"], "services", body, ld)

def service_page(s):
    r = "../"
    path = f"services/{s['slug']}.html"
    items = [("Home", "index.html"), ("Services", "services/index.html"), (s["name"], None)]
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in s["facts"])
    deliver = "".join(f'<div class="glass"><h3>{SP}{e(t)}</h3><p>{e(d)}</p></div>' for t, d in s["deliver"])
    ex = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in s["examples"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in s["faq"])
    others = [x for x in SERVICES if x["slug"] != s["slug"]][:3]
    rel = "".join(f'<a class="glass" href="{x["slug"]}.html"><b>{e(x["name"])}</b><span>{e(x["short"])}</span></a>' for x in others)
    u = UC[s["usecase"]]
    extra = f'<div class="cta-row"><a class="btn btn-primary" href="{r}contact.html">Discuss your project <span class="arr">→</span></a><a class="btn btn-glass" href="{r}use-cases/{u["slug"]}.html">See the {e(u["name"])} demo</a></div>'
    body = page_hero(r, items, e(s["h1"]).rstrip("."), e(s["lede"]), extra, f'<dl class="facts glass-strong">{facts}</dl>') + f"""
<section class="block" style="padding-top:48px"><div class="wrap two">
  <h2>{e(s['title'])}</h2>
  <div class="prose">{''.join(f'<p>{e(p)}</p>' for p in s['intro'])}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>What we deliver</h2><p>Choose the parts you need. We can deliver a complete solution or work alongside your own team.</p></div>
  <div class="deliv">{deliver}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <div><h2>Where it pays off</h2><p class="intro">Examples of where companies put {e(s['name'])} to work today.</p></div>
  <ul class="ex-list glass">{ex}</ul>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>How a project runs</h2><p>Working software at every checkpoint, so you can decide with real results in hand.</p></div>{PROCESS}
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Common questions</h2>
  <div class="faq glass">{faq}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Often combined with</h2></div>
  <div class="related">{rel}</div>
</div></section>
{related_reading(r, [s['slug']])}
{cta_band(r, f"Ready to talk about {e(s['name'])}?")}"""
    ld = [crumb_ld([("Home", ""), ("Services", "services/"), (s["name"], path)]),
          {"@context": "https://schema.org", "@type": "Service", "name": s["title"], "serviceType": s["name"], "description": SEO[s["slug"]][1],
           "provider": {"@id": ORG_ID}, "areaServed": [{"@type": "Country", "name": c} for c in GCC], "url": abs_url(path)},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]]}]
    return page(r, path, *SEO[s["slug"]], "services", body, [ORG_LD] + ld)

def uc_hub():
    r = "../"
    body = page_hero(r, [("Home", "index.html"), ("Use cases", None)], "See what AI software can do for your team",
                     f"{len(USE_CASES)} interactive demos of the software we build. Each runs in your browser on example data, and each can be adapted to your processes and connected to your systems.") + f"""
<section class="block" style="padding-top:20px"><div class="wrap">{uc_switch(r)}</div></section>
{cta_band(r, "Need something similar?", "We adapt these demos to your data, processes and systems, usually starting with a two-week prototype.")}"""
    t, m = SEO["use-cases"]
    return page(r, "use-cases/", t.format(n=len(USE_CASES)), m.format(n=len(USE_CASES)),
                "use-cases", body, [crumb_ld([("Home", ""), ("Use cases", "use-cases/")])], demo=True)


def uc_page(u):
    r = "../"
    path = f"use-cases/{u['slug']}.html"
    items = [("Home", "index.html"), ("Use cases", "use-cases/index.html"), (u["name"], None)]
    how = '<div class="howto">' + "".join(f'<div class="glass"><b>{e(t)}</b><span>{e(d)}</span></div>' for t, d in u["how"]) + "</div>"
    rel = "".join(f'<a class="glass" href="{r}services/{k}.html"><b>{e(SVC[k]["name"])}</b><span>{e(SVC[k]["short"])}</span></a>' for k in u["services"])
    others = "".join(f'<a class="glass" href="{r}use-cases/{x["slug"]}.html"><b>{e(x["name"])} demo</b><span>{e(x["card"])}</span></a>' for x in USE_CASES if x["slug"] != u["slug"])
    svc_names = " and ".join(lc(SVC[k]["name"]) for k in u["services"][:2])
    uc_faq = [
        ("Can we get a solution like this for our company?", f"Yes. The {lc(u['name'])} demo shows the idea with fictional data. We build your version around your own processes, data and systems, combining {svc_names}."),
        ("How long does it take to build a solution like this?", "We start with a free pilot on your own examples, usually within one to two weeks. A production version typically follows within a few weeks, depending on integrations."),
        ("Does it connect to our existing systems?", "Yes. We connect to ERP systems such as SAP, CRMs, email, calendars and spreadsheets through secure, approved interfaces."),
        ("Does it work in Arabic and English?", "Yes. Screens, documents and AI answers can be built in English and Arabic, including right-to-left layouts."),
    ]
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in uc_faq)
    body = page_hero(r, items, e(u["h1"]).rstrip("."), e(u["lede"]), how) + f"""
<section class="demo-stage"><div class="wrap">{DEMOS[u['slug']]()}
  <p class="note" style="margin-top:16px">This demo runs in your browser with fictional example data. In a real project it connects to your systems and uses a language model for the AI steps.</p>
</div></section>
<section class="block" style="padding-top:20px"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Services behind this demo</h2><p>We combine these services to build solutions like this one around your processes.</p></div>
  <div class="related">{rel}</div>
</div></section>
<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Questions about this demo</h2>
  <div class="faq glass">{faq}</div>
</div></section>
{related_reading(r, [u['slug']] + u['services'])}
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>More demos</h2></div>
  <div class="related" style="grid-template-columns:repeat(auto-fit,minmax(260px,1fr))">{others}</div>
</div></section>
{cta_band(r, e(u.get('cta') or f"Want this for your {u['label'].lower()} team?"), "We adapt the demo to your data and systems, usually starting with a two-week prototype.")}"""
    ld = [crumb_ld([("Home", ""), ("Use cases", "use-cases/"), (u["name"], path)]),
          {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": f"{u['name']} demo", "applicationCategory": "BusinessApplication",
           "operatingSystem": "Web", "description": u["meta"], "url": abs_url(path), "creator": {"@id": ORG_ID},
           "offers": {"@type": "Offer", "price": "0", "priceCurrency": "AED", "description": "Free interactive demo"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in uc_faq]}]
    t, m = SEO.get(u["slug"], (u["title"], u["meta"]))
    return page(r, path, t, m, "use-cases", body, ld, demo=True)

# --------------------------------------------------------------------------
# Pricing (UAE market prices, AED, excl. 5 % VAT)
# --------------------------------------------------------------------------
PRICES = [
  ("ai-agents", "13,900", "per agent, fixed price", ["Chat, WhatsApp or voice", "Answers from your documents", "Actions in your systems", "Guardrails and human approval"]),
  ("workflow-automation", "11,900", "per process, fixed price", ["Emails, documents, approvals", "Connected to ERP, CRM or email", "Exception queue for your team", "Dashboard of time saved"]),
  ("data-management", "10,900", "per dashboard or data project", ["KPI dashboards, live data", "Data from ERP, Excel and tools", "Clean master data", "Alerts and reports"]),
  ("web-applications", "11,900", "one-time, fixed price", ["Portals and internal tools", "Roles and permissions", "Built only for your company", "Integrations to your systems"]),
  ("mobile-apps", "11,900", "one-time, fixed price", ["iOS and Android", "Photos, GPS and signatures", "Works offline in the field", "Synced to your back office"]),
  ("sap-integration", None, "priced after the free discovery call", ["SAP and other ERP systems", "APIs and data pipelines", "Single sign-on", "Secure, monitored interfaces"]),
]
PLANS = [
  ("Essential", "For apps and automations", "1,100", None, ["Hosting and monitoring", "Security updates", "Bug fixing", "Response next business day"], False),
  ("Business", "For software your team uses daily", "2,200", "Recommended", ["Everything in Essential", "4 hours of changes per month", "Response within 8 hours", "Monthly status report"], True),
  ("Premium", "For business-critical systems", "4,400", None, ["Everything in Business", "8 hours of changes per month", "Response within 4 hours", "Priority handling"], False),
]
PRICE_FAQ = [
  ("What does the pilot project cost?", "Nothing. We build a pilot for one use case, free of charge and with no obligation. You test it with your own examples. Only if you say yes do we agree on a fixed price for the full solution."),
  ("What does unlimited revisions mean?", "We revise designs, screens and features within the agreed scope until you approve them. Revision rounds are never billed extra."),
  ("Why do you show starting prices?", "Every solution is built for your company. The final price depends on scope, such as integrations, user roles and languages. After the pilot you get a binding fixed price."),
  ("Do you charge per user?", "No. Project prices are one-time and operations plans are per company. Your whole team can use the software at no extra cost. Only AI model usage depends on volume and is billed at cost."),
  ("Are prices including VAT?", "No. All prices are in AED and exclude 5 % UAE VAT."),
  ("Do you offer Arabic?", "Yes. Interfaces and AI assistants can be built in English and Arabic, including right-to-left layouts."),
]
PILOT_RULES = ["One use case: one agent, one workflow or one screen flow", "Up to 5 working days of build effort on our side", "You provide sample data and one contact person", "Runs in our test environment, not your live systems", "No contract and no cost if you say no"]

def pricing():
    r = ""
    items = [("Home", "index.html"), ("Pricing", None)]
    side = f"""<dl class="facts glass-strong"><div><dt>Pilot project</dt><dd class="hl">Free</dd></div><div><dt>Revisions</dt><dd class="hl">Unlimited</dd></div><div><dt>Pricing</dt><dd>Fixed price per project</dd></div><div><dt>Per-user fees</dt><dd>None</dd></div><div><dt>Currency</dt><dd>AED, excl. 5 % VAT</dd></div></dl>"""
    extra = f'<div class="cta-row"><a class="btn btn-primary" href="{r}contact.html">Request a free pilot <span class="arr">→</span></a><a class="btn btn-glass" href="#prices">See prices</a></div>'
    hero = page_hero(r, items, "Free pilot. Unlimited revisions.", "No off-the-shelf software: we build solutions for your company. Your pilot project is <b>free of charge</b>, we revise it <b>until you are happy</b>, and you only pay once you say yes.", extra, side)
    rules = "".join(f"<li>{CHECK}<span>{e(x)}</span></li>" for x in PILOT_RULES)
    rev = "".join(f"<li>{CHECK}<span>{e(x)}</span></li>" for x in ["Designs and screens", "Features and workflows", "Texts in English and Arabic", "Every round included until you approve"])
    promise = f"""<section class="block" style="padding-top:20px"><div class="wrap">
  <div class="promise">
    <div class="promise-card glass-strong">
      <div class="promise-top"><span class="promise-big">AED 0</span><div><h2>Free pilot project</h2><p>We build a working pilot for your use case without you paying anything. You test it with real examples. Only if you say yes do we talk about working together.</p></div></div>
      <ul class="promise-rules">{rules}</ul>
    </div>
    <div class="promise-card glass-strong alt">
      <div class="promise-top"><span class="promise-big inf" aria-hidden="true">∞</span><div><h2>Unlimited revisions</h2><p>We refine designs, screens and features within the agreed scope until you approve them. No revision is ever billed extra.</p></div></div>
      <ul class="promise-rules">{rev}</ul>
      <a class="btn btn-primary" href="{r}contact.html" style="justify-self:start">Start your free pilot <span class="arr">→</span></a>
    </div>
  </div>
</div></section>"""
    cards = ""
    for slug, price, unit, feats, in [(a, b, c, d) for a, b, c, d in PRICES]:
        sv = SVC[slug]
        hl = " hl" if slug == "ai-agents" else ""
        pr = f'<div class="price"><small>from</small><b>AED {price}</b></div>' if price else '<div class="price"><b class="req">On request</b></div>'
        f = "".join(f"<li>{CHECK}<span>{e(x)}</span></li>" for x in feats)
        cards += f"""<article class="price-card glass{hl}"><span class="d-ic" aria-hidden="true">{ICONS[sv['icon']]}</span><h3>{e(sv['name'])}</h3>{pr}<p class="unit">{e(unit)}</p><ul>{f}</ul><a class="link" href="{r}services/{slug}.html">More on {e(lc(sv['name']))} <span class="arr">→</span></a></article>"""
    plans = ""
    for name, forr, price, badge, feats, star in PLANS:
        f = "".join(f"<li>{CHECK}<span>{e(x)}</span></li>" for x in feats)
        b = f'<span class="badge">{e(badge)}</span>' if badge else ""
        plans += f"""<article class="plan glass{' star' if star else ''}">{b}<h3>{e(name)}</h3><p class="unit">{e(forr)}</p><div class="price"><small>AED</small><b>{price}</b></div><p class="unit">per month, per company</p><ul>{f}</ul></article>"""
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in PRICE_FAQ)
    steps = """<div class="steps s4">
  <div class="step glass"><div class="step-dot">1</div><h3>Discovery call</h3><div class="dur">Free · 30 minutes</div><p>We find the task that costs your team the most time and what a solution would bring.</p></div>
  <div class="step glass"><div class="step-dot">2</div><h3>Free pilot</h3><div class="dur">AED 0 · no obligation</div><p>A working pilot for one use case. You test it with your own examples and ask for as many changes as you need.</p></div>
  <div class="step glass"><div class="step-dot">3</div><h3>Build</h3><div class="dur">Fixed price · only after your OK</div><p>Once you are convinced, we build the full solution at the agreed fixed price and connect your systems.</p></div>
  <div class="step glass"><div class="step-dot">4</div><h3>Operate</h3><div class="dur">From AED 1,100 / month</div><p>Hosting, monitoring, updates and improvements for a fixed monthly fee per company.</p></div>
</div>"""
    body = hero + promise + f"""
<section class="block" id="prices" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>Typical prices per service</h2><p>Starting prices below the usual UAE market rate, for the full solution after your free pilot. One-time and fixed, with no per-user fees.</p></div>
  <div class="price-grid">{cards}</div>
  <div class="price-extras">
    <div class="glass"><b>Large platforms and AI software</b><span>Several modules, custom AI agents or multi-site rollouts: <strong>from AED 135,000</strong>.</span></div>
    <div class="glass"><b>Government and free zone procurement</b><span>Quotes for tenders and supplier registrations: <strong>on request</strong>.</span></div>
  </div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>We keep it running after launch</h2><p>Operations plans per company, not per user. Extra hours cost AED 270, or AED 2,490 for a 10-hour pack. AI model usage is billed at cost.</p></div>
  <div class="plan-grid">{plans}</div>
  <p class="note" style="text-align:center;margin-top:22px">All prices in AED, excluding 5 % UAE VAT. Payment: 50 % on order, 50 % on acceptance.</p>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>Test first, then decide</h2><p>You see working software before you spend anything.</p></div>{steps}
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Questions about pricing</h2>
  <div class="faq glass">{faq}</div>
</div></section>
{cta_band(r, "Start with a free pilot", "Tell us about your process. We reply within one business day and propose a pilot you can test at no cost.")}"""
    ld = [crumb_ld([("Home", ""), ("Pricing", "pricing.html")]),
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in PRICE_FAQ]}]
    return page(r, "pricing.html", *SEO["pricing"], "pricing", body, ld)

def lp_page(p):
    r = "../"
    kind = p["kind"]; hub = HUBS[kind]
    path = f"{kind}/{p['slug']}.html"
    items = [("Home", "index.html"), (hub["name"], f"{kind}/index.html"), (p["name"], None)]
    facts = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in p["facts"])
    d0 = UC[p["demos"][0]]
    extra = f'<div class="cta-row"><a class="btn btn-primary" href="{r}contact.html">Request a free pilot <span class="arr">→</span></a><a class="btn btn-glass" href="{r}use-cases/{d0["slug"]}.html">Try the {e(d0["name"])} demo</a></div>'
    points = "".join(f'<div class="glass"><h3>{SP}{e(t)}</h3><p>{e(d)}</p></div>' for t, d in p["points"])
    ex = "".join(f"<li><b>{e(t)}</b><span>{e(d)}</span></li>" for t, d in p["examples"])
    demos = "".join(f'<a class="glass" href="{r}use-cases/{k}.html"><b>{e(UC[k]["name"])} demo</b><span>{e(UC[k]["card"])}</span></a>' for k in p["demos"])
    svcs = "".join(f'<a class="glass" href="{r}services/{k}.html"><b>{e(SVC[k]["name"])}</b><span>{e(SVC[k]["short"])}</span></a>' for k in p["services"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    others = "".join(f'<a href="{r}{kind}/{x["slug"]}.html">{e(x["name"])}</a>' for x in LP_BY_KIND[kind] if x["slug"] != p["slug"])
    typ_h = f"Typical AI projects in {p['city']}" if kind == "locations" else f"Typical {lc(p['name'])} projects" if kind == "industries" else "Typical projects"
    svc_h = f"AI services for companies in {p['name']}" if kind == "locations" else "Services behind it"
    reading = related_reading(r, [p["slug"]] + p["services"])
    body = page_hero(r, items, e(p["h1"]), e(p["lede"]), extra, f'<dl class="facts glass-strong">{facts}</dl>') + f"""
<section class="block" style="padding-top:48px"><div class="wrap two">
  <h2>{e(p['intro_h'])}</h2>
  <div class="prose">{''.join(f'<p>{e(x)}</p>' for x in p['intro'])}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>{e(p['points_h'])}</h2><p>Every part can be delivered on its own or combined into one solution.</p></div>
  <div class="deliv">{points}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <div><h2>{e(typ_h)}</h2><p class="intro">Examples of where AI pays off first.</p></div>
  <ul class="ex-list glass">{ex}</ul>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Try it in your browser</h2><p>Working demos of the kind of software we build, running on example data.</p></div>
  <div class="related">{demos}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>{e(svc_h)}</h2></div>
  <div class="related">{svcs}</div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Common questions</h2>
  <div class="faq glass">{faq}</div>
</div></section>

{reading}
<section class="block" style="padding-top:0"><div class="wrap">
  <p class="note lp-more"><b>More {e(hub['name'].lower())}:</b> {others}</p>
</div></section>
{cta_band(r, e(p['cta']), "Tell us about your process. We reply within one business day and propose a free pilot you can test with your own examples.")}"""
    area = [{"@type": "Country", "name": p["country"]}] if kind == "locations" else [{"@type": "Country", "name": c} for c in GCC]
    svc_ld = {"@context": "https://schema.org", "@type": "Service", "name": p["h1"], "description": p["meta"], "url": abs_url(path),
              "provider": {"@id": ORG_ID}, "areaServed": area,
              "serviceType": {"locations": "AI development and automation", "industries": f"AI solutions for {p['name'].lower()}", "solutions": p["name"]}[kind]}
    if kind == "industries":
        svc_ld["audience"] = {"@type": "BusinessAudience", "audienceType": p["name"]}
    ld = [crumb_ld([("Home", ""), (hub["name"], f"{kind}/"), (p["name"], path)]), svc_ld,
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}]
    return page(r, path, p["title"], p["meta"], "services", body, [ORG_LD] + ld)

def lp_hub(kind):
    r = "../"
    hub = HUBS[kind]
    cards = "".join(f'<a class="glass" href="{r}{kind}/{x["slug"]}.html"><b>{e(x["h1"])}</b><span>{e(x["meta"])}</span></a>' for x in LP_BY_KIND[kind])
    extra = f'<p class="note" style="margin-top:22px">Looking for a specific service? See all <a class="link" href="{r}services/index.html">AI development services</a> or <a class="link" href="{r}pricing.html">typical prices</a>.</p>'
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in hub.get("faq", []))
    intro = f"""<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>{e(hub['intro_h'])}</h2>
  <div class="prose">{''.join(f'<p>{e(x)}</p>' for x in hub['intro'])}</div>
</div></section>""" if hub.get("intro") else ""
    faq_sec = f"""<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Common questions</h2>
  <div class="faq glass">{faq}</div>
</div></section>""" if faq else ""
    body = page_hero(r, [("Home", "index.html"), (hub["name"], None)], e(hub["h1"]), e(hub["lede"])) + f"""
<section class="block" style="padding-top:20px"><div class="wrap"><div class="related">{cards}</div>{extra}</div></section>
{intro}
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>How a project runs</h2><p>Working software at every checkpoint, starting with a free pilot.</p></div>{PROCESS}
</div></section>
{faq_sec}
{cta_band(r)}"""
    ld = [crumb_ld([("Home", ""), (hub["name"], f"{kind}/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": abs_url(f"{kind}/{x['slug']}.html"), "name": x["h1"]} for i, x in enumerate(LP_BY_KIND[kind])]}]
    if hub.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in hub["faq"]]})
    return page(r, f"{kind}/", hub["title"], hub["meta"], "services", body, ld)

ABOUT_FAQ = [
  ("Where is SDA AI Services based?", "Our office is at Meydan Grandstand, 6th floor, Meydan Road, Nad Al Sheba, Dubai, United Arab Emirates. We work with companies across the UAE and the GCC."),
  ("What does SDA stand for?", "SDA stands for Software, Development, Applications & AI Services. The legal entity is SDA SERVICES L.L.C-FZ."),
  ("Which languages do you work in?", "English and Arabic, including right-to-left interfaces and Arabic AI assistants."),
  ("How do projects start?", "With a free 30-minute discovery call and a free pilot for one use case. You only pay once you decide to go ahead."),
]

def about():
    r = ""
    items = [("Home", "index.html"), ("About us", None)]
    side = """<dl class="facts glass-strong"><div><dt>Company</dt><dd>SDA SERVICES L.L.C-FZ</dd></div><div><dt>Office</dt><dd>Meydan, Dubai, UAE</dd></div><div><dt>Experience</dt><dd>10+ years in enterprise software</dd></div><div><dt>Projects</dt><dd>25+ delivered</dd></div><div><dt>Languages</dt><dd>English and Arabic</dd></div></dl>"""
    extra = f'<div class="cta-row">{book_btn(r)}<a class="btn btn-glass" href="{r}use-cases/index.html">Try the live demos</a></div>'
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in ABOUT_FAQ)
    body = page_hero(r, items, "About SDA AI Services", "We are a Dubai-based AI agency. We design, build and run AI agents, automation and custom software for companies in the UAE and GCC that want systems in production, not slide decks.", extra, side) + f"""
<section class="block" style="padding-top:48px"><div class="wrap two">
  <h2>Who we are</h2>
  <div class="prose"><p>SDA stands for <b>Software, Development, Applications &amp; AI Services</b>. Behind the name is a team with more than ten years of experience in enterprise software, including large SAP projects for international companies, and more than 25 delivered projects.</p>
  <p>That background shapes how we build AI. We think about security, compliance, integration and change management from the first day, because we know what it takes for software to run in a real company, with real users and real data. Today we focus entirely on AI: agents and assistants, workflow automation, custom web and mobile apps, data and dashboards, and integration with SAP and other core systems.</p></div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>How we work</h2><p>Six promises that apply to every project.</p></div>
  <div class="deliv">
    <div class="glass"><h3>{SP}Free pilot first</h3><p>You see working software on your own examples before you pay anything. If it does not convince you, you walk away at no cost.</p></div>
    <div class="glass"><h3>{SP}Fixed prices in AED</h3><p>After the pilot you get a binding fixed price. No per-user fees, so your whole team can use what we build.</p></div>
    <div class="glass"><h3>{SP}Unlimited revisions</h3><p>We refine designs, screens and features within the agreed scope until you approve them.</p></div>
    <div class="glass"><h3>{SP}Measured results</h3><p>Every project starts with a metric, such as hours saved or response time, and we report against it.</p></div>
    <div class="glass"><h3>{SP}Your data stays yours</h3><p>Hosting in the environment you choose, in the UAE or your own cloud, and no training on your data without consent.</p></div>
    <div class="glass"><h3>{SP}Built to hand over</h3><p>Clean code, documentation and training, so your team can own and extend what we build.</p></div>
  </div>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head"><h2>From idea to production in five steps</h2><p>Short cycles and working software at every checkpoint.</p></div>{PROCESS}
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <div><h2>Where we work</h2><p class="intro">From our office in Dubai we serve companies across the Gulf, remotely and on site when a project needs it.</p></div>
  <ul class="ex-list glass">{"".join(f'<li><b><a href="{r}locations/{x["slug"]}.html">{e(x["name"])}</a></b><span>{e(x["meta"])}</span></li>' for x in LP_BY_KIND["locations"])}</ul>
</div></section>

<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Common questions</h2>
  <div class="faq glass">{faq}</div>
</div></section>
{cta_band(r, "Let's see what AI can do for your team")}"""
    ld = [ORG_LD, crumb_ld([("Home", ""), ("About us", "about.html")]),
          {"@context": "https://schema.org", "@type": "AboutPage", "name": "About SDA AI Services", "url": abs_url("about.html"), "about": {"@id": ORG_ID}, "mainEntity": {"@id": ORG_ID}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in ABOUT_FAQ]}]
    return page(r, "about.html", "About SDA AI Services | AI Agency in Dubai, UAE",
                "SDA AI Services is a Dubai-based AI agency (SDA SERVICES L.L.C-FZ) with 10+ years of enterprise software experience. Free pilot, fixed prices, English and Arabic.",
                "about", body, ld)

def _fmt_date(d):
    return datetime.date.fromisoformat(d).strftime("%-d %B %Y")

def _read_min(post):
    words = len(re.sub(r"<[^>]+>", " ", post["body"]).split()) + sum(len((q + " " + a).split()) for q, a in post["faq"])
    return max(3, round(words / 220))

def insights_hub():
    r = "../"
    cards = "".join(f'<a class="glass" href="{r}insights/{x["slug"]}.html"><small>{_fmt_date(x["date"])} · {_read_min(x)} min read</small><b>{e(x["h1"])}</b><span>{e(x["lede"])}</span></a>' for x in POSTS)
    body = page_hero(r, [("Home", "index.html"), ("Insights", None)], "Insights on AI for UAE and GCC companies",
                     "Practical guides on AI agents, automation, costs and data protection, written for decision makers in the UAE and GCC. No hype, just what you need to plan a project.") + f"""
<section class="block" style="padding-top:20px"><div class="wrap"><div class="posts">{cards}</div></div></section>
{cta_band(r, "Have a question we have not answered?", "Tell us about your process. We reply within one business day with first ideas and a proposed next step.")}"""
    ld = [crumb_ld([("Home", ""), ("Insights", "insights/")]),
          {"@context": "https://schema.org", "@type": "Blog", "@id": SITE_URL + "/insights/#blog", "name": f"{BRAND} Insights", "url": abs_url("insights/"),
           "inLanguage": "en", "publisher": {"@id": ORG_ID},
           "blogPost": [{"@type": "BlogPosting", "headline": x["h1"], "url": abs_url(f"insights/{x['slug']}.html"), "datePublished": x["date"]} for x in POSTS]}]
    return page(r, "insights/", "AI Insights for UAE & GCC Companies | SDA AI Services",
                "Guides on AI agents, WhatsApp chatbots, invoice automation, AI costs in AED and data protection in the UAE and GCC, from a Dubai AI agency.",
                "insights", body, ld)

def post_page(x):
    r = "../"
    path = f"insights/{x['slug']}.html"
    items = [("Home", "index.html"), ("Insights", "insights/index.html"), (x["h1"], None)]
    meta_line = f'<div class="post-meta"><span>{_fmt_date(x["date"])}</span><span>{_read_min(x)} min read</span><span>By {BRAND}</span></div>'
    take = "".join(f"<li>{e(t)}</li>" for t in x["takeaways"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in x["faq"])
    others = [y for y in POSTS if y["slug"] != x["slug"]][:2]
    more = "".join(f'<a class="glass" href="{y["slug"]}.html"><small>Guide</small><b>{e(y["h1"])}</b><span>{e(y["lede"])}</span></a>' for y in others)
    body = page_hero(r, items, e(x["h1"]), e(x["lede"]), meta_line) + f"""
<section class="block" style="padding-top:36px"><div class="wrap"><article class="article">
  <div class="key-take glass"><b>Key takeaways</b><ul>{take}</ul></div>
  <div class="prose">{x["body"].replace("{r}", r)}</div>
</article></div></section>
<section class="block" style="padding-top:0"><div class="wrap two">
  <h2>Common questions</h2>
  <div class="faq glass">{faq}</div>
</div></section>
<section class="block" style="padding-top:0"><div class="wrap">
  <div class="sec-head left" style="margin-bottom:28px"><h2>Keep reading</h2></div>
  <div class="posts">{more}</div>
</div></section>
{cta_band(r)}"""
    ld = [ORG_LD, crumb_ld([("Home", ""), ("Insights", "insights/"), (x["h1"], path)]),
          {"@context": "https://schema.org", "@type": "BlogPosting", "headline": x["h1"], "description": x["meta"], "url": abs_url(path),
           "mainEntityOfPage": abs_url(path), "datePublished": x["date"], "dateModified": x.get("updated", x["date"]), "inLanguage": "en",
           "image": OG_IMAGE, "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": SITE_URL + "/insights/#blog"}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in x["faq"]]}]
    return page(r, path, x["title"], x["meta"], "insights", body, ld)

CONTACT_FAQ = [
  ("What happens after I send the form?", "We reply within one business day with first ideas, a few questions and a proposal for a free 30-minute discovery call."),
  ("What should I write in the project details?", "A few lines are enough: which process or task you want to improve, which systems are involved (for example SAP, a CRM or Excel) and what success would look like."),
  ("Which languages do you work in?", "English and Arabic. Interfaces, documents and AI assistants can be built in both, including right-to-left layouts."),
  ("Do you work with companies outside the UAE?", "Yes. We are based in Dubai and work with companies across the GCC: Saudi Arabia, Qatar, Kuwait, Bahrain and Oman, mostly remotely with on-site workshops when needed."),
  ("Is the first project really free?", "Yes. We build a pilot for one use case at no cost and with no obligation. You only pay if you decide to go ahead with the full solution."),
]
if WHATSAPP:
    CONTACT_FAQ.insert(1, ("Can I contact you on WhatsApp?", f"Yes. Message us on WhatsApp at {WHATSAPP_DISPLAY}. We answer during business hours: {HOURS}. Messages sent outside these hours get a reply on the next business day."))

def contact():
    r = ""
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in CONTACT_FAQ)
    body = f"""<section class="block" style="padding-top:64px"><div class="wrap">{crumbs(r, [("Home", "index.html"), ("Contact", None)])}{contact_block("h1")}</div></section>
<section class="block" style="padding-top:0"><div class="wrap two">
  <div><h2>Before you get in touch</h2><p class="intro">Answers to what people usually ask before their first call. Prefer to look first? <a class="link" href="{r}use-cases/index.html">Try the live demos</a> or see <a class="link" href="{r}pricing.html">typical prices</a>.</p></div>
  <div class="faq glass">{faq}</div>
</div></section>"""
    ld = [ORG_LD, crumb_ld([("Home", ""), ("Contact", "contact.html")]),
          {"@context": "https://schema.org", "@type": "ContactPage", "name": "Contact SDA AI Services", "url": abs_url("contact.html"), "about": {"@id": ORG_ID}},
          {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
              {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in CONTACT_FAQ]}]
    return page(r, "contact.html", *SEO["contact"], "contact", body, ld)


def simple_page(path, title, meta, h1, body_html, noindex=False):
    r = ""
    hdr = page_hero(r, [("Home", "index.html"), (title, None)], h1, meta)
    body = hdr + f'<section class="block" style="padding-top:12px"><div class="wrap"><div class="prose legal glass">{body_html}</div></div></section>'
    return page(r, path, title, meta, "", body, noindex=noindex)

PRIVACY_UPDATED = "12 November 2026"

def privacy():
    analytics = ("<h2>Website analytics</h2><p>We use Cloudflare Web Analytics to count visits and see which pages are read. It works without cookies, "
                 "does not create user profiles and does not track you across websites.</p>") if ANALYTICS else ""
    whatsapp = ("<h2>WhatsApp</h2><p>If you contact us on WhatsApp, WhatsApp (operated by Meta Platforms) processes your phone number, profile name and messages "
                "under its own terms and privacy policy. We use your messages only to answer your request. The WhatsApp buttons on this website are "
                "plain links: no data is sent to WhatsApp until you open the chat yourself.</p>") if WHATSAPP else ""
    wa_provider = "<li><b>Messaging:</b> WhatsApp (Meta Platforms), only if you contact us there.</li>" if WHATSAPP else ""
    booking = ("<h2>Booking a call</h2><p>If you book a discovery call, Google Calendar (Google LLC) processes your name, email address and the "
               "details you enter to schedule the meeting and send you the invitation. The call takes place on Google Meet. We use these details "
               "only to prepare and hold the call.</p>") if BOOKING_URL else ""
    return simple_page("privacy.html", "Privacy policy", "How SDA AI Services handles personal data on this website and when you contact us.", "Privacy policy", f"""
<p><b>Last updated:</b> {PRIVACY_UPDATED}</p>
<h2>Who is responsible</h2><p>SDA SERVICES L.L.C-FZ (trading as {BRAND}), Meydan Grandstand, 6th floor, Meydan Road, Nad Al Sheba, Dubai, United Arab Emirates. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Data we process when you visit</h2><p>When you visit this website, our hosting provider processes technical data such as your IP address, browser type, the time of access and the pages you request. This is necessary to deliver the website securely and to protect it against attacks. We do not use this data to identify you.</p>
<h2>Cookies</h2><p>This website does not set cookies and does not use advertising or tracking tools.</p>
{analytics}
<h2>Contact form and email</h2><p>When you send the contact form or email us, we process your name, email address, company and message to answer your request and, if you wish, to prepare an offer. The form is processed on our hosting provider's infrastructure and delivered to our business mailbox. You receive a short automatic confirmation by email. We delete this data when it is no longer needed for that purpose, unless we must keep it by law.</p>
{booking}
{whatsapp}
<h2>Demos on this website</h2><p>The interactive demos run entirely in your browser. Text, photos and signatures you enter in a demo are not sent to us or stored.</p>
<h2>Service providers</h2><ul><li><b>Hosting and security:</b> Cloudflare, Inc. (global content delivery network).</li><li><b>Business email:</b> Google Workspace (Google LLC).</li>{wa_provider}<li><b>Fonts:</b> served from our own server. Your browser does not connect to Google Fonts or other font services.</li></ul>
<p>These providers may process data outside the UAE. We rely on their contractual data protection commitments.</p>
<h2>Your rights</h2><p>Under the UAE Personal Data Protection Law (Federal Decree-Law No. 45 of 2021) and, where it applies to you, other data protection laws, you can request access to, correction or deletion of your data, restrict or object to processing, and receive your data in a portable format. Contact us at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
<h2>Changes</h2><p>We update this policy when our website or services change. The date at the top shows the latest version.</p>""")

def legal():
    reg_lines = ([f"Trade licence number: {e(LICENSE_NO)}"] if LICENSE_NO else []) + ([f"Formation number: {e(FORMATION_NO)}"] if FORMATION_NO else [])
    reg = f"<h2>Registration</h2><p>{'<br>'.join(reg_lines)}</p>" if reg_lines else ""
    tel = f'<br>Phone: <a href="tel:{PHONE.replace(" ", "")}">{e(PHONE)}</a>' if PHONE else ""
    return simple_page("legal-notice.html", "Legal notice", "Company information for SDA AI Services (SDA SERVICES L.L.C-FZ, Dubai, UAE).", "Legal notice", f"""
<h2>Company</h2><p>SDA SERVICES L.L.C-FZ<br>Trading as {BRAND} (Software, Development, Applications &amp; AI Services)<br>Meydan Grandstand, 6th floor, Meydan Road<br>Nad Al Sheba, Dubai<br>United Arab Emirates</p>
<h2>Contact</h2><p>Email: <a href="mailto:{EMAIL}">{EMAIL}</a>{tel}<br>Business hours: {HOURS}</p>
{reg}
<h2>Content</h2><p>We prepare the content of this website with care, but cannot guarantee that it is complete, correct and up to date at all times. Prices shown are starting prices in AED, excluding 5 % VAT; binding prices are agreed in a written offer.</p>
<h2>Demos</h2><p>All demos on this website use fictional example data. Names of companies and people in the demos are invented.</p>
<h2>Links</h2><p>We are not responsible for the content of external websites we link to.</p>""")

def thanks():
    return simple_page("thanks.html", "Thank you", "We received your request.", "Thanks, we received your request",
        '<p>We reply within one business day with first ideas and a proposed next step.</p><p><a class="btn btn-primary" href="index.html">Back to the homepage <span class="arr">→</span></a></p>', noindex=True)

def not_found():
    return simple_page("404.html", "Page not found", "This page does not exist.", "This page does not exist",
        '<p>The link may be old or mistyped. Try one of these instead:</p><p><a class="link" href="/index.html">Homepage</a> · <a class="link" href="/services/index.html">Services</a> · <a class="link" href="/use-cases/index.html">Live demos</a> · <a class="link" href="/contact.html">Contact</a></p>', noindex=True)

# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
def standalone(fragment):
    """Wrap a page fragment into a complete HTML document for hosting."""
    head_part, _, rest = fragment.partition('<a class="skip"')
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head_part + '</head>\n<body>\n<a class="skip"' + rest + '\n</body>\n</html>\n')

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in (ROOT / "src" / "assets").iterdir():
        if f.is_dir():
            shutil.copytree(f, OUT / "assets" / f.name)
        else:
            shutil.copy(f, OUT / "assets" / f.name)
    pages = {"index.html": home(), "contact.html": contact(), "services/index.html": services_hub(), "use-cases/index.html": uc_hub(),
             "pricing.html": pricing(), "privacy.html": privacy(), "legal-notice.html": legal(), "thanks.html": thanks(), "404.html": not_found(),
             "about.html": about(), "insights/index.html": insights_hub()}
    for x in POSTS:
        pages[f"insights/{x['slug']}.html"] = post_page(x)
    for s in SERVICES:
        pages[f"services/{s['slug']}.html"] = service_page(s)
    for u in USE_CASES:
        pages[f"use-cases/{u['slug']}.html"] = uc_page(u)
    for kind in HUBS:
        pages[f"{kind}/index.html"] = lp_hub(kind)
    for x in LANDING:
        pages[f"{x['kind']}/{x['slug']}.html"] = lp_page(x)
    for p, frag in pages.items():
        out = OUT / p
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(clean_links(standalone(frag), p), encoding="utf-8")
    # preview entry for the claude.ai artifact (skeleton is added by the host)
    # bundle the demos: shared toolkit first, then each demo in site order
    parts = [DEMO_DIR / "_shared"] + [DEMO_DIR / s for s in DEMO_ORDER]
    (OUT / "assets" / "demos.js").write_text("\n".join((d / f).read_text(encoding="utf-8") for d in parts for f in (["shared.js"] if d.name == "_shared" else ["demo.js"])), encoding="utf-8")
    (OUT / "assets" / "demos.css").write_text("\n".join((d / f).read_text(encoding="utf-8") for d in parts for f in (["shared.css"] if d.name == "_shared" else ["demo.css"])), encoding="utf-8")
    (ROOT / "preview.html").write_text(pages["index.html"], encoding="utf-8")
    today = datetime.date.today().isoformat()
    # lastmod changes only when a page's content changes (hashes kept in src/lastmod.json)
    lm_file = ROOT / "src" / "lastmod.json"
    lm = json.loads(lm_file.read_text()) if lm_file.exists() else {}
    for pth, frag in pages.items():
        h = _hl.sha1(re.sub(r"\?v=[0-9a-f]{8}", "", frag).encode()).hexdigest()[:12]
        if lm.get(pth, {}).get("hash") != h:
            lm[pth] = {"hash": h, "date": today}
    lm = {k: v for k, v in lm.items() if k in pages}
    lm_file.write_text(json.dumps(lm, indent=1, sort_keys=True) + "\n")
    prio = lambda p: "1.0" if p == "index.html" else "0.9" if p in ("services/index.html", "pricing.html", "contact.html", "locations/dubai.html") or p.startswith("services/") else "0.3" if p in ("privacy.html", "legal-notice.html") else "0.8" if p.split("/")[0] in HUBS or p.startswith("insights/") or p == "about.html" else "0.7"
    urls = "".join(f"  <url><loc>{abs_url(p)}</loc><lastmod>{lm[p]['date']}</lastmod><priority>{prio(p)}</priority></url>\n" for p in pages if p not in ("404.html", "thanks.html"))
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    shutil.copy(ROOT / "src" / "_headers", OUT / "_headers")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    # llms.txt: plain-language map of the site for AI search engines (ChatGPT, Perplexity, Gemini, Claude)
    sec = lambda items: "".join(f"- [{n}]({u}): {d}\n" for n, u, d in items)
    llms = (f"# {BRAND}\n\n> Dubai-based AI agency (SDA SERVICES L.L.C-FZ, Meydan, Dubai, UAE). SDA stands for Software, Development, Applications & AI Services. "
            "We build AI agents, workflow automation, custom web and mobile apps, data management and SAP integration for companies in the UAE and GCC. "
            "Every project starts with a free pilot; prices are fixed, in AED, with no per-user fees. Languages: English and Arabic.\n\n"
            f"Contact: {EMAIL}{(' · WhatsApp ' + WHATSAPP_DISPLAY) if WHATSAPP else ''} · {abs_url('contact.html')}\n"
            + (f"Company: SDA SERVICES L.L.C-FZ, trade licence no. {LICENSE_NO}, formation no. {FORMATION_NO}\n" if LICENSE_NO else "") + "\n"
            "## Services\n" + sec([(x["name"], abs_url(f"services/{x['slug']}.html"), SEO[x["slug"]][1]) for x in SERVICES]) +
            "\n## Solutions\n" + sec([(x["name"], abs_url(f"solutions/{x['slug']}.html"), x["meta"]) for x in LP_BY_KIND["solutions"]]) +
            "\n## Industries\n" + sec([(x["name"], abs_url(f"industries/{x['slug']}.html"), x["meta"]) for x in LP_BY_KIND["industries"]]) +
            "\n## Regions\n" + sec([(x["name"], abs_url(f"locations/{x['slug']}.html"), x["meta"]) for x in LP_BY_KIND["locations"]]) +
            "\n## Live demos\n" + sec([(u["name"], abs_url(f"use-cases/{u['slug']}.html"), SEO.get(u["slug"], (0, u["meta"]))[1]) for u in USE_CASES]) +
            "\n## Insights\n" + sec([(x["h1"], abs_url(f"insights/{x['slug']}.html"), x["meta"]) for x in POSTS]) +
            "\n## Company\n" + sec([("About us", abs_url("about.html"), "Who we are, how we work, where we work."), ("Pricing", abs_url("pricing.html"), SEO["pricing"][1]), ("Contact", abs_url("contact.html"), SEO["contact"][1])]))
    (OUT / "llms.txt").write_text(llms, encoding="utf-8")
    (OUT / "site.webmanifest").write_text(json.dumps({"name": BRAND, "short_name": "SDA AI", "start_url": "/", "display": "standalone",
        "background_color": "#F8F7F5", "theme_color": "#C2410C", "icons": [
            {"src": "/assets/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/brand/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2))
    # Cloudflare Pages serves the repository root, so mirror the finished site there as well.
    for item in OUT.iterdir():
        target = ROOT / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy(item, target)
    print(f"Built {len(pages)} pages into {OUT} and mirrored them to the repository root")

if __name__ == "__main__":
    main()
