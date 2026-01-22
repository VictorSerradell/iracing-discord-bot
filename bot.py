import os
import discord
from discord.ext import commands
import random
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no está definida. Agrégala en Railway o .env.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    print("¡Listo para roastear y divertirnos mientras esperamos iRacing! 🔥")

# Comandos básicos de prueba
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! Estoy vivo y con ganas de quemar a alguien 😈")

@bot.command(name="status")
async def status(ctx):
    await ctx.send(f"Bot online ✅ | Prefijo: {PREFIX} | API iRacing: en espera de credenciales OAuth")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Comandos disponibles 🔥", color=0xff4500)
    embed.add_field(name=f"{PREFIX}ping", value="Comprueba que estoy despierto", inline=False)
    embed.add_field(name=f"{PREFIX}status", value="Estado del bot", inline=False)
    embed.add_field(name=f"{PREFIX}help", value="Este mensaje", inline=False)
    embed.add_field(name=f"{PREFIX}meme", value="Meme aleatorio de simracing", inline=False)
    embed.add_field(name=f"{PREFIX}roast [@usuario]", value="Quema a alguien (o a ti mismo)", inline=False)
    embed.add_field(name=f"{PREFIX}roast [@usuario] hard", value="Versión sin piedad", inline=False)
    embed.add_field(name=f"{PREFIX}motivation", value="Frase motivacional... o algo así", inline=False)
    embed.add_field(name=f"{PREFIX}lap", value="Tu vuelta rápida imaginaria", inline=False)
    embed.add_field(name=f"{PREFIX}crash", value="Drama de carrera instantáneo", inline=False)
    await ctx.send(embed=embed)

# Memes aleatorios
memes = [
    "https://i.imgur.com/8m3jK.gif",  # crash clásico
    "https://tenor.com/view/sim-racing-crash-gif-17894567",
    "https://i.imgur.com/Qwerty.gif",  # agrega links reales de memes simracing
    "https://i.imgur.com/abc123.jpg",  # placeholder - sustituye por links reales
    "https://i.imgur.com/def456.png"
]

@bot.command(name="meme")
async def meme(ctx):
    meme_url = random.choice(memes)
    await ctx.send(f"Dosis de simracing humor: {meme_url}\n(¡Cuidado con los spoilers de tu próxima carrera!)")

# Roast mejorado
roasts_soft = [
    "Tu iRating sube más despacio que un tractor en Monza...",
    "Conduces como si el 'brake' fuera un mito urbano",
    "Tu SR es alto porque corres en lluvia... y aun así chocas 😂",
    "Eres tan lento que el safety car te pide que aceleres",
    "Tu línea parece dibujada por un niño con los ojos vendados"
]

roasts_hard = [
    "Tu iRating es tan bajo que los AI rookies te ven venir y se apartan por lástima...",
    "Conduces como si el volante fuera un joystick de PS1 sin vibración",
    "Tienes más incidents que un político con promesas incumplidas",
    "Tu ghost car en replay parece un borracho en patines eléctricos",
    "Eres el motivo por el que existe el black flag... y el wall ride como deporte olímpico",
    "Tu qualifying es tan lento que clasificas en la vuelta de calentamiento del día siguiente",
    "Corres tan sucio que los safety cars se activan solos cuando apareces en el grid",
    "Tu setup es tan malo que hasta el muro te dice 'bro, para ya que me duele'",
    "Tus restarts son tan malos que hasta el caution flag se ríe de ti en voz alta",
    "Eres tan lento que el pace car te adelanta y te pide autógrafo"
]

@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None, intensity: str = "medium"):
    if member is None:
        member = ctx.author

    if member.bot:
        await ctx.send("No roasteo bots, que ya tenemos suficiente con los AI de iRacing 😤")
        return

    intensity = intensity.lower()
    if intensity == "hard":
        roast_text = random.choice(roasts_hard)
        fire = "🔥🔥🔥🔥"
    elif intensity == "soft":
        roast_text = random.choice(roasts_soft)
        fire = "🔥"
    else:  # medium por defecto
        all_roasts = roasts_soft + roasts_hard[:8]  # mezcla equilibrada
        roast_text = random.choice(all_roasts)
        fire = "🔥🔥"

    await ctx.send(f"{member.mention} {roast_text}\n{fire}")

# Motivación simulada
motivaciones = [
    "¡Sigue empujando! El pódium está a solo 3 restarts de distancia...",
    "El que no choca, no avanza... o eso dicen los que chocan mucho",
    "Tu próximo incident es solo práctica para el siguiente",
    "El wall ride es una técnica válida... en mi mundo",
    "Recuerda: el que llega último, llega con más historia que contar"
]

@bot.command(name="motivation")
async def motivation(ctx):
    frase = random.choice(motivaciones)
    await ctx.send(f"💪 {frase}\n¡A darle, crack! (pero no al muro, eh)")

# Vuelta rápida imaginaria
@bot.command(name="lap")
async def lap(ctx):
    tiempo = random.uniform(1.15, 3.59)
    await ctx.send(f"¡Vuelta rápida imaginaria! ⏱️ {tiempo:.3f} segundos... en mis sueños, claro 🚀")

# Crash dramático
@bot.command(name="crash")
async def crash(ctx):
    await ctx.send("💥 **¡BOOM!** Acabo de besar el muro en la curva 1... otra vez 😭\n"
                   "Mi coche ahora es arte abstracto en la grava. ¿Quién me recoge?")

# Iniciar bot
bot.run(TOKEN)