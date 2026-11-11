"""Helpers and official sources for the private internship study book."""
from html import escape

SOURCES = {
 'V1': ('Vue 3 — Introduction', 'https://vuejs.org/guide/introduction'),
 'V2': ('Vue — Reactivity Fundamentals', 'https://vuejs.org/guide/essentials/reactivity-fundamentals'),
 'V3': ('Vue — Computed Properties', 'https://vuejs.org/guide/essentials/computed.html'),
 'V4': ('Vue — Composables', 'https://vuejs.org/guide/reusability/composables.html'),
 'R1': ('Vue Router — History Modes', 'https://router.vuejs.org/guide/essentials/history-mode.html'),
 'T1': ('Vite 7 — Getting Started', 'https://v7.vite.dev/guide/'),
 'L1': ('Laravel 12 — Request Lifecycle', 'https://laravel.com/framework/docs/12.x/lifecycle'),
 'L2': ('Laravel 12 — Sanctum', 'https://laravel.com/framework/docs/12.x/sanctum'),
 'L3': ('Laravel 12 — Database / Transactions', 'https://laravel.com/framework/docs/12.x/database'),
 'L4': ('Laravel 12 — Eloquent Relationships', 'https://laravel.com/framework/docs/12.x/eloquent-relationships'),
 'L5': ('Laravel 12 — Validation', 'https://laravel.com/framework/docs/12.x/validation'),
 'L6': ('Laravel 12 — Hashing', 'https://laravel.com/framework/docs/12.x/hashing'),
 'L7': ('Laravel 12 — Migrations', 'https://laravel.com/framework/docs/12.x/migrations'),
 'P1': ('PostgreSQL 18 — About PostgreSQL', 'https://www.postgresql.org/about/'),
 'P2': ('PostgreSQL 18 — Constraints', 'https://www.postgresql.org/docs/18/ddl-constraints.html'),
 'P3': ('PostgreSQL 18 — Numeric Types', 'https://www.postgresql.org/docs/18/datatype-numeric.html'),
 'P4': ('PostgreSQL 18 — MVCC', 'https://www.postgresql.org/docs/18/mvcc-intro.html'),
 'P5': ('PostgreSQL 18 — Transaction Isolation', 'https://www.postgresql.org/docs/18/transaction-iso.html'),
 'P6': ('PostgreSQL 18 — Explicit Locking', 'https://www.postgresql.org/docs/18/explicit-locking.html'),
 'P7': ('PostgreSQL 18 — Indexes', 'https://www.postgresql.org/docs/18/indexes-intro.html'),
 'P8': ('PostgreSQL 18 — Transactions', 'https://www.postgresql.org/docs/18/tutorial-transactions.html'),
 'P9': ('PostgreSQL 18 — Date/Time Types', 'https://www.postgresql.org/docs/18/datatype-datetime.html'),
 'C1': ('Chart.js — Introduction', 'https://www.chartjs.org/docs/latest/'),
 'C2': ('Chart.js — Accessibility', 'https://www.chartjs.org/docs/latest/general/accessibility.html'),
 'H1': ('PHP — Introduction', 'https://www.php.net/whatisphp'),
 'N1': ('Node.js — Introduction', 'https://nodejs.org/learn/getting-started/introduction-to-nodejs'),
 'E1': ('Playwright — Test Isolation', 'https://playwright.dev/docs/browser-contexts'),
 'J1': ('MDN — Number.MAX_SAFE_INTEGER', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER'),
}


def cite(*ids):
    return '<p class="sources">Rujukan konsep: '+ ' · '.join(f'<a href="{SOURCES[i][1]}">{i} — {escape(SOURCES[i][0])}</a>' for i in ids)+'</p>'


def p(text):
    return '<p>'+text+'</p>'


def h(text):
    return '<h3>'+text+'</h3>'


def ul(*items):
    return '<ul>'+''.join('<li>'+item+'</li>' for item in items)+'</ul>'


def table(headers, rows, cls=''):
    return f'<table class="{cls}"><thead><tr>'+''.join('<th>'+str(c)+'</th>' for c in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'


def note(title, text, kind=''):
    return f'<aside class="{kind}"><strong>{title}</strong><p>{text}</p></aside>'


def code(text):
    return '<pre><code>'+escape(text.strip())+'</code></pre>'


def page(section, title, lead, body, kind=''):
    return {'section':section,'title':title,'lead':lead,'body':body,'kind':kind}


def qa(question, answer):
    return '<div class="qa"><h3>'+question+'</h3><p>'+answer+'</p></div>'
