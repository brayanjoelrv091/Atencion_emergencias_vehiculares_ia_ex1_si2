import re

with open('landing/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

styles = re.search(r'<style>(.*?)</style>', text, re.DOTALL).group(1)
body = re.search(r'<body class="([^"]*)">(.*)</body>', text, re.DOTALL).group(2)

# Reemplazar onClick con (click) de angular y href a rutas internas
body = body.replace('onclick="toggleMenu()"', '(click)="toggleMenu()"')
body = body.replace('class="md:hidden glass"', '[class]="isMenuOpen ? \'md:hidden glass open\' : \'md:hidden glass\'"')
body = body.replace('id="navbar"', '[class.nav-scrolled]="isNavScrolled"')
body = body.replace('id="navbar" class="', 'id="navbar" class="') # just mapping

# Guardar CSS
with open('frontend/src/app/pages/landing-page/landing-page.component.css', 'w', encoding='utf-8') as f:
    f.write(styles)

# Guardar HTML
with open('frontend/src/app/pages/landing-page/landing-page.component.html', 'w', encoding='utf-8') as f:
    f.write('<div class="tech-grid font-sans antialiased">')
    f.write(body)
    f.write('</div>')
