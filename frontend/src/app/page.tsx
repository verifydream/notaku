import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  MessageCircle,
  Receipt,
  BarChart3,
  CreditCard,
  Smartphone,
  Zap,
  CheckCircle2,
} from "lucide-react";

const WA_LINK = "https://wa.me/6281234567890?text=Halo%20NotaKu%2C%20mau%20coba%20catat%20usaha";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📒</span>
          <span className="text-xl font-bold text-amber-900">NotaKu</span>
        </div>
        <Badge variant="secondary" className="bg-amber-100 text-amber-800">
          Beta — Gratis
        </Badge>
      </nav>

      {/* Hero */}
      <section className="px-6 pt-16 pb-24 text-center max-w-3xl mx-auto">
        <Badge className="mb-4 bg-green-100 text-green-800 border-green-200">
          🇮🇩 Made for Indonesia
        </Badge>
        <h1 className="text-4xl sm:text-5xl font-bold text-amber-950 leading-tight mb-6">
          Chat → Nota → <span className="text-amber-600">Selesai.</span>
        </h1>
        <p className="text-lg text-amber-800/70 mb-8 max-w-xl mx-auto">
          Catat usaha tanpa buka app. Cukup kirim pesan di WhatsApp,
          NotaKu otomatis catat transaksi, bikin nota, dan rekap keuanganmu.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <a href={WA_LINK} target="_blank" rel="noopener">
            <Button size="lg" className="bg-green-600 hover:bg-green-700 text-white px-8 py-6 text-lg rounded-2xl shadow-lg shadow-green-200">
              <MessageCircle className="mr-2 h-5 w-5" />
              Mulai via WhatsApp
            </Button>
          </a>
          <a href="#fitur">
            <Button size="lg" variant="outline" className="px-8 py-6 text-lg rounded-2xl border-amber-200 text-amber-800">
              Lihat Fitur →
            </Button>
          </a>
        </div>
        <p className="mt-6 text-sm text-amber-700/50">
          Tanpa install. Tanpa daftar. Tanpa ribet.
        </p>
      </section>

      {/* How it works */}
      <section className="px-6 py-16 bg-white">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h2 className="text-3xl font-bold text-amber-950 mb-3">Gimana caranya?</h2>
          <p className="text-amber-700/60">Tiga langkah, selesai.</p>
        </div>
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          {[
            { step: "1", icon: "💬", title: "Kirim Pesan", desc: "Chat NotaKu: \"3 nasi uduk, 1 kopi susu\"" },
            { step: "2", icon: "✅", title: "Konfirmasi", desc: "NotaKu tampilkan ringkasan. Ketik \"oke\" untuk konfirmasi." },
            { step: "3", icon: "🧾", title: "Nota Terkirim", desc: "PDF nota otomatis dikirim ke pelanggan via WhatsApp." },
          ].map((s) => (
            <Card key={s.step} className="border-amber-100 shadow-sm">
              <CardContent className="pt-8 pb-6 text-center">
                <div className="text-4xl mb-4">{s.icon}</div>
                <div className="text-xs font-bold text-amber-500 mb-2">LANGKAH {s.step}</div>
                <h3 className="text-lg font-bold text-amber-900 mb-2">{s.title}</h3>
                <p className="text-sm text-amber-700/60">{s.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="fitur" className="px-6 py-20 bg-amber-50/50">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h2 className="text-3xl font-bold text-amber-950 mb-3">Fitur Utama</h2>
          <p className="text-amber-700/60">Yang warungmu butuh, bukan yang ribet.</p>
        </div>
        <div className="max-w-4xl mx-auto grid sm:grid-cols-2 gap-6">
          {[
            { icon: <Receipt className="h-6 w-6 text-amber-600" />, title: "Nota PDF Otomatis", desc: "Pelangganmu terima nota cantik langsung di WhatsApp. Gak perlu printer thermal." },
            { icon: <BarChart3 className="h-6 w-6 text-amber-600" />, title: "Rekap Harian", desc: "Jam 9 malam, NotaKu kirim ringkasan: omset, pengeluaran, profit. Tanpa hitung manual." },
            { icon: <Smartphone className="h-6 w-6 text-amber-600" />, title: "Voice Note", desc: "Malas ketik? Kirim voice note. NotaKu dengar dan catat otomatis." },
            { icon: <CreditCard className="h-6 w-6 text-amber-600" />, title: "KUR-Ready Report", desc: "Setelah 3 bulan, NotaKu siapkan laporan keuangan untuk apply KUR." },
            { icon: <Zap className="h-6 w-6 text-amber-600" />, title: "Zero Install", desc: "Gak perlu download app. WhatsApp-only. HP android biasa juga jalan." },
            { icon: <CheckCircle2 className="h-6 w-6 text-amber-600" />, title: "AI Parser", desc: "Ketik bebas: \"3 nasduk 1 kopi\". NotaKu paham dan catat dengan benar." },
          ].map((f, i) => (
            <Card key={i} className="border-amber-100">
              <CardContent className="flex gap-4 items-start pt-6">
                <div className="p-2 bg-amber-100 rounded-xl shrink-0">{f.icon}</div>
                <div>
                  <h3 className="font-bold text-amber-900 mb-1">{f.title}</h3>
                  <p className="text-sm text-amber-700/60">{f.desc}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Social proof */}
      <section className="px-6 py-16 bg-white">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-amber-950 mb-8">Kenapa NotaKu?</h2>
          <div className="grid sm:grid-cols-3 gap-8 text-center">
            {[
              { number: "30Jt+", label: "UMKM di Indonesia" },
              { number: "87%", label: "Lebih suka WhatsApp" },
              { number: "$235M", label: "Credit gap UMKM" },
            ].map((s, i) => (
              <div key={i}>
                <div className="text-3xl font-bold text-amber-600">{s.number}</div>
                <div className="text-sm text-amber-700/60 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20 bg-amber-900 text-center">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-4">
            Mulai catat usahamu sekarang.
          </h2>
          <p className="text-amber-200/70 mb-8">
            Gratis. Tanpa kartu kredit. Langsung jalan.
          </p>
          <a href={WA_LINK} target="_blank" rel="noopener">
            <Button size="lg" className="bg-green-500 hover:bg-green-600 text-white px-10 py-7 text-xl rounded-2xl shadow-xl">
              <MessageCircle className="mr-2 h-6 w-6" />
              Buka NotaKu di WhatsApp
            </Button>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 text-center text-sm text-amber-700/40">
        <p>© 2026 NotaKu. Dibangun untuk UMKM Indonesia. 🇮🇩</p>
      </footer>
    </div>
  );
}
