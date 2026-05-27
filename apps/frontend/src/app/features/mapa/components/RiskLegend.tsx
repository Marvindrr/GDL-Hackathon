export function RiskLegend() {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/90 p-3 shadow-xl">
      <h4 className="mb-2 text-xs font-semibold text-white">
        Riesgo
      </h4>

      <div className="space-y-2 text-xs text-slate-300">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-red-500" />
          Alto
        </div>

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-yellow-500" />
          Medio
        </div>

        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-green-500" />
          Bajo
        </div>
      </div>
    </div>
  );
}