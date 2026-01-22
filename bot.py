import os
import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
from iracingdataapi.client import irDataClient

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
IR_USERNAME = os.getenv("IRACING_USERNAME")
IR_PASSWORD = os.getenv("IRACING_PASSWORD")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no definida.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

ir_client = None

@bot.event
async def on_ready():
    global ir_client
    print(f"Bot conectado como {bot.user}")
    print("¡Listo para roastear y probar iRacing! 🔥")

    try:
        ir_client = irDataClient(
            username=IR_USERNAME,
            password=IR_PASSWORD,
            use_pydantic=False
        )
        print("Conectado a iRacing Data API ✓")

        # Test con debug ultra detallado
        try:
            print("Intentando get_cars() para probar conexión...")
            cars = ir_client.get_cars()
            print(f"ÉXITO! Se cargaron {len(cars)} coches.")
        except Exception as test_e:
            print(f"Test falló: {repr(test_e)}")
            print("Tipo de error:", type(test_e).__name__)
            
            try:
                last_resp = None
                if hasattr(ir_client, 'last_response'):
                    last_resp = ir_client.last_response
                elif hasattr(ir_client, '_last_response'):
                    last_resp = ir_client._last_response
                
                if last_resp:
                    print("=== DEBUG RAW API (TEST) ===")
                    print("Status code:", last_resp.status_code)
                    print("Content-Type:", last_resp.headers.get('Content-Type', 'No disponible'))
                    print("Contenido (primeros 1200 caracteres):")
                    print(last_resp.text[:1200])
                    print("=======================")
                else:
                    print("No se encontró last_response en ir_client")
            except Exception as debug_e:
                print("Error al capturar raw:", debug_e)
    except Exception as e:
        print(f"Error al crear cliente iRacing: {e}")

# Comandos divertidos (mantenerlos)
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! Estoy vivo y con ganas de quemar a alguien 😈")

@bot.command(name="status")
async def status(ctx):
    api_status = "✅ Conectado" if ir_client else "⚠️ Sin conexión a iRacing"
    await ctx.send(f"Bot online | Prefijo: {PREFIX} | iRacing API: {api_status}")

@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(title="Comandos disponibles 🔥", color=0xff4500)
    embed.add_field(name=f"{PREFIX}ping", value="Comprueba que estoy vivo", inline=False)
    embed.add_field(name=f"{PREFIX}status", value="Estado del bot", inline=False)
    embed.add_field(name=f"{PREFIX}ayuda", value="Este mensaje", inline=False)
    embed.add_field(name=f"{PREFIX}meme", value="Meme aleatorio", inline=False)
    embed.add_field(name=f"{PREFIX}roast [@usuario] [soft/medium/hard]", value="Quema a alguien", inline=False)
    embed.add_field(name=f"{PREFIX}motivation", value="Frase motivacional", inline=False)
    embed.add_field(name=f"{PREFIX}lap", value="Vuelta rápida imaginaria", inline=False)
    embed.add_field(name=f"{PREFIX}crash", value="Drama de carrera", inline=False)
    embed.add_field(name=f"{PREFIX}mystats", value="Tus stats de iRacing (prueba)", inline=False)
    embed.add_field(name=f"{PREFIX}profile <cust_id>", value="Stats de otro piloto", inline=False)
    await ctx.send(embed=embed)

# Memes
memes = [
    "https://i.imgur.com/8m3jK.gif",
    "https://tenor.com/view/sim-racing-crash-gif-17894567"
]

@bot.command(name="meme")
async def meme(ctx):
    meme_url = random.choice(memes)
    await ctx.send(f"Simracing humor: {meme_url}")

# Roast simple
roasts = [
    "Tu iRating es tan bajo que los AI rookies te ven venir y se apartan por lástima...",
    "Conduces como si el volante fuera un joystick de PS1 sin vibración",
    "Tienes más incidents que victorias... y las victorias son en practice solo 😭"
]

