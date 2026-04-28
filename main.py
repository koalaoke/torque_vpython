from math import radians

from vpython import *

running = False
dt = 0.01

scene = canvas(background=color.white, width=800, height=500)

wire_width = shapes.circle(radius=0.2)
rectpath = paths.rectangle(width=10, height=10)
ring = extrusion(shape=wire_width, path=rectpath, color=color.yellow)

ring.area = 10 * 10
ring.current = 0
ring.mm_dipolar = ring.up * ring.area * ring.current
ring.n_espiras = 1
ring.velocity = 0
ring.border = vec(0, 10, 0)

curve(pos=[vec(0, 0, -5), vec(0, 0, 5)], color=color.cyan)

seta_borda = attach_arrow(ring, "border", color=color.red, scale=0.1, shaftwidth=0.15)
seta_borda.visible = False
seta_mm_dipolar = attach_arrow(
    ring, "mm_dipolar", color=color.green, scale=0.005, shaftwidth=0.15
)
seta_campo = arrow(axis=vec(0, 0, 0), color=color.blue, opacity=0.4, shaftwidth=0.15)

seta_forca_dir = arrow(color=color.orange, shaftwidth=0.15)
seta_forca_esq = arrow(color=color.orange, shaftwidth=0.15)
seta_forca_dir.visible = False
seta_forca_esq.visible = False


def mudar_campo(evt):
    field_t.text = f" {field.value:1.2f} T"
    seta_campo.axis = vec(field.value, 0, 0)


def mudar_angulo_inicial(evt):
    """Ajusta a orientação da espira antes de começar"""
    angle_rad = radians(angle_slider.value)
    ring.up = vec(0, 1, 0).rotate(angle=angle_rad, axis=vec(0, 0, 1))
    ring.border = vec(0, 10, 0).rotate(angle=angle_rad, axis=vec(0, 0, 1))

    ring.mm_dipolar = ring.up * ring.area * ring.current
    angle_t.text = f" {angle_slider.value:1.0f}°"
    ring.velocity = 0


def mudar_espira(evt):
    global ring
    match evt.id:
        case "height":
            ring.size.x = height_rectangle.value
            height_t.text = f" {height_rectangle.value:1.2f} m"
        case "width":
            ring.size.z = width_rectangle.value
            ring.border = width_rectangle.value * ring.border.hat
            width_t.text = f" {width_rectangle.value:1.2f} m"
        case "mass":
            massa_t.text = f" {massa_rectangle.value:1.2f} g"
        case "current":
            ring.current = current.value
            current_t.text = f" {current.value:1.2f} A"
        case "espiras":
            ring.n_espiras = espiras_slider.value
            espiras_t.text = f" {espiras_slider.value:1.0f}"

    ring.area = width_rectangle.value * height_rectangle.value
    ring.mm_dipolar = ring.up * ring.area * ring.current


def toggle_pause(btn):
    global running
    running = not running
    btn.text = "Continuar" if not running else "Pausar"
    seta_forca_dir.visible = running
    seta_forca_esq.visible = running
    angle_slider.disabled = running


# --- INTERFACE ---
scene.append_to_caption("<b>Configurações Iniciais:</b>\n")

scene.append_to_caption("Ângulo Inicial: ")
angle_slider = slider(bind=mudar_angulo_inicial, min=0, max=360, step=1, value=0)
angle_t = wtext(text=" 0°")
scene.append_to_caption(" <i>(Só funciona com a simulação pausada)</i>")

scene.append_to_caption("\n\n<b>Variáveis Físicas:</b>\n")

scene.append_to_caption("Campo Magnético (B): ")
field = slider(bind=mudar_campo, min=-1, max=1, value=0, id="f")
field_t = wtext(text=f" {field.value:1.2f} T")
scene.append_to_caption("\n\n")

scene.append_to_caption("Corrente (i): ")
current = slider(bind=mudar_espira, min=-30, max=30, value=0, id="current")
current_t = wtext(text=f" {current.value:1.2f} A")
scene.append_to_caption("\n\n")

scene.append_to_caption("Nº de Espiras (N): ")
espiras_slider = slider(
    bind=mudar_espira, min=1, max=100, step=1, value=1, id="espiras"
)
espiras_t = wtext(text=f" {espiras_slider.value:1.0f}")
scene.append_to_caption("\n\n")

scene.append_to_caption("Largura: ")
width_rectangle = slider(bind=mudar_espira, min=0.1, max=10, value=10, id="width")
width_t = wtext(text=f" {width_rectangle.value:1.2f} m")
scene.append_to_caption(" | Altura: ")
height_rectangle = slider(bind=mudar_espira, min=0.1, max=10, value=10, id="height")
height_t = wtext(text=f" {height_rectangle.value:1.2f} m")
scene.append_to_caption("\n\n")

scene.append_to_caption("Massa (g): ")
massa_rectangle = slider(bind=mudar_espira, min=1, max=100, value=10, id="mass")
massa_t = wtext(text=f" {massa_rectangle.value:1.2f} g")
scene.append_to_caption("\n\n")

btn_pause = button(text="Começar", pos=scene.title_anchor, bind=toggle_pause)

texto_forca = label(
    pos=vec(-12, 12, 0), text="", box=False, line=False, opacity=0, color=color.orange
)
texto_torque = label(
    pos=vec(-12, 10.5, 0), text="", box=False, line=False, opacity=0, color=color.green
)
texto_mu = label(
    pos=vec(-12, 9, 0), text="", box=False, line=False, opacity=0, color=color.black
)

# --- LOOP ---
while True:
    if running:
        rate(1 / dt)

        # Amortecimento
        b = 5.0
        air_drag = b * ring.velocity

        # Torque
        tau_vec = ring.n_espiras * cross(ring.mm_dipolar, seta_campo.axis)

        # Atualização da Inércia
        acc = (tau_vec.z - air_drag) / massa_rectangle.value
        ring.velocity += acc * dt

        # Aplicar Rotação
        d_theta = ring.velocity * dt
        ring.rotate(angle=d_theta, axis=vec(0, 0, 1))
        ring.border = ring.border.rotate(angle=d_theta, axis=vec(0, 0, 1))
        ring.mm_dipolar = ring.up * ring.area * ring.current

        # Atualizar setas de Força (Laranjas)
        L_vec = vec(0, 0, height_rectangle.value)
        F_vec = cross(ring.n_espiras * ring.current * L_vec, seta_campo.axis) * 0.1
        dir_lateral = cross(ring.up, vec(0, 0, 1)).hat

        seta_forca_dir.pos = dir_lateral * (height_rectangle.value / 2)
        seta_forca_dir.axis = -F_vec
        seta_forca_esq.pos = -dir_lateral * (height_rectangle.value / 2)
        seta_forca_esq.axis = F_vec

        texto_forca.text = f"Módulo da Força (|F|): {mag(F_vec):.2f} N"
        texto_torque.text = f"Módulo do Torque (|Tau|): {mag(tau_vec):.2f} N.m"
        texto_mu.text = f"Momento Dipolar (|Mu|): {mag(ring.mm_dipolar):.2f} A.m²"
    else:
        rate(10)
