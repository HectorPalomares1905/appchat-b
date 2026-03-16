# ============================================================
#  ui.py — Diseño ChatFlow naranja. Burbujas ajustadas al ancho
#           de la ventana con expand=True en las columnas.
# ============================================================

import flet as ft
import re

# ── PALETA ───────────────────────────────────────────────────
BG          = "#F0F2F5"
SURFACE     = "#FFFFFF"
USER_BUBBLE = "#E8500A"
BOT_BUBBLE  = "#FFFFFF"
BORDER      = "#E0E0E0"
SUBTEXT     = "#9E9E9E"
WHITE       = "#FFFFFF"
TEXT_DARK   = "#1A1A1A"
TEXT_MED    = "#555555"
INPUT_BG    = "#F0F2F5"
CODE_GREEN  = "#2D6A4F"
SUCCESS_BG  = "#F0FFF4"
SUCCESS_BD  = "#A8D5B5"


def border_all(w, c):
    s = ft.BorderSide(w, c)
    return ft.Border(s, s, s, s)


def limpiar_codigo(texto: str) -> list:
    controles = []
    partes = re.split(r"```(?:\w*\n)?(.*?)```", texto, flags=re.DOTALL)
    for i, parte in enumerate(partes):
        parte = parte.strip()
        if not parte:
            continue
        if i % 2 == 1:
            controles.append(
                ft.Container(
                    content=ft.Text(parte.strip(), color=CODE_GREEN, size=12,
                                    font_family="monospace", selectable=True),
                    bgcolor="#E8F5E9", border_radius=8,
                    padding=ft.Padding(12, 8, 12, 8),
                    margin=ft.Margin(0, 4, 0, 4),
                )
            )
        else:
            controles.append(
                ft.Markdown(
                    parte, selectable=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    md_style_sheet=ft.MarkdownStyleSheet(
                        p_text_style   =ft.TextStyle(color=TEXT_DARK, size=14),
                        h1_text_style  =ft.TextStyle(color=TEXT_DARK, size=17, weight=ft.FontWeight.BOLD),
                        h2_text_style  =ft.TextStyle(color=TEXT_DARK, size=15, weight=ft.FontWeight.BOLD),
                        h3_text_style  =ft.TextStyle(color=TEXT_DARK, size=14, weight=ft.FontWeight.BOLD),
                        a_text_style   =ft.TextStyle(color=USER_BUBBLE),
                        code_text_style=ft.TextStyle(color=CODE_GREEN, size=12),
                    ),
                )
            )
    return controles or [ft.Text(texto, color=TEXT_DARK, size=14, selectable=True)]


# ── BURBUJAS ─────────────────────────────────────────────────
# La clave para que se ajusten al ancho de la ventana:
#   - El Row ocupa todo el ancho (expand=True en el Column padre del ListView)
#   - La columna interior tiene expand=True para llenar el espacio disponible
#   - El Container de la burbuja tiene un max_width relativo (usando expand con límite)

def user_bubble(text: str) -> ft.Container:
    """Burbuja naranja alineada a la derecha, ancho máximo 75% via margin."""
    return ft.Container(
        content=ft.Text(text, color=WHITE, size=14, selectable=True),
        bgcolor=USER_BUBBLE,
        border_radius=ft.BorderRadius(18, 18, 4, 18),
        padding=ft.Padding(14, 10, 14, 10),
        margin=ft.Margin(80, 2, 0, 2),   # margen izquierdo grande = burbuja no llena todo
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color="#40E8500A", offset=ft.Offset(0, 3),
        ),
        alignment=ft.alignment.Alignment(1, 0),
    )


def _avatar() -> ft.Container:
    return ft.Container(
        content=ft.Text("🍅", size=15),
        width=36, height=36,
        bgcolor="#FFE8D6",
        border_radius=18,
        alignment=ft.alignment.Alignment(0, 0),
        margin=ft.Margin(0, 0, 8, 0),
    )


