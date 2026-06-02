import discord
from discord.ext import commands, tasks
import subprocess
import psutil
import socket
import requests
import asyncio

# =========================
# CONFIG
# =========================

TOKEN = "TOKEN DO BOT"

#from dotenv import load_dotenv
#import os
#load_dotenv()
#TOKEN = os.getenv("TOKEN")

AUTHORIZED_USERS = [ID DO USUARIO MASTER DO DISCORD]

ALERT_CHANNEL_ID = "ID DO CANAL DE ALERTAS"

DISK_ALERT = 90
CPU_ALERT = 90
RAM_ALERT = 90
TEMP_ALERT = 80

# =========================
# DISCORD
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# SERVICES
# =========================

docker_containers = {
    "lidarr": "lidarr",
    "radarr": "radarr",
    "sonarr": "sonarr",
    "prowlarr": "prowlarr",
    "homeassistant": "homeassistant",
    "flaresolverr": "flaresolverr"
}

system_services = {
    "plex": "plexmediaserver",
    "qbittorrent": "qbittorrent",
    "adguard": "AdGuardHome"
}

compose_paths = {
    "lidarr": "/home/tiago2609/docker/lidarr",
    "prowlarr": "/home/tiago2609/docker/prowlarr",
    "homeassistant": "/home/tiago2609/homeassistant",
    "docker": "/home/tiago2609/docker"
}

# =========================
# HELPERS
# =========================

def authorized(ctx):
    return ctx.author.id in AUTHORIZED_USERS

def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def get_temperature():
    try:
        output = run_command(["sensors"])

        for line in output.splitlines():
            if "Package id 0" in line or "Tctl" in line:
                parts = line.split("+")
                if len(parts) > 1:
                    temp = parts[1].split("°")[0]
                    return float(temp)

        return "N/A"

    except:
        return "N/A"

def internet_online():
    try:
        requests.get("https://1.1.1.1", timeout=5)
        return True
    except:
        return False

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    health_monitor.start()

# =========================
# BASIC
# =========================

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def ip(ctx):
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    await ctx.send(f"IP do servidor: `{ip}`")

# =========================
# SERVER
# =========================

@bot.command()
async def server(ctx):

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime = run_command(["uptime", "-p"])
    temp = get_temperature()

    msg = f"""
CPU: {cpu}%
RAM: {ram}%
DISCO: {disk}%
TEMP: {temp}°C
UPTIME: {uptime}
"""

    await ctx.send(f"```{msg}```")

@bot.command()
async def temp(ctx):

    temp = get_temperature()

    await ctx.send(f"Temperatura: `{temp}°C`")

@bot.command()
async def docker(ctx):

    result = run_command([
        "docker",
        "ps",
        "--format",
        "table {{.Names}}\t{{.Status}}"
    ])

    await ctx.send(f"```{result}```")

@bot.command()
async def compose(ctx):

    result = ""

    for name, path in compose_paths.items():
        result += f"{name}:\n{path}\n\n"

    await ctx.send(f"```{result}```")

@bot.command()
async def health(ctx):

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = get_temperature()

    offline = []

    # Docker
    for name, container in docker_containers.items():

        try:
            status = run_command([
                "docker",
                "inspect",
                "-f",
                "{{.State.Status}}",
                container
            ])

            if status != "running":
                offline.append(name)

        except:
            offline.append(name)

    # Services
    for name, service in system_services.items():

        status = run_command([
            "systemctl",
            "is-active",
            service
        ])

        if status != "active":
            offline.append(name)

    internet = "OK" if internet_online() else "OFFLINE"

    msg = f"""
CPU: {cpu}%
RAM: {ram}%
DISCO: {disk}%
TEMP: {temp}°C
INTERNET: {internet}

OFFLINE:
{', '.join(offline) if offline else 'Nenhum'}
"""

    await ctx.send(f"```{msg}```")

# =========================
# CONTROL
# =========================

@bot.command()
async def restart(ctx, service):

    if not authorized(ctx):
        return

    # Docker
    if service in docker_containers:

        run_command([
            "docker",
            "restart",
            docker_containers[service]
        ])

        await ctx.send(f"{service} reiniciado.")
        return

    # systemd
    if service in system_services:

        run_command([
            "sudo",
            "systemctl",
            "restart",
            system_services[service]
        ])

        await ctx.send(f"{service} reiniciado.")
        return

    await ctx.send("Serviço inválido.")

