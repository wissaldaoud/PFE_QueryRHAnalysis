"use client";

import { useState } from "react";
import {
  Search, Download, History, FileText, Code,
  Brain, Zap, Database, Shield, TrendingUp, Users,
  BarChart2, Clock, ChevronRight, Send, Sparkles, Activity
} from "lucide-react";
import MainLayout from "@/components/MainLayout";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LabelList, LineChart, Line, Area, AreaChart
} from "recharts";

interface QueryResult {
  success: boolean;
  answer: string;
  query_type: string;
  data?: any;
  sql_query?: string;
  visualization?: {
    type: string;
    data?: any[];
    value?: number;
    label?: string;
    x?: string;
    y?: string;
  };
  error?: string;
}

// ── Palette Sopra HR officielle ─────────────────────────────────────
const S = {
  bg:       "#F4F5F7",
  white:    "#FFFFFF",
  dark:     "#1A1333",
  purple1:  "#5B2D8E",
  purple2:  "#7B3FA8",
  violet:   "#A855C8",
  rose:     "#C2185B",
  gradH:    "linear-gradient(135deg, #2D1B5E 0%, #5B2D8E 35%, #8B3AAF 65%, #B5468C 85%, #C2185B 100%)",
  gradBtn:  "linear-gradient(135deg, #6B2FA0 0%, #9B3DBF 50%, #C2185B 100%)",
  gradCard: "linear-gradient(145deg, #3D1A6E 0%, #6B2FA0 100%)",
  border:   "rgba(91,45,142,0.15)",
  shadow:   "0 4px 24px rgba(91,45,142,0.10)",
  text:     "#1A1333",
  textSub:  "#5B2D8E",
  textMut:  "#8B7BAA",
};

