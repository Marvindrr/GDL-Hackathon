type Props = {
  instrucciones: string[];
  destino?: string;
  loading?: boolean;
};

export function EscapeRouteInstructionsPanel({
  instrucciones,
  destino,
  loading = false,
}: Props) {
  return (
    <div className="h-full border-l border-slate-800 bg-slate-950/95 p-4">
      <h3 className="text-sm font-bold text-white">
        Ruta de escape
      </h3>

      <p className="mt-1 text-xs text-slate-500">
        Instrucciones fuera del mapa para mejor lectura.
      </p>

      {loading ? (
        <div className="mt-5 rounded-lg border border-orange-500/30 bg-orange-500/10 p-3 text-sm text-orange-200">
          Calculando ruta segura...
        </div>
      ) : instrucciones.length === 0 ? (
        <div className="mt-5 rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-slate-400">
          Selecciona una zona, cámara o presiona calcular ruta para generar instrucciones.
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          {destino && (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3">
              <p className="text-xs text-emerald-300">Destino recomendado</p>
              <p className="text-sm font-semibold text-white">{destino}</p>
            </div>
          )}

          <ol className="space-y-2">
            {instrucciones.map((instruccion, index) => (
              <li
                key={`${instruccion}-${index}`}
                className="flex gap-2 rounded-lg border border-slate-800 bg-slate-900 p-3 text-sm text-slate-300"
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-orange-600 text-xs font-bold text-white">
                  {index + 1}
                </span>

                <span>{instruccion}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}