/** Tablero (§8): KPIs, líneas y kanban, con refresco por polling (60 s). */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";
import type { Lineas } from "../api/tipos";
import { Cargando, ChipEtapa, Kpi } from "../componentes/ui";
import { useI18n } from "../estado/i18n";

interface Resumen { en_cola: number; en_proceso: number;
                    esperando_aprobacion: number; en_produccion_30d: number; }
interface Kanban { columnas: Record<string, { id: string; titulo: string; tipo: string;
                   prioridad: string; gate_pendiente: number | null }[]>; }

const COLS = ["triage", "design", "build", "qa", "security", "deploy"];

export default function Tablero() {
  const { t } = useI18n();
  const nav = useNavigate();
  const [resumen, setResumen] = useState<Resumen | null>(null);
  const [lineas, setLineas] = useState<Lineas | null>(null);
  const [kanban, setKanban] = useState<Kanban | null>(null);

  useEffect(() => {
    let vivo = true;
    async function cargar() {
      try {
        const [r, l, k] = await Promise.all([
          api.get<Resumen>("/api/v1/dashboard/summary"),
          api.get<Lineas>("/api/v1/dashboard/lines"),
          api.get<Kanban>("/api/v1/dashboard/kanban"),
        ]);
        if (vivo) { setResumen(r); setLineas(l); setKanban(k); }
      } catch { /* polling silencioso */ }
    }
    cargar();
    const timer = setInterval(cargar, 60_000);
    return () => { vivo = false; clearInterval(timer); };
  }, []);

  if (!resumen || !lineas || !kanban) return <Cargando />;

  return (
    <div className="view">
      <div className="view-head">
        <div><h1>{t("dash.title")}</h1><p>{t("dash.sub")}</p></div>
        <div className="spacer" />
        <button className="btn primary" onClick={() => nav("/nuevo-ticket")}>
          + {t("nav.newticket")}
        </button>
      </div>

      <div className="grid4" style={{ marginBottom: 16 }}>
        <Kpi lbl={t("dash.k1")} num={resumen.en_cola} />
        <Kpi lbl={t("dash.k2")} num={resumen.en_proceso} />
        <Kpi lbl={t("dash.k3")} num={resumen.esperando_aprobacion} color="gate" />
        <Kpi lbl={t("dash.k4")} num={resumen.en_produccion_30d} color="ok" />
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <label>{t("dash.lines")}</label>
        <table className="kc" style={{ marginTop: 6 }}>
          <tbody>
            {lineas.lineas.map((l) => (
              <tr key={l.numero} className={l.ticket_id ? "click" : ""}
                  onClick={() => l.ticket_id && nav(`/tickets/${l.ticket_id}`)}>
                <td><b>{t("dash.line")}</b> {l.numero}</td>
                <td>{l.ticket_id ?? "—"}</td>
                <td>{l.etapa ? <ChipEtapa etapa={l.etapa} /> :
                     <span className="chip"><span className="dot" />{t("dash.idle")}</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <label>{t("dash.kanban")}</label>
        <div className="kanban" style={{ marginTop: 10 }}>
          {COLS.map((col) => (
            <div className="kcol" key={col}>
              <h4><span>{t(`st.${col}`)}</span>
                  <span>{kanban.columnas[col]?.length ?? 0}</span></h4>
              {(kanban.columnas[col] ?? []).map((tk) => (
                <div key={tk.id} className={`kcard ${tk.gate_pendiente ? "gatewait" : ""}`}
                     onClick={() => nav(`/tickets/${tk.id}`)}>
                  <span className="kid">{tk.id}</span><br />{tk.titulo}
                  {tk.gate_pendiente &&
                    <><br /><span className="gtag">⛨ Gate {tk.gate_pendiente}</span></>}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