export default function QueryEnginePage() {
  const [query, setQuery]               = useState("");
  const [loading, setLoading]           = useState(false);
  const [loadingStep, setLoadingStep]   = useState("");
  const [result, setResult]             = useState<QueryResult | null>(null);
  const [showSQL, setShowSQL]           = useState(false);
  const [queryHistory, setQueryHistory] = useState<any[]>([]);
  const [activeQuick, setActiveQuick]   = useState<number | null>(null);

  const executeQuery = async () => {
    if (!query.trim()) return;
    setLoading(true); setResult(null); setShowSQL(false);
    setLoadingStep("Analyse sémantique NLP en cours…");
    const t1 = setTimeout(() => setLoadingStep("Détection intent & entités RH…"), 1400);
    const t2 = setTimeout(() => setLoadingStep("Génération SQL & exécution DWH…"), 2800);
    try {
      const token = localStorage.getItem("access_token");
      if (!token) { window.location.href = "/login"; return; }
      const res = await fetch("http://localhost:8000/api/v1/query/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) {
        if (res.status === 401) { localStorage.removeItem("access_token"); window.location.href = "/login"; return; }
        throw new Error(`Erreur ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
      setQueryHistory(p => [{ query, timestamp: new Date().toLocaleTimeString(), success: data.success }, ...p.slice(0, 9)]);
    } catch (e: any) {
      setResult({ success: false, answer: "Erreur de connexion au serveur.", query_type: "error", error: e.message });
    } finally {
      clearTimeout(t1); clearTimeout(t2);
      setLoading(false); setLoadingStep("");
    }
  };

  const exportData = async (format: string) => {
    if (!query.trim()) return;
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      const res = await fetch("http://localhost:8000/api/v1/query/execute/export", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query, export_format: format }),
      });
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `export.${format}`;
      document.body.appendChild(a); a.click();
      URL.revokeObjectURL(url); document.body.removeChild(a);
    } catch {}
  };

  const quickQueries = [
    { icon: Users,      text: "Combien d'employés actifs ?",        cat: "Effectif"    },
    { icon: BarChart2,  text: "Répartition des employés par sexe",  cat: "Statistique" },
    { icon: TrendingUp, text: "Évolution des embauches par année",  cat: "Tendance"    },
    { icon: Activity,   text: "Taux de turnover",                   cat: "Turnover"    },
    { icon: Clock,      text: "Qui est absent aujourd'hui ?",        cat: "Absences"    },
    { icon: Search,     text: "Top 10 employés les plus anciens",   cat: "Ancienneté"  },
  ];

  const renderAnswer = (text: string) => ({
    __html: text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
  });

  return (
    <MainLayout>
      <div style={{ minHeight:"100vh", background: S.bg, fontFamily:"'Outfit','Segoe UI',sans-serif" }}>

        {/* ══ HEADER ══════════════════════════════════════════════════════ */}
        <header style={{ background: S.gradH, position:"relative", overflow:"hidden" }}>
          <div style={{ position:"absolute", inset:0, opacity:0.035,
            backgroundImage:`url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
            backgroundSize:"160px" }} />
         
          <div style={{ maxWidth:"1360px", margin:"0 auto", padding:"42px 36px 38px", position:"relative", zIndex:1 }}>
            <div style={{ display:"flex", alignItems:"center", gap:"18px", marginBottom:"26px" }}>
              <div style={{ width:"54px", height:"54px", borderRadius:"15px",
                background:"rgba(255,255,255,0.13)", backdropFilter:"blur(8px)",
                border:"1px solid rgba(255,255,255,0.22)",
                display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
              
              </div>
              <div>
                <p style={{ color:"rgba(255,255,255,0.5)", fontSize:"10.5px", letterSpacing:"3px",
                  textTransform:"uppercase", fontWeight:600, margin:"0 0 4px 0" }}>
                  Sopra HR · Analytics Platform
                </p>
                <h1 style={{ color:"#fff", fontSize:"26px", fontWeight:700, margin:0, letterSpacing:"-0.3px" }}>
                  Moteur de Requêtes RH
                </h1>
                <p style={{ color:"rgba(255,255,255,0.58)", fontSize:"13px", margin:"5px 0 0 0" }}>
                  Interrogez vos données en langage naturel — NLP sémantique multilingue
                </p>
              </div>
            </div>

            <div style={{ display:"flex", gap:"8px", flexWrap:"wrap" }}>
              {[
          
             
               
                
               
              ].map(({ icon: Icon, label }, i) => (
                <div key={i} style={{ display:"flex", alignItems:"center", gap:"6px",
                  background:"rgba(255,255,255,0.1)", backdropFilter:"blur(6px)",
                  border:"1px solid rgba(255,255,255,0.18)", borderRadius:"20px",
                  padding:"5px 13px", color:"rgba(255,255,255,0.82)", fontSize:"11.5px", fontWeight:500 }}>
                  
                  {label}
                </div>
              ))}
            </div>
          </div>
        </header>

        {/* ══ BODY ════════════════════════════════════════════════════════ */}
        <main style={{ maxWidth:"1360px", margin:"0 auto", padding:"32px 36px",
          display:"grid", gridTemplateColumns:"1fr 300px", gap:"24px" }}>

          {/* ── COLONNE GAUCHE ─────────────────────────────────────────── */}
          <div style={{ display:"flex", flexDirection:"column", gap:"20px" }}>

            {/* Saisie */}
            <div style={{ background: S.white, borderRadius:"18px", padding:"28px", boxShadow: S.shadow, border:`1px solid ${S.border}` }}>
              <label style={{ color: S.textMut, fontSize:"10.5px", fontWeight:700,
                letterSpacing:"2px", textTransform:"uppercase", display:"block", marginBottom:"10px" }}>
                Votre question
              </label>

              <textarea
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && e.ctrlKey) executeQuery(); }}
                placeholder="Ex : Combien d'employés actifs ?  ·  Répartition par sexe  ·  Évolution des embauches par année…"
                rows={4}
                style={{ width:"100%", boxSizing:"border-box", padding:"14px 18px",
                  background:"#FAFAFA", border:`1.5px solid ${S.border}`, borderRadius:"12px",
                  color: S.text, fontSize:"14px", lineHeight:1.65,
                  outline:"none", resize:"none",
                  fontFamily:"'Outfit','Segoe UI',sans-serif",
                  transition:"border-color 0.2s, box-shadow 0.2s",
                }}
                onFocus={e => { e.target.style.borderColor = S.purple1; e.target.style.boxShadow = `0 0 0 3px rgba(91,45,142,0.08)`; e.target.style.background = "#fff"; }}
                onBlur={e  => { e.target.style.borderColor = S.border;  e.target.style.boxShadow = "none"; e.target.style.background = "#FAFAFA"; }}
              />

              <div style={{ display:"flex", justifyContent:"space-between", marginTop:"6px", marginBottom:"14px" }}>
                <span style={{ color: S.textMut, fontSize:"11px" }}>Ctrl + Entrée pour exécuter</span>
                <span style={{ color: S.textMut, fontSize:"11px" }}>{query.length} car.</span>
              </div>

              <div style={{ display:"flex", gap:"10px" }}>
                <button onClick={executeQuery} disabled={loading || !query.trim()}
                  style={{ flex:1, padding:"13px 22px",
                    background: loading || !query.trim() ? "#E8DEFA" : S.gradBtn,
                    border:"none", borderRadius:"12px", color: loading || !query.trim() ? "#A080C8" : "#fff",
                    fontWeight:700, fontSize:"14px",
                    cursor: loading || !query.trim() ? "not-allowed" : "pointer",
                    display:"flex", alignItems:"center", justifyContent:"center", gap:"9px",
                    boxShadow: loading || !query.trim() ? "none" : "0 4px 20px rgba(107,47,160,0.38)",
                    transition:"all 0.2s", fontFamily:"inherit" }}>
                  {loading
                    ? <>
                        <div style={{ width:"15px", height:"15px", border:"2px solid rgba(160,128,200,0.4)", borderTop:"2px solid #A080C8", borderRadius:"50%", animation:"spin .7s linear infinite" }} />
                        <span style={{ fontSize:"12px" }}>{loadingStep}</span>
                      </>
                    : <><Send style={{ width:"15px", height:"15px" }} />Analyser la requête</>
                  }
                </button>

                {[{ label:"CSV", fmt:"csv", icon: Download }, { label:"Excel", fmt:"excel", icon: FileText }].map(({ label, fmt, icon: Icon }) => (
                  <button key={fmt} onClick={() => exportData(fmt)}
                    style={{ padding:"13px 18px", background:"#fff",
                      border:`1.5px solid ${S.border}`, borderRadius:"12px",
                      color: S.textSub, fontWeight:600, fontSize:"13px",
                      cursor:"pointer", display:"flex", alignItems:"center", gap:"7px",
                      transition:"all 0.2s", fontFamily:"inherit" }}
                    onMouseEnter={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor = S.purple1; el.style.background = "#F9F3FF"; }}
                    onMouseLeave={e => { const el = e.currentTarget as HTMLElement; el.style.borderColor = S.border; el.style.background = "#fff"; }}
                  >
                    <Icon style={{ width:"14px", height:"14px" }} />{label}
                  </button>
                ))}
              </div>

              {loading && (
                <div style={{ marginTop:"14px", padding:"12px 16px",
                  background:"linear-gradient(135deg,#F6EFFE,#FDF0F7)",
                  border:`1px solid rgba(91,45,142,0.18)`, borderRadius:"10px",
                  display:"flex", alignItems:"center", gap:"12px" }}>
                  <div style={{ display:"flex", gap:"4px" }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{ width:"5px", height:"5px", borderRadius:"50%",
                        background: S.purple2, animation:`bounce .9s ease-in-out ${i*0.15}s infinite` }} />
                    ))}
                  </div>
                  <span style={{ color: S.textSub, fontSize:"12px", fontWeight:500 }}>{loadingStep}</span>
                </div>
              )}
            </div>

            {/* Résultats */}
            {result && (
              <div style={{ background: S.white, borderRadius:"18px", padding:"28px",
                boxShadow: S.shadow, border:`1.5px solid ${result.success ? S.border : "rgba(194,24,91,0.22)"}` }}>

                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"18px" }}>
                  <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
                    <div style={{ width:"8px", height:"8px", borderRadius:"50%",
                      background: result.success ? "#22C55E" : "#EF4444",
                      boxShadow: result.success ? "0 0 8px rgba(34,197,94,0.5)" : "0 0 8px rgba(239,68,68,0.5)" }} />
                    <h2 style={{ color: S.text, fontSize:"16px", fontWeight:700, margin:0 }}>Résultats</h2>
                  </div>
                  {result.sql_query && (
                    <button onClick={() => setShowSQL(!showSQL)}
                      style={{ color: S.textSub, fontSize:"12px", fontWeight:600,
                        background:"#F6EFFE", border:`1px solid rgba(91,45,142,0.18)`,
                        borderRadius:"8px", padding:"5px 12px", cursor:"pointer",
                        display:"flex", alignItems:"center", gap:"5px", fontFamily:"inherit" }}>
                      <Code style={{ width:"12px", height:"12px" }} />
                      {showSQL ? "Masquer" : "Voir"} SQL
                    </button>
                  )}
                </div>

                {showSQL && result.sql_query && (
                  <div style={{ background:"#1A1333", borderRadius:"10px", padding:"16px", marginBottom:"16px", overflowX:"auto" }}>
                    <pre style={{ color:"#C084FC", fontSize:"11.5px",
                      fontFamily:"'JetBrains Mono','Fira Code',monospace", margin:0, lineHeight:1.65 }}>
                      {result.sql_query}
                    </pre>
                  </div>
                )}

                <div style={{ padding:"14px 18px", borderRadius:"12px", marginBottom:"22px",
                  background: result.success ? "linear-gradient(135deg,#F9F3FF,#FDF0F7)" : "#FEF2F2",
                  borderLeft:`4px solid ${result.success ? S.purple1 : "#EF4444"}`,
                  border:`1px solid ${result.success ? "rgba(91,45,142,0.12)" : "rgba(239,68,68,0.18)"}` }}>
                  <p style={{ color: result.success ? S.text : "#B91C1C",
                    fontSize:"14px", fontWeight:500, margin:0, lineHeight:1.65 }}
                    dangerouslySetInnerHTML={renderAnswer(result.answer)} />
                </div>

                {/* Visualisations */}
                {result.visualization && result.data && (() => {
                  const viz = result.visualization!;

                  if (viz.type === "metric") return (
                    <div style={{ display:"flex", alignItems:"center", justifyContent:"center",
                      padding:"52px 24px", background: S.gradH, borderRadius:"16px" }}>
                      <div style={{ textAlign:"center" }}>
                        <div style={{ fontSize:"76px", fontWeight:800, color:"#fff", lineHeight:1,
                          textShadow:"0 4px 20px rgba(194,24,91,0.4)" }}>
                          {Number(viz.value)?.toLocaleString()}
                        </div>
                        <div style={{ color:"rgba(255,255,255,0.6)", fontSize:"12px", marginTop:"12px",
                          fontWeight:600, letterSpacing:"2.5px", textTransform:"uppercase" }}>
                          {viz.label}
                        </div>
                      </div>
                    </div>
                  );

                  if (viz.type === "table" && viz.data) return (
                    <div style={{ overflowX:"auto", borderRadius:"12px", border:`1px solid ${S.border}` }}>
                      <table style={{ width:"100%", borderCollapse:"collapse" }}>
                        <thead>
                          <tr style={{ background:"linear-gradient(135deg,#F6EFFE,#FDF0F7)" }}>
                            {Object.keys(viz.data[0] || {}).map(k => (
                              <th key={k} style={{ padding:"11px 16px", textAlign:"left",
                                color: S.textSub, fontSize:"10.5px", fontWeight:700,
                                letterSpacing:"1.5px", textTransform:"uppercase",
                                borderBottom:`2px solid rgba(91,45,142,0.1)` }}>{k}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {viz.data.slice(0,50).map((row:any, i:number) => (
                            <tr key={i}
                              style={{ background: i%2===0 ? "#FAFAFA" : "#fff", transition:"background .15s" }}
                              onMouseEnter={e => (e.currentTarget.style.background="#F9F3FF")}
                              onMouseLeave={e => (e.currentTarget.style.background = i%2===0 ? "#FAFAFA" : "#fff")}
                            >
                              {Object.values(row).map((v:any, j:number) => (
                                <td key={j} style={{ padding:"10px 16px", color: S.text,
                                  fontSize:"13px", borderBottom:`1px solid rgba(91,45,142,0.05)` }}>
                                  {typeof v==="number" ? v.toLocaleString() : String(v ?? "—")}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {viz.data.length > 50 && (
                        <div style={{ textAlign:"center", padding:"10px", color: S.textMut, fontSize:"11px" }}>
                          50 / {viz.data.length} lignes affichées
                        </div>
                      )}
                    </div>
                  );

                  if (viz.type === "bar_chart" && viz.data) {
                    const xKey = viz.x || Object.keys(viz.data[0])[0];
                    const yKey = viz.y || Object.keys(viz.data[0])[1];
                    const colors = ["#5B2D8E","#7B3FA8","#9B4FC8","#B5468C","#C2185B","#8B3AAF"];
                    return (
                      <div style={{ background:"#FAFAFA", borderRadius:"14px", padding:"22px", height:"380px" }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={viz.data} margin={{ top:20, right:16, bottom:65, left:10 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(91,45,142,0.07)" vertical={false} />
                            <XAxis dataKey={xKey} angle={-35} textAnchor="end" height={75}
                              tick={{ fill: S.textMut, fontSize:11, fontFamily:"inherit" }}
                              axisLine={{ stroke:"rgba(91,45,142,0.12)" }} tickLine={false} />
                            <YAxis tick={{ fill: S.textMut, fontSize:11 }} axisLine={false} tickLine={false}
                              tickFormatter={v => v.toLocaleString()} />
                            <Tooltip contentStyle={{ background:"#fff", border:`1px solid ${S.border}`,
                              borderRadius:"10px", fontSize:"13px", fontFamily:"inherit", boxShadow: S.shadow }}
                              cursor={{ fill:"rgba(91,45,142,0.04)" }} />
                            <Bar dataKey={yKey} radius={[7,7,0,0]}>
                              <LabelList dataKey={yKey} position="top"
                                style={{ fill: S.textSub, fontSize:"11px", fontWeight:600 }} />
                              {viz.data.map((_:any, i:number) => (
                                <Cell key={i} fill={colors[i % colors.length]} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  }

                  if (viz.type === "line_chart" && viz.data) {
                    const xKey = viz.x || Object.keys(viz.data[0])[0];
                    const yKey = viz.y || Object.keys(viz.data[0])[1];
                    return (
                      <div style={{ background:"#FAFAFA", borderRadius:"14px", padding:"22px", height:"360px" }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={viz.data} margin={{ top:20, right:16, bottom:30, left:10 }}>
                            <defs>
                              <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%"  stopColor={S.purple1} stopOpacity={0.18}/>
                                <stop offset="95%" stopColor={S.purple1} stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(91,45,142,0.07)" vertical={false} />
                            <XAxis dataKey={xKey} tick={{ fill: S.textMut, fontSize:11 }}
                              axisLine={{ stroke:"rgba(91,45,142,0.12)" }} tickLine={false} />
                            <YAxis tick={{ fill: S.textMut, fontSize:11 }} axisLine={false} tickLine={false} />
                            <Tooltip contentStyle={{ background:"#fff", border:`1px solid ${S.border}`,
                              borderRadius:"10px", fontSize:"13px", boxShadow: S.shadow }} />
                            <Area type="monotone" dataKey={yKey}
                              stroke={S.purple1} strokeWidth={2.5} fill="url(#areaGrad)"
                              dot={{ fill: S.purple1, r:4, strokeWidth:2, stroke:"#fff" }}
                              activeDot={{ r:6, fill: S.rose, stroke:"#fff", strokeWidth:2 }} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    );
                  }

                  if (viz.type === "pie_chart" && viz.data) {
                    const keys = Object.keys(viz.data[0] || {});
                    const colors = [S.purple1, S.violet, S.rose, "#9B59B6", "#D63B82"];
                    return (
                      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill,minmax(145px,1fr))", gap:"10px" }}>
                        {viz.data.map((item:any, i:number) => (
                          <div key={i} style={{ background:"#FAFAFA", border:`1.5px solid ${S.border}`,
                            borderRadius:"12px", padding:"16px", borderTop:`3px solid ${colors[i%colors.length]}` }}>
                            <p style={{ color: S.textMut, fontSize:"10.5px", margin:"0 0 6px 0",
                              fontWeight:600, letterSpacing:"1px", textTransform:"uppercase" }}>
                              {item[keys[0]] ?? "—"}
                            </p>
                            <p style={{ color: S.text, fontSize:"24px", fontWeight:700, margin:0 }}>
                              {typeof item[keys[1]]==="number" ? item[keys[1]].toLocaleString() : item[keys[1]] ?? "—"}
                            </p>
                          </div>
                        ))}
                      </div>
                    );
                  }
                  return null;
                })()}
              </div>
            )}
          </div>

          {/* ── SIDEBAR DROITE ──────────────────────────────────────────── */}
          <aside style={{ display:"flex", flexDirection:"column", gap:"18px" }}>

            {/* Requêtes rapides */}
            <div style={{ background: S.white, borderRadius:"18px", padding:"22px", boxShadow: S.shadow, border:`1px solid ${S.border}` }}>
              <h3 style={{ color: S.text, fontSize:"13px", fontWeight:700,
                margin:"0 0 14px 0", display:"flex", alignItems:"center", gap:"7px" }}>
                <Sparkles style={{ width:"14px", height:"14px", color: S.purple2 }} />
                Requêtes suggérées
              </h3>
              <div style={{ display:"flex", flexDirection:"column", gap:"5px" }}>
                {quickQueries.map(({ icon: Icon, text, cat }, i) => (
                  <button key={i} onClick={() => { setQuery(text); setActiveQuick(i); }}
                    style={{ textAlign:"left", padding:"10px 12px",
                      background: activeQuick===i ? "#F6EFFE" : "#FAFAFA",
                      border:`1.5px solid ${activeQuick===i ? S.purple1 : "rgba(91,45,142,0.1)"}`,
                      borderRadius:"10px", cursor:"pointer",
                      display:"flex", alignItems:"center", gap:"10px",
                      transition:"all 0.15s", fontFamily:"inherit" }}
                    onMouseEnter={e => { const el = e.currentTarget as HTMLElement; if(activeQuick!==i){ el.style.background="#F9F3FF"; el.style.borderColor="rgba(91,45,142,0.22)"; } }}
                    onMouseLeave={e => { const el = e.currentTarget as HTMLElement; if(activeQuick!==i){ el.style.background="#FAFAFA"; el.style.borderColor="rgba(91,45,142,0.1)"; } }}
                  >
                    <div style={{ width:"30px", height:"30px", flexShrink:0,
                      background: activeQuick===i ? S.purple1 : "rgba(91,45,142,0.08)",
                      borderRadius:"8px", display:"flex", alignItems:"center", justifyContent:"center" }}>
                      <Icon style={{ width:"13px", height:"13px", color: activeQuick===i ? "#fff" : S.purple2 }} />
                    </div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <p style={{ color: S.text, fontSize:"12px", fontWeight:500, margin:0,
                        overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{text}</p>
                      <p style={{ color: S.textMut, fontSize:"10px", margin:"2px 0 0 0" }}>{cat}</p>
                    </div>
                    <ChevronRight style={{ width:"12px", height:"12px", color: S.textMut, flexShrink:0 }} />
                  </button>
                ))}
              </div>
            </div>

            {/* Historique */}
            {queryHistory.length > 0 && (
              <div style={{ background: S.white, borderRadius:"18px", padding:"22px", boxShadow: S.shadow, border:`1px solid ${S.border}` }}>
                <h3 style={{ color: S.text, fontSize:"13px", fontWeight:700,
                  margin:"0 0 14px 0", display:"flex", alignItems:"center", gap:"7px" }}>
                  <History style={{ width:"14px", height:"14px", color: S.purple2 }} />
                  Historique récent
                </h3>
                <div style={{ display:"flex", flexDirection:"column", gap:"5px", maxHeight:"200px", overflowY:"auto" }}>
                  {queryHistory.map((h, i) => (
                    <button key={i} onClick={() => setQuery(h.query)}
                      style={{ textAlign:"left", padding:"9px 12px", background:"#FAFAFA",
                        border:`1px solid rgba(91,45,142,0.08)`, borderRadius:"9px",
                        cursor:"pointer", transition:"background .15s", fontFamily:"inherit" }}
                      onMouseEnter={e => (e.currentTarget.style.background="#F9F3FF")}
                      onMouseLeave={e => (e.currentTarget.style.background="#FAFAFA")}
                    >
                      <div style={{ display:"flex", alignItems:"center", gap:"7px" }}>
                        <div style={{ width:"6px", height:"6px", borderRadius:"50%", flexShrink:0,
                          background: h.success ? "#22C55E" : "#EF4444" }} />
                        <p style={{ color: S.text, fontSize:"11.5px", margin:0,
                          overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{h.query}</p>
                      </div>
                      <p style={{ color: S.textMut, fontSize:"10px", margin:"2px 0 0 18px" }}>{h.timestamp}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

          
           

          </aside>
        </main>

        <style>{`
          @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');
          @keyframes spin   { to { transform: rotate(360deg); } }
          @keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
          textarea::placeholder { color: #C4B8D8; font-size: 13px; }
          ::-webkit-scrollbar       { width: 4px; }
          ::-webkit-scrollbar-track { background: #F4F5F7; }
          ::-webkit-scrollbar-thumb { background: rgba(91,45,142,0.25); border-radius: 4px; }
        `}</style>
      </div>
    </MainLayout>
  );
}