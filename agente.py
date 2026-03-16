import json
import threading
from openai import OpenAI
from dotenv import load_dotenv

from prompt import SYSTEM_PROMPT, CAMPOS, RESUMEN_TEMPLATE

load_dotenv(override=True)
client = OpenAI()

_CONFIRMAR = {"si", "sí", "yes", "correcto", "confirmo", "ok", "adelante", "guardar"}

_EXTRACTOR_PROMPT = (
    "Eres un extractor de datos JSON. Lee la conversacion y devuelve "
    "UNICAMENTE esta linea JSON con los valores encontrados (null si no se menciono):\n"
    '{"productor":null,"producto":null,"variedad":null,"peso_neto":null,"total_cajas":null}\n\n'
    "Reglas absolutas:\n"
    "- Responde SOLO con el JSON en una linea. Cero texto extra.\n"
    "- Sin markdown, sin explicaciones, sin saltos de linea dentro del JSON.\n"
    "- Ejemplos: 'Luis Pacheco'->productor, 'Tomate'->producto, "
    "'Saladette'->variedad, '131 kg'->peso_neto:'131', '80 cajas'->total_cajas:'80'"
)


def _extraer_datos(historial: list[dict]) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _EXTRACTOR_PROMPT},
            *historial[-20:],
        ],
        temperature=0,
        max_tokens=100,
    )
    texto = resp.choices[0].message.content.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    texto = texto.splitlines()[0].strip()
    print(f"[extractor] {texto}")
    try:
        raw = json.loads(texto)
    except json.JSONDecodeError:
        print(f"[extractor] JSON invalido: {texto}")
        return {}
    return {
        k: str(v).strip()
        for k, v in raw.items()
        if k in CAMPOS and v and str(v).strip() not in ("null", "None", "")
    }


class AgenteRecepcion:

    def __init__(self):
        self.historial: list[dict] = []
        self.datos: dict = {}
        self.esperando_confirmacion = False
        self._lock = threading.Lock()

    def _completo(self) -> bool:
        return all(self.datos.get(c) for c in CAMPOS)

    def responder(self, msg: str) -> tuple[str, bool]:
        with self._lock:
            return self._procesar(msg)

    def _procesar(self, msg: str) -> tuple[str, bool]:

        # ── Confirmacion pendiente ────────────────────────────
        if self.esperando_confirmacion:
            if any(p in msg.lower() for p in _CONFIRMAR):
                self.esperando_confirmacion = False

                datos_json = json.dumps(
                    {k: self.datos.get(k) for k in CAMPOS},
                    ensure_ascii=False, indent=2
                )
                return (
                    "Registro recibido correctamente!\n\n"
                    "Datos registrados:\n"
                    f"```json\n{datos_json}\n```\n\n"
                    "Si tienes otra recepcion, dimelo.",
                    True,
                )
            else:
                self.esperando_confirmacion = False
                return "Claro, que dato deseas corregir?", False

        # ── Paso 1: respuesta conversacional ─────────────────
        self.historial.append({"role": "user", "content": msg})

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *self.historial[-16:],
            ],
            temperature=0.1,
            max_tokens=400,
            stream=True,
        )

        respuesta_texto = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                respuesta_texto += delta

        self.historial.append({"role": "assistant", "content": respuesta_texto})

        # ── Paso 2: extraccion ────────────────────────────────
        nuevos = _extraer_datos(self.historial)
        for k, v in nuevos.items():
            self.datos[k] = v

        # ── Completo? → resumen ───────────────────────────────
        if self._completo() and not self.esperando_confirmacion:
            resumen = RESUMEN_TEMPLATE.format(
                **{k: self.datos.get(k, "-") for k in CAMPOS}
            )
            self.esperando_confirmacion = True
            return respuesta_texto + "\n\n" + resumen, False

        return respuesta_texto, False