def bot_bubble(texto: str) -> ft.Row:
    """Burbuja blanca con avatar, ocupa el ancho disponible menos margen derecho."""
    return ft.Row(
        controls=[
            _avatar(),
            ft.Column(
                controls=[
                    ft.Text("Asistente", color=TEXT_DARK, size=12,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(
                            limpiar_codigo(texto), spacing=4, tight=True
                        ),
                        bgcolor=BOT_BUBBLE,
                        border_radius=ft.BorderRadius(4, 18, 18, 18),
                        padding=ft.Padding(14, 10, 14, 10),
                        shadow=ft.BoxShadow(
                            blur_radius=6, spread_radius=0,
                            color="#18000000", offset=ft.Offset(0, 2),
                        ),
                    ),
                ],
                spacing=4,
                expand=True,                          # ← ocupa el ancho restante
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(width=40),                   # margen derecho
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def success_bubble(texto: str) -> ft.Row:
    return ft.Row(
        controls=[
            _avatar(),
            ft.Column(
                controls=[
                    ft.Text("Asistente", color=TEXT_DARK, size=12,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column(
                            limpiar_codigo(texto), spacing=4, tight=True
                        ),
                        bgcolor=SUCCESS_BG,
                        border=border_all(1, SUCCESS_BD),
                        border_radius=ft.BorderRadius(4, 18, 18, 18),
                        padding=ft.Padding(14, 10, 14, 10),
                        shadow=ft.BoxShadow(
                            blur_radius=6, spread_radius=0,
                            color="#18000000", offset=ft.Offset(0, 2),
                        ),
                    ),
                ],
                spacing=4,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def typing_indicator() -> ft.Row:
    return ft.Row(
        controls=[
            _avatar(),
            ft.Column(
                controls=[
                    ft.Text("Asistente", color=TEXT_DARK, size=12,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Row([
                            ft.Container(width=9, height=9, bgcolor="#CCCCCC", border_radius=5),
                            ft.Container(width=9, height=9, bgcolor="#BBBBBB", border_radius=5, opacity=0.7),
                            ft.Container(width=9, height=9, bgcolor="#AAAAAA", border_radius=5, opacity=0.4),
                        ], spacing=6),
                        bgcolor=BOT_BUBBLE,
                        border_radius=ft.BorderRadius(4, 18, 18, 18),
                        padding=ft.Padding(14, 12, 14, 12),
                        shadow=ft.BoxShadow(
                            blur_radius=6, spread_radius=0,
                            color="#18000000", offset=ft.Offset(0, 2),
                        ),
                    ),
                ],
                spacing=4,
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


# ── HEADER ───────────────────────────────────────────────────

def build_header() -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Text("E", color=USER_BUBBLE, size=22,
                                    weight=ft.FontWeight.BOLD),
                    width=54, height=54,
                    bgcolor=WHITE,
                    border_radius=27,
                    alignment=ft.alignment.Alignment(0, 0),
                    shadow=ft.BoxShadow(blur_radius=10, color="#30000000",
                                        offset=ft.Offset(0, 3)),
                ),
            ]),
            ft.Container(height=10),
            ft.Text("Recepción de Producto", color=WHITE, size=24,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=4),
            ft.Text("Registra tu entrega en 5 preguntas rápidas.",
                    color="#FFE0CC", size=13),
        ], spacing=0),
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1, -1),
            end=ft.alignment.Alignment(1, 1),
            colors=["#C0390A", "#E8500A", "#FF7B3A", "#FF9A6C", "#E8609A"],
        ),
        padding=ft.Padding(24, 30, 24, 26),
        border_radius=ft.BorderRadius(0, 0, 24, 24),
        shadow=ft.BoxShadow(blur_radius=16, spread_radius=0,
                             color="#30E8500A", offset=ft.Offset(0, 6)),
    )


# ── INPUT BAR ─────────────────────────────────────────────────

def build_input_bar(field, send_btn) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [field, send_btn],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=SURFACE,
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
        padding=ft.Padding(14, 12, 14, 12),
        shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                             color="#12000000", offset=ft.Offset(0, -3)),
    )