@bot.command()
async def stop(ctx, service):

    if not authorized(ctx):
        return

    if service in docker_containers:

        run_command([
            "docker",
            "stop",
            docker_containers[service]
        ])

        await ctx.send(f"{service} parado.")
        return

    if service in system_services:

        run_command([
            "sudo",
            "systemctl",
            "stop",
            system_services[service]
        ])

        await ctx.send(f"{service} parado.")
        return

@bot.command()
async def start(ctx, service):

    if not authorized(ctx):
        return

    if service in docker_containers:

        run_command([
            "docker",
            "start",
            docker_containers[service]
        ])

        await ctx.send(f"{service} iniciado.")
        return

    if service in system_services:

        run_command([
            "sudo",
            "systemctl",
            "start",
            system_services[service]
        ])

        await ctx.send(f"{service} iniciado.")
        return

@bot.command()
async def status(ctx, service):

    # Docker
    if service in docker_containers:

        status = run_command([
            "docker",
            "inspect",
            "-f",
            "{{.State.Status}}",
            docker_containers[service]
        ])

        await ctx.send(f"{service}: `{status}`")
        return

    # systemd
    if service in system_services:

        status = run_command([
            "systemctl",
            "is-active",
            system_services[service]
        ])

        await ctx.send(f"{service}: `{status}`")
        return

@bot.command()
async def reboot(ctx):

    if not authorized(ctx):
        return

    await ctx.send("Reiniciando servidor...")

    run_command([
        "sudo",
        "reboot"
    ])

# =========================
# MONITOR
# =========================

@tasks.loop(minutes=5)
async def health_monitor():

    channel = bot.get_channel(ALERT_CHANNEL_ID)

    if not channel:
        return

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temp = get_temperature()

    alerts = []

    if cpu >= CPU_ALERT:
        alerts.append(f"CPU alta: {cpu}%")

    if ram >= RAM_ALERT:
        alerts.append(f"RAM alta: {ram}%")

    if disk >= DISK_ALERT:
        alerts.append(f"DISCO cheio: {disk}%")

    if temp != "N/A":
        if temp >= TEMP_ALERT:
            alerts.append(f"TEMPERATURA alta: {temp}°C")

    # Docker check
    for name, container in docker_containers.items():

        try:
            status = run_command([
                "docker",
                "inspect",
                "-f",
                "{{.State.Status}}",
                container
            ])

            if status != "running":
                alerts.append(f"Container OFFLINE: {name}")

        except:
            alerts.append(f"Container OFFLINE: {name}")

    # Service check
    for name, service in system_services.items():

        status = run_command([
            "systemctl",
            "is-active",
            service
        ])

        if status != "active":
            alerts.append(f"Serviço OFFLINE: {name}")

    if not internet_online():
        alerts.append("Internet OFFLINE")

    if alerts:

        message = "\n".join(alerts)

        await channel.send(
            f"⚠️ ALERTA HOMELAB ⚠️\n```{message}```"
        )

@bot.command()
async def comandos(ctx):

    msg = """
COMANDOS DISPONÍVEIS

INFO
!ping
!server
!docker
!compose
!ip
!temp
!health
!comandos
!power

CONTROLE
!status <serviço>

!restart <serviço>
!start <serviço>
!stop <serviço>

!reboot

SERVIÇOS DISPONÍVEIS

DOCKER
- lidarr
- radarr
- sonarr
- prowlarr
- homeassistant
- flaresolverr

SYSTEMD
- plex
- qbittorrent
- adguard

EXEMPLOS

!restart sonarr
!status plex
!stop qbittorrent
!start adguard
!health
"""

    await ctx.send(f"```{msg}```")

@bot.command()
async def power(ctx):

    if not authorized(ctx):
        return

    try:

        result = run_command([
            "sudo",
            "powerstat",
            "-R",
            "-n",
            "1"
        ])

        watts = "N/A"

        for line in result.splitlines():

            if "Watts" in line:

                parts = line.split()

                for part in parts:

                    try:
                        value = float(part)
                        watts = value
                        break
                    except:
                        pass

        cpu = psutil.cpu_percent(interval=1)

        msg = f"""
CONSUMO ENERGÉTICO

Watts atuais: {watts} W
CPU atual: {cpu}%
"""

        await ctx.send(f"```{msg}```")

    except Exception as e:

        await ctx.send(f"Erro ao obter powerstat: {e}")


# =========================
# START
# =========================

bot.run(TOKEN)
