import os
import flet as ft
import threading

from prompt import BIENVENIDA
from agente import AgenteRecepcion
from ui import (
    BG, SURFACE, BORDER, USER_BUBBLE, SUBTEXT, WHITE, INPUT_BG, TEXT_DARK,
    build_header, build_input_bar,
    user_bubble, bot_bubble, success_bubble, typing_indicator,
)


def main(page: ft.Page) -> None:
    page.title         = "Recepcion de Producto · Empacadora"
    page.bgcolor       = BG
    page.padding       = 0

    agente = AgenteRecepcion()
    procesando = {"valor": False}

    # ── Chat ──────────────────────────────────────────────────
    chat = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.Padding(16, 20, 16, 16),
        auto_scroll=True,
    )
    chat.controls.append(bot_bubble(BIENVENIDA))

    # ── Input ─────────────────────────────────────────────────
    field = ft.TextField(
        hint_text="Reply ...",
        hint_style=ft.TextStyle(color=SUBTEXT, size=14),
        text_style=ft.TextStyle(color=TEXT_DARK, size=14),
        bgcolor=INPUT_BG,
        border=ft.InputBorder.NONE,
        border_radius=24,
        expand=True,
        min_lines=1,
        max_lines=4,
        shift_enter=True,
        content_padding=ft.Padding(20, 12, 20, 12),
    )

    send_btn = ft.Container(
        content=ft.Text("›", color=WHITE, size=28, weight=ft.FontWeight.BOLD),
        bgcolor=USER_BUBBLE,
        border_radius=24,
        width=48, height=48,
        alignment=ft.alignment.Alignment(0, 0),
        ink=True,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color="#50E8500A", offset=ft.Offset(0, 3),
        ),
        on_click=lambda e: _enviar(),
    )

    def _enviar(_=None) -> None:
        if procesando["valor"]:
            return
        txt = (field.value or "").strip()
        if not txt:
            return

        procesando["valor"] = True
        field.value = ""
        field.disabled = True
        send_btn.bgcolor = "#CCCCCC"
        field.update()
        send_btn.update()

        chat.controls.append(user_bubble(txt))
        typing = typing_indicator()
        chat.controls.append(typing)
        chat.update()

        def fetch() -> None:
            try:
                respuesta, guardado = agente.responder(txt)
            except Exception as e:
                import traceback
                traceback.print_exc()
                respuesta = f"Error inesperado: {type(e).__name__}"
                guardado  = False
            finally:
                procesando["valor"] = False
                field.disabled = False
                send_btn.bgcolor = USER_BUBBLE
                field.update()
                send_btn.update()

            chat.controls.remove(typing)
            if guardado:
                chat.controls.append(success_bubble(respuesta))
            else:
                chat.controls.append(bot_bubble(respuesta))
            chat.update()

        threading.Thread(target=fetch, daemon=True).start()

    field.on_submit = lambda e: _enviar()

    page.add(
        ft.Column([
            build_header(),
            ft.Container(content=chat, expand=True, bgcolor=BG),
            build_input_bar(field, send_btn),
        ], expand=True, spacing=0)
    )


# ── Punto de entrada ──────────────────────────────────────────
# En local corre como escritorio.
# En Render (variable PORT presente) corre como web.
PORT = os.environ.get("PORT")

if PORT:
    # Modo web — Render
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=int(PORT),
        host="0.0.0.0",
    )
else:
    # Modo escritorio — desarrollo local
    ft.app(target=main)
