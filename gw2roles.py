import discord
from discord.ext import commands
import random
import json

# --- CONFIGURACION ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- ESTRUCTURA DE ROSTER ---
class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role

roster = [
    Player("Ana", "Tanke"),
    Player("Acccooo", "Healer"),
    Player("Shido", "BoonDPS"),
    Player("Ana (conferencias :0)", "BoonDPS"),
    Player("Pingu", "DPS"),
    Player("Jaume", "DPS"),
    Player("XXXXX", "DPS"),
    Player("XXXXX1", "DPS"),
    Player("XXXXX2", "DPS"),
    Player("XXXXX3", "DPS")
]

# --- CARGAR WINGS DESDE JSON ---
with open('wings_mecanicas.json', 'r', encoding='utf-8') as f:
    wings = json.load(f)

# --- FUNCION DE ASIGNACION ---
def asignar_mecanicas(boss_data, jugadores_disponibles):
    asignaciones = {p.name: [] for p in jugadores_disponibles}
    usados = set()

    for mecanica in boss_data:
        elegibles = [p for p in jugadores_disponibles if p.role in mecanica["roles"] and p.name not in usados]
        if len(elegibles) < mecanica["count"]:
            return f"❌ No hay suficientes jugadores para '{mecanica['name']}' ({mecanica['count']}x)"
        seleccionados = random.sample(elegibles, mecanica["count"])
        for p in seleccionados:
            asignaciones[p.name].append(mecanica["name"])
            usados.add(p.name)

    resultado = "\n**Asignaciones específicas:**\n"
    for nombre, tareas in asignaciones.items():
        if tareas:
            resultado += f"**{nombre}** → {', '.join(tareas)}\n"
    return resultado

# --- FUNCION PARA DIVIDIR COMPOSICION FIJA ---
def obtener_composicion(disponibles):
    disponibles_copia = disponibles[:]
    composicion = {"Tanke": None, "Healer": None, "BoonDPS": [], "DPS": []}
    for p in disponibles_copia:
        if p.role == "Tanke" and composicion["Tanke"] is None:
            composicion["Tanke"] = p
        elif p.role == "Healer" and composicion["Healer"] is None:
            composicion["Healer"] = p
        elif p.role == "BoonDPS" and len(composicion["BoonDPS"]) < 2:
            composicion["BoonDPS"].append(p)
        elif p.role == "DPS" and len(composicion["DPS"]) < 6:
            composicion["DPS"].append(p)
    seleccionados = [p for p in [composicion['Tanke'], composicion['Healer']] + composicion['BoonDPS'] + composicion['DPS'] if p]
    return composicion

# --- COMPROBAR CANAL ---
def canal_valido(ctx):
    return ctx.channel.name == "mecanicas"

# --- FUNCION PARA ENVIAR MENSAJE EN TROZOS ---
async def enviar_mensaje_largo(ctx, mensaje):
    partes = [mensaje[i:i+1990] for i in range(0, len(mensaje), 1990)]
    for parte in partes:
        await ctx.send(parte)

# --- COMANDOS ---
@bot.command()
async def asignar(ctx, wing: str, *, boss: str):
    if not canal_valido(ctx): return
    wing = wing.title()
    boss = boss.title()
    if wing not in wings:
        await ctx.send(f"❌ Wing '{wing}' no existe.")
        return
    if boss not in wings[wing]:
        await ctx.send(f"❌ Boss '{boss}' no encontrado en {wing}.")
        return
    disponibles = roster[:]
    composicion = obtener_composicion(disponibles)
    resultado = f"**{boss} ({wing})**\n"
    resultado += f"**Tank:** {composicion['Tanke'].name if composicion['Tanke'] else 'N/A'}\n"
    resultado += f"**Healer:** {composicion['Healer'].name if composicion['Healer'] else 'N/A'}\n"
    resultado += f"**BoonDPS:** {', '.join(p.name for p in composicion['BoonDPS']) or 'N/A'}\n"
    resultado += asignar_mecanicas(wings[wing][boss], disponibles)
    await enviar_mensaje_largo(ctx, resultado)

@bot.command()
async def asignarWing(ctx, wing: str):
    if not canal_valido(ctx): return
    wing = wing.title()
    if wing not in wings:
        await ctx.send(f"❌ Wing '{wing}' no existe.")
        return
    disponibles = roster[:]
    composicion = obtener_composicion(disponibles)
    mensaje = f"**Asignaciones para {wing}:**\n"
    mensaje += f"**Tank:** {composicion['Tanke'].name if composicion['Tanke'] else 'N/A'}\n"
    mensaje += f"**Healer:** {composicion['Healer'].name if composicion['Healer'] else 'N/A'}\n"
    mensaje += f"**BoonDPS:** {', '.join(p.name for p in composicion['BoonDPS']) or 'N/A'}\n"
    for boss, mecanicas in wings[wing].items():
        mensaje += f"\n__{boss}__\n"
        mensaje += asignar_mecanicas(mecanicas, disponibles)
        mensaje += "\n"
    await enviar_mensaje_largo(ctx, mensaje)

@bot.command()
async def asignarTodo(ctx):
    if not canal_valido(ctx): return
    for wing, bosses in wings.items():
        disponibles = roster[:]
        composicion = obtener_composicion(disponibles)
        mensaje = f"**=== {wing} ===**\n"
        mensaje += f"**Tank:** {composicion['Tanke'].name if composicion['Tanke'] else 'N/A'}\n"
        mensaje += f"**Healer:** {composicion['Healer'].name if composicion['Healer'] else 'N/A'}\n"
        mensaje += f"**BoonDPS:** {', '.join(p.name for p in composicion['BoonDPS']) or 'N/A'}\n"
        for boss, mecanicas in bosses.items():
            mensaje += f"\n__{boss}__\n"
            mensaje += asignar_mecanicas(mecanicas, disponibles)
            mensaje += "\n"
        await enviar_mensaje_largo(ctx, mensaje)


# --- EJECUTAR BOT ---
bot.run("CODIGITO")