@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    roast_text = random.choice(roasts)
    await ctx.send(f"{member.mention} {roast_text} 🔥")

@bot.command(name="motivation")
async def motivation(ctx):
    frases = ["¡Sigue empujando! El pódium está a solo 3 restarts...", "El wall ride es una técnica válida... en mi mundo"]
    await ctx.send(f"💪 {random.choice(frases)}")

@bot.command(name="lap")
async def lap(ctx):
    tiempo = random.uniform(1.15, 3.59)
    await ctx.send(f"¡Vuelta rápida imaginaria! ⏱️ {tiempo:.3f} s... en mis sueños 🚀")

@bot.command(name="crash")
async def crash(ctx):
    await ctx.send("💥 ¡BOOM! Acabo de besar el muro... otra vez 😭")

# Comando iRacing con debug máximo
@bot.command(name="mystats")
async def mystats(ctx):
    if ir_client is None:
        await ctx.send("No conectado a iRacing. Revisa logs.")
        return

    try:
        print("Ejecutando !mystats: member_profile()...")
        profile = ir_client.member_profile()
        cust_id = profile.get("cust_id")
        name = profile.get("name", "Tu nombre")

        stats = ir_client.member_chart_data(cust_id=cust_id, chart_type=1)

        irating = stats.get("irating", [{}])[-1].get("value", "N/A")
        sr = stats.get("safety_rating", [{}])[-1].get("value", "N/A")

        embed = discord.Embed(title=f"Tus stats - {name}", color=0x00ff00)
        embed.add_field(name="iRating", value=irating, inline=True)
        embed.add_field(name="SR", value=f"{sr:.2f}", inline=True)
        embed.add_field(name="Cust ID", value=cust_id, inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error en mystats: {str(e)}")
        print(f"mystats error: {repr(e)}")
        
        try:
            last_resp = None
            if hasattr(ir_client, 'last_response'):
                last_resp = ir_client.last_response
            elif hasattr(ir_client, '_last_response'):
                last_resp = ir_client._last_response
            
            if last_resp:
                print("=== RAW mystats ===")
                print("Status code:", last_resp.status_code)
                print("Content-Type:", last_resp.headers.get('Content-Type', 'No disponible'))
                print("Raw response (1200 chars):")
                print(last_resp.text[:1200])
                print("==================")
            else:
                print("No hay last_response disponible")
        except Exception as debug_e:
            print("Error capturando raw:", debug_e)

# Comando profile con debug
@bot.command(name="profile")
async def profile(ctx, cust_id: str):
    if ir_client is None:
        await ctx.send("API no disponible.")
        return

    try:
        cust_id_int = int(cust_id)
        print(f"Ejecutando !profile {cust_id_int}")
        profile = ir_client.member_profile(cust_id=cust_id_int)
        name = profile.get("name", "Desconocido")

        chart = ir_client.member_chart_data(cust_id=cust_id_int, chart_type=1)
        ir = chart.get("irating", [{}])[-1].get("value", "N/A")
        sr = chart.get("safety_rating", [{}])[-1].get("value", "N/A")

        embed = discord.Embed(title=f"Perfil: {name}", color=0x3498db)
        embed.add_field(name="iRating", value=ir)
        embed.add_field(name="SR", value=f"{sr:.2f}")
        embed.set_footer(text=f"Cust ID: {cust_id}")
        await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("Cust ID debe ser un número.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
        print(f"profile error: {repr(e)}")
        try:
            last_resp = None
            if hasattr(ir_client, 'last_response'):
                last_resp = ir_client.last_response
            elif hasattr(ir_client, '_last_response'):
                last_resp = ir_client._last_response
            
            if last_resp:
                print("=== RAW profile ===")
                print("Status code:", last_resp.status_code)
                print("Content-Type:", last_resp.headers.get('Content-Type'))
                print("Raw (1200 chars):")
                print(last_resp.text[:1200])
                print("==================")
        except:
            print("No raw disponible en profile")

bot.run(TOKEN)