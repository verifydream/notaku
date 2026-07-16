"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  TrendingDown,
  Wallet,
  Receipt,
  MessageCircle,
  ExternalLink,
} from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Summary {
  date: string;
  total_sales: number;
  total_expenses: number;
  profit: number;
  transaction_count: number;
}

interface Transaction {
  id: string;
  total: number;
  type: string;
  note: string | null;
  created_at: string;
  items: { id: string; menu_item_name: string; quantity: number; unit_price: number; subtotal: number }[];
}

function fmtRp(n: number) {
  return "Rp " + n.toLocaleString("id-ID");
}

export default function DashboardPage() {
  const [phone, setPhone] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  async function fetchData(p: string) {
    try {
      const [sumRes, txRes] = await Promise.all([
        fetch(`${API}/api/users/${p}/summary`),
        fetch(`${API}/api/users/${p}/transactions`),
      ]);
      if (sumRes.ok) setSummary(await sumRes.json());
      if (txRes.ok) setTransactions(await txRes.json());
      setLoaded(true);
    } catch {
      setLoaded(true);
    }
  }

  // Check URL params for phone
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const p = params.get("phone");
    if (p) {
      setPhone(p);
      fetchData(p);
    }
  }, []);

  if (!phone) {
    return (
      <div className="min-h-screen bg-amber-50 flex items-center justify-center p-6">
        <Card className="w-full max-w-md border-amber-100">
          <CardHeader>
            <CardTitle className="text-amber-900">📒 NotaKu Dashboard</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-amber-700/60 mb-4">
              Masukkan nomor WhatsApp kamu untuk melihat dashboard.
            </p>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const input = (e.target as HTMLFormElement).elements.namedItem("phone") as HTMLInputElement;
                setPhone(input.value);
                fetchData(input.value);
              }}
              className="flex gap-2"
            >
              <input
                name="phone"
                placeholder="081234567890"
                className="flex-1 px-3 py-2 border border-amber-200 rounded-lg text-sm"
              />
              <Button type="submit" className="bg-amber-600 hover:bg-amber-700 text-white">
                Lihat
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-amber-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-amber-900">📒 NotaKu</h1>
            <p className="text-sm text-amber-700/50">Dashboard untuk {phone}</p>
          </div>
          <a
            href={`https://wa.me/62${phone.slice(1)}?text=rekap`}
            target="_blank"
            rel="noopener"
          >
            <Button variant="outline" size="sm" className="border-amber-200 text-amber-700">
              <MessageCircle className="h-4 w-4 mr-1" />
              Buka WhatsApp
            </Button>
          </a>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="border-amber-100">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-amber-600 mb-1">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-xs font-medium">Omset Hari Ini</span>
                </div>
                <div className="text-xl font-bold text-amber-900">{fmtRp(summary.total_sales)}</div>
              </CardContent>
            </Card>
            <Card className="border-amber-100">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-red-500 mb-1">
                  <TrendingDown className="h-4 w-4" />
                  <span className="text-xs font-medium">Pengeluaran</span>
                </div>
                <div className="text-xl font-bold text-amber-900">{fmtRp(summary.total_expenses)}</div>
              </CardContent>
            </Card>
            <Card className="border-amber-100">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-green-600 mb-1">
                  <Wallet className="h-4 w-4" />
                  <span className="text-xs font-medium">Profit</span>
                </div>
                <div className="text-xl font-bold text-amber-900">{fmtRp(summary.profit)}</div>
              </CardContent>
            </Card>
            <Card className="border-amber-100">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-amber-600 mb-1">
                  <Receipt className="h-4 w-4" />
                  <span className="text-xs font-medium">Transaksi</span>
                </div>
                <div className="text-xl font-bold text-amber-900">{summary.transaction_count}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Transactions */}
        <Card className="border-amber-100">
          <CardHeader>
            <CardTitle className="text-amber-900 text-lg">Transaksi Terakhir</CardTitle>
          </CardHeader>
          <CardContent>
            {transactions.length === 0 ? (
              <div className="text-center py-8 text-amber-700/40">
                {loaded ? "Belum ada transaksi. Mulai chat di WhatsApp!" : "Memuat..."}
              </div>
            ) : (
              <div className="space-y-3">
                {transactions.slice(0, 20).map((tx) => (
                  <div
                    key={tx.id}
                    className="flex items-center justify-between p-3 bg-amber-50/50 rounded-lg"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={tx.type === "sale" ? "default" : "destructive"}
                          className={`text-xs ${tx.type === "sale" ? "bg-green-100 text-green-700" : ""}`}
                        >
                          {tx.type === "sale" ? "Penjualan" : "Pengeluaran"}
                        </Badge>
                        <span className="text-xs text-amber-600/50">
                          {new Date(tx.created_at).toLocaleString("id-ID", { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                      {tx.items.length > 0 && (
                        <p className="text-xs text-amber-700/50 mt-1">
                          {tx.items.map((i) => `${i.quantity}x ${i.menu_item_name}`).join(", ")}
                        </p>
                      )}
                    </div>
                    <div className={`font-bold ${tx.type === "sale" ? "text-green-700" : "text-red-600"}`}>
                      {tx.type === "sale" ? "+" : "-"}{fmtRp(tx.total)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
