import { Diamond } from 'lucide-react';
import { Link } from 'react-router-dom';

const footerLinks = [
  { label: 'Fuentes de Datos', href: '#' },
  { label: 'Política de Privacidad', href: '#' },
  { label: 'Términos de Uso', href: '#' },
  { label: 'Contribuir', href: '#' },
];

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background">
      <div className="container py-8">
        <div className="flex flex-col items-center gap-4">
          <Link to="/" className="flex items-center gap-2">
            <Diamond className="h-5 w-5 text-primary" />
            <span className="font-bold">DevRadar Ecuador</span>
          </Link>

          <nav className="flex flex-wrap justify-center gap-6">
            {footerLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <p className="text-xs text-muted-foreground">
            © 2026 DevRadar Ecuador. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </footer>
  );
}
