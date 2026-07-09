import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { Hero } from "@/components/hero/Hero";
import { MoatSection } from "@/components/moat/MoatSection";
import { OfferStackSection } from "@/components/offer-stack/OfferStackSection";
import { GuaranteeSection } from "@/components/guarantee/GuaranteeSection";
import { TriageCallSection } from "@/components/triage-call/TriageCallSection";

function App() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <MoatSection />
        <OfferStackSection />
        <GuaranteeSection />
        <TriageCallSection />
      </main>
      <Footer />
    </>
  );
}

export default App;
