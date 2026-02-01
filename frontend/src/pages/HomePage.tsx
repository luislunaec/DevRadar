import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, DollarSign, TrendingUp, Sparkles } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const features = [
  {
    icon: DollarSign,
    title: 'Salarios Competitivos',
    description: 'Analiza rangos salariales reales reportados por profesionales.',
  },
  {
    icon: TrendingUp,
    title: 'Tendencias de Stack',
    description: 'Descubre si React, Angular o Vue lideran el mercado y qué tecnologías están en declive.',
  },
  {
    icon: Sparkles,
    title: 'Recomendación con IA',
    description: 'Análisis de perfil con ofertas laborales.',
  },
];

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/dashboard?rol=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex items-center justify-center bg-hero-pattern">
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        
        <div className="container relative z-10 py-20">
          <div className="glass-card max-w-4xl mx-auto p-12 text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Sparkles className="h-4 w-4" />
              Mercado IT Ecuador
            </div>
            
            <h1 className="text-display mb-4">
              Descubre qué tecnologías exige el mercado TI en Ecuador
            </h1>
            
            <p className="text-muted-foreground text-lg mb-8 max-w-2xl mx-auto">
              Datos en tiempo real sobre salarios, tecnologías y oportunidades laborales en el sector tecnológico ecuatoriano.
            </p>

            <form onSubmit={handleSearch} className="flex gap-2 max-w-xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Buscar rol (ej: Backend Developer, Data Scientist...)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-12 h-14 bg-secondary border-border text-lg"
                />
              </div>
              <Button type="submit" size="lg" className="h-14 px-8">
                Analizar Mercado
              </Button>
            </form>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="container">
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="glass-card p-6 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="p-3 rounded-lg bg-primary/10 text-primary w-fit mb-4">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-h3 mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </Layout>
  );
}
