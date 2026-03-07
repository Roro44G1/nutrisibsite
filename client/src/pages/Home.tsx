import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, CheckCircle2, Leaf, Heart, Droplets, Zap } from "lucide-react";
import { useState } from "react";

/**
 * DESIGN PHILOSOPHY: Organic Wellness Minimalism
 * - Sage green (#7BA882) for trust and nature
 * - Warm cream (#F5F1E8) background for purity
 * - Terracotta (#D4845C) accents for energy
 * - Playfair Display for elegant headings
 * - Asymmetric layout with breathing room
 */

export default function Home() {
  const [expandedSupplement, setExpandedSupplement] = useState<string | null>(null);

  const supplements = [
    {
      id: "red-yeast-rice",
      name: "Orezul Roșu Fermentat",
      scientificName: "Red Yeast Rice (RYR)",
      icon: "🌾",
      image: "https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/supplement-hero-red-yeast-rice-SM2hBMrRNuyZraU4vWrydq.webp",
      efficacy: "Reduce LDL colesterol cu 20-30%",
      dosage: "2-48 mg monacolina K pe zi",
      mechanism: "Inhibă HMG-CoA reductaza, similar cu statinele",
      sideEffects: ["Afectare hepatică", "Interacțiuni medicamentoase"],
      highlights: ["Produs tradițional chinezesc", "Identic chimic cu lovastatina"],
      color: "from-red-100 to-orange-50"
    },
    {
      id: "berberine",
      name: "Berberina",
      scientificName: "Berberine (BBR)",
      icon: "🌿",
      image: "https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/supplement-hero-berberine-YFVAuw9xS5txzAyt6nXwph.webp",
      efficacy: "Reduce colesterolul total cu 0.47 mmol/L",
      dosage: "500-1500 mg pe zi (2-3 doze)",
      mechanism: "Activează AMPK, reduce producția de colesterol hepatic",
      sideEffects: ["Tulburări gastro-intestinale", "Diaree", "Crampe abdominale"],
      highlights: ["Utilizată în medicina tradițională chineză", "Efecte antiinflamatorii"],
      color: "from-yellow-100 to-amber-50"
    },
    {
      id: "plant-sterols",
      name: "Steroli Vegetali",
      scientificName: "Plant Sterols & Stanols (Phytosterols)",
      icon: "🥑",
      image: "https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/supplement-hero-plant-sterols-e2xDZfuRwve6NCSRyPudxv.webp",
      efficacy: "Reduce LDL colesterol cu 8.5-10%",
      dosage: "1.5-3 grame pe zi (2 doze la mese)",
      mechanism: "Concurează cu colesterolul pentru absorbție intestinală",
      sideEffects: ["Reduce absorbția vitaminelor liposolubile (A, D, E, K)"],
      highlights: ["Găsite în nuci, semințe, ulei de măsline", "Sigure cu puține efecte secundare"],
      color: "from-green-100 to-emerald-50"
    },
    {
      id: "soluble-fiber",
      name: "Fibre Solubile",
      scientificName: "Soluble Fiber (Psyllium)",
      icon: "🌾",
      image: "https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/hero-banner-DSifdUy5AGZGEryjknfUv5.webp",
      efficacy: "Reduce LDL colesterol cu 5-10%",
      dosage: "5-10 grame pe zi",
      mechanism: "Formează gel în intestin, leagă colesterolul și acizii biliari",
      sideEffects: ["Balonare", "Gaze", "Disconfort gastro-intestinal"],
      highlights: ["Găsite în ovăz, orzul, mere, citrice", "Beneficii digestive suplimentare"],
      color: "from-blue-100 to-cyan-50"
    },
    {
      id: "omega3",
      name: "Acizi Grași Omega-3",
      scientificName: "Omega-3 Fatty Acids (EPA/DHA)",
      icon: "🐟",
      image: "https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/lifestyle-wellness-scene-TkszLXP9eV5jfpeJZ5RJpa.webp",
      efficacy: "Reduce trigliceride cu 20-30%",
      dosage: "2-4 grame EPA+DHA pe zi",
      mechanism: "Reduce trigliceride, crește HDL, proprietăți antiinflamatorii",
      sideEffects: ["Gust de pește", "Indigestie", "Risc de sângerare la doze mari"],
      highlights: ["Găsite în pești grași (somon, macrou)", "Beneficii cardiovasculare generale"],
      color: "from-indigo-100 to-blue-50"
    }
  ];

  const lifestyleChanges = [
    {
      title: "Dietă Sănătoasă",
      description: "Fructe, legume, cereale integrale, leguminoase și grăsimi sănătoase",
      impact: "Reducere semnificativă a colesterolului",
      icon: <Leaf className="w-6 h-6" />
    },
    {
      title: "Exerciții Fizice",
      description: "Activitate fizică constantă și regulată",
      impact: "Crește HDL, scade LDL și trigliceride",
      icon: <Heart className="w-6 h-6" />
    },
    {
      title: "Greutate Sănătoasă",
      description: "Menținerea unui BMI optim",
      impact: "Pierderea în greutate îmbunătățește profilul lipidic",
      icon: <Zap className="w-6 h-6" />
    },
    {
      title: "Renunțare la Fumat",
      description: "Eliminarea fumatului complet",
      impact: "Îmbunătățește sănătatea cardiovasculară",
      icon: <CheckCircle2 className="w-6 h-6" />
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-border shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Leaf className="w-8 h-8 text-primary" />
            <h1 className="text-xl md:text-2xl font-bold text-primary">Statine Alternative</h1>
          </div>
          <nav className="hidden md:flex gap-6 lg:gap-8 text-sm font-medium">
            <a href="#lifestyle" className="text-foreground hover:text-primary transition duration-200">Stil de viață</a>
            <a href="#supplements" className="text-foreground hover:text-primary transition duration-200">Suplimente</a>
            <a href="#important" className="text-foreground hover:text-primary transition duration-200">Considerații</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/10 via-background to-background py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-center">
            <div>
              <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
                Alternative Naturale la Statine
              </h2>
              <p className="text-base md:text-lg text-muted-foreground mb-8 leading-relaxed">
                Explorează opțiuni naturale, susținute de dovezi științifice, pentru gestionarea colesterolului și sănătatea cardiovasculară.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground transition duration-200">
                  Citește Ghidul Complet
                </Button>
                <Button variant="outline" className="border-primary text-primary hover:bg-primary/5 transition duration-200">
                  Contactează Medicul
                </Button>
              </div>
            </div>
            <div className="relative h-64 sm:h-80 md:h-96 rounded-lg overflow-hidden shadow-lg">
              <img
                src="https://d2xsxph8kpxj0f.cloudfront.net/310519663130980155/nS9e9GnZwWPkqeBoNntz2V/hero-banner-DSifdUy5AGZGEryjknfUv5.webp"
                alt="Ingrediente naturale pentru sănătate"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Introduction */}
      <section className="py-16 bg-white border-b border-border">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="prose prose-lg max-w-none">
            <p className="text-foreground leading-relaxed mb-6">
              Statinele sunt medicamente prescrise frecvent pentru a reduce colesterolul LDL, cunoscut și sub denumirea de „colesterol rău". Deși sunt eficiente în prevenirea bolilor cardiovasculare, unii pacienți pot experimenta efecte adverse sau pot căuta alternative naturale.
            </p>
            <p className="text-foreground leading-relaxed">
              Acest ghid explorează diverse opțiuni naturale, susținute de dovezi științifice, care pot contribui la gestionarea nivelului de colesterol. <strong>Este esențial să rețineți că orice modificare a tratamentului trebuie discutată în prealabil cu medicul curant.</strong>
            </p>
          </div>
        </div>
      </section>

      {/* Lifestyle Changes Section */}
      <section id="lifestyle" className="py-20 bg-background">
        <div className="container mx-auto px-4">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">Modificări ale Stilului de Viață</h2>
            <p className="text-lg text-muted-foreground">Pilonul principal pentru management eficient al colesterolului</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {lifestyleChanges.map((change, idx) => (
              <Card key={idx} className="border-border hover:shadow-md transition-all duration-200 hover:-translate-y-1">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                    {change.icon}
                  </div>
                  <CardTitle className="text-base md:text-lg">{change.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">{change.description}</p>
                  <div className="pt-4 border-t border-border">
                    <p className="text-sm font-medium text-primary">{change.impact}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Supplements Section */}
      <section id="supplements" className="py-20 bg-white border-y border-border">
        <div className="container mx-auto px-4">
          <div className="mb-16">
            <h2 className="text-4xl font-bold text-foreground mb-4">Suplimente Naturale</h2>
            <p className="text-lg text-muted-foreground">Opțiuni cu potențial de reducere a colesterolului</p>
          </div>

          <Tabs defaultValue="red-yeast-rice" className="w-full">
            <TabsList className="grid w-full grid-cols-2 md:grid-cols-5 mb-8">
              {supplements.map((supp) => (
                <TabsTrigger key={supp.id} value={supp.id} className="text-xs md:text-sm">
                  {supp.name.split(" ")[0]}
                </TabsTrigger>
              ))}
            </TabsList>

            {supplements.map((supplement) => (
              <TabsContent key={supplement.id} value={supplement.id}>
                <Card className="border-border overflow-hidden">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 p-4 md:p-8">
                    {/* Image */}
                    <div className="flex flex-col gap-4">
                      <div className={`rounded-lg overflow-hidden h-64 md:h-80 bg-gradient-to-br ${supplement.color}`}>
                        <img
                          src={supplement.image}
                          alt={supplement.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex flex-col justify-between">
                      <div>
                        <div className="mb-6">
                          <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-2">{supplement.name}</h3>
                          <p className="text-xs md:text-sm text-muted-foreground italic">{supplement.scientificName}</p>
                        </div>

                        <div className="space-y-6">
                          {/* Efficacy */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                              <CheckCircle2 className="w-5 h-5 text-primary" />
                              Eficacitate
                            </h4>
                            <p className="text-foreground">{supplement.efficacy}</p>
                          </div>

                          {/* Mechanism */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                              <Zap className="w-5 h-5 text-primary" />
                              Mecanism de Acțiune
                            </h4>
                            <p className="text-foreground">{supplement.mechanism}</p>
                          </div>

                          {/* Dosage */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                              <Droplets className="w-5 h-5 text-primary" />
                              Dozaj Recomandat
                            </h4>
                            <p className="text-foreground">{supplement.dosage}</p>
                          </div>

                          {/* Side Effects */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                              <AlertCircle className="w-5 h-5 text-secondary" />
                              Efecte Secundare Posibile
                            </h4>
                            <ul className="text-foreground space-y-1">
                              {supplement.sideEffects.map((effect, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-secondary mt-1">•</span>
                                  <span>{effect}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          {/* Highlights */}
                          <div>
                            <h4 className="font-semibold text-foreground mb-2">Informații Importante</h4>
                            <ul className="text-foreground space-y-1">
                              {supplement.highlights.map((highlight, idx) => (
                                <li key={idx} className="flex items-start gap-2">
                                  <span className="text-primary mt-1">✓</span>
                                  <span>{highlight}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>

                      <div className="mt-8 pt-6 border-t border-border">
                        <Button className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground">
                          Aflați mai multe
                        </Button>
                      </div>
                    </div>
                  </div>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </div>
      </section>

      {/* Important Considerations */}
      <section id="important" className="py-20 bg-background">
        <div className="container mx-auto px-4 max-w-3xl">
          <h2 className="text-4xl font-bold text-foreground mb-12">Considerații Importante</h2>

          <div className="space-y-6">
            <Card className="border-border border-l-4 border-l-primary hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg md:text-xl">
                  <AlertCircle className="w-5 md:w-6 h-5 md:h-6 text-primary flex-shrink-0" />
                  Consultați Medicul
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground">
                  Niciuna dintre aceste alternative naturale nu ar trebui să înlocuiască tratamentul prescris de medic fără o discuție prealabilă. Medicul poate evalua riscurile și beneficiile și poate monitoriza progresul dumneavoastră.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border border-l-4 border-l-primary hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg md:text-xl">
                  <CheckCircle2 className="w-5 md:w-6 h-5 md:h-6 text-primary flex-shrink-0" />
                  Calitatea Suplimentelor
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground">
                  Alegeți suplimente de la producători de încredere, care oferă produse standardizate și testate pentru puritate și potență.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border border-l-4 border-l-primary hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg md:text-xl">
                  <Zap className="w-5 md:w-6 h-5 md:h-6 text-primary flex-shrink-0" />
                  Interacțiuni Medicamentoase
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground">
                  Suplimentele naturale pot interacționa cu medicamentele prescrise. Informați medicul despre toate suplimentele pe care le luați.
                </p>
              </CardContent>
            </Card>

            <Card className="border-border border-l-4 border-l-primary hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg md:text-xl">
                  <Heart className="w-5 md:w-6 h-5 md:h-6 text-primary flex-shrink-0" />
                  Monitorizare Regulată
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-foreground">
                  Chiar și cu alternative naturale, este importantă monitorizarea regulată a nivelului de colesterol pentru a evalua eficacitatea intervențiilor.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Conclusion */}
      <section className="py-20 bg-white border-t border-border">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="bg-gradient-to-br from-primary/5 to-secondary/5 rounded-lg p-6 md:p-8 border border-border">
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-6">Concluzie</h2>
            <p className="text-foreground leading-relaxed mb-6">
              Există o serie de alternative naturale și modificări ale stilului de viață care pot contribui la gestionarea nivelului de colesterol. Orezul roșu fermentat, berberina, sterolii vegetali, fibrele solubile și acizii grași Omega-3 au demonstrat potențial în studiile științifice.
            </p>
            <p className="text-foreground leading-relaxed mb-6">
              Cu toate acestea, ele nu sunt o soluție universală și eficacitatea lor poate varia de la o persoană la alta. Abordarea cea mai eficientă implică adesea o combinație de modificări ale stilului de viață și, dacă este necesar, suplimente, toate sub supravegherea unui profesionist medical.
            </p>
            <p className="text-foreground font-semibold text-lg">
              Sănătatea dumneavoastră cardiovasculară merită o abordare personalizată și informată.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-foreground text-background py-12 border-t border-border">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="font-bold mb-4 flex items-center gap-2 text-sm md:text-base">
                <Leaf className="w-5 h-5" />
                Alternative Naturale la Statine
              </h3>
              <p className="text-xs md:text-sm opacity-80">
                Ghid complet și bine documentat despre alternative naturale la statine, bazat pe dovezi științifice.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-sm md:text-base">Navigare</h4>
              <ul className="text-xs md:text-sm space-y-2 opacity-80">
                <li><a href="#lifestyle" className="hover:opacity-100 transition duration-200">Stil de viață</a></li>
                <li><a href="#supplements" className="hover:opacity-100 transition duration-200">Suplimente</a></li>
                <li><a href="#important" className="hover:opacity-100 transition duration-200">Considerații</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4 text-sm md:text-base">Disclaimer</h4>
              <p className="text-xs opacity-80">
                Informațiile de pe acest site sunt doar în scop educativ. Consultați întotdeauna un profesionist medical înainte de a face orice schimbări în tratament.
              </p>
            </div>
          </div>
          <div className="border-t border-background/20 pt-8 text-center text-xs md:text-sm opacity-80">
            <p>&copy; 2026 Alternative Naturale la Statine. Toate drepturile rezervate.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
