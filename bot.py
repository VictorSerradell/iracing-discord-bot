import os
import discord
from discord.ext import commands
from iracingdataapi.client import irDataClient
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
IR_USERNAME = os.getenv("IRACING_USERNAME")
IR_PASSWORD = os.getenv("IRACING_PASSWORD")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no definida. Agrégala en Railway o .env.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

ir_client = None

@bot.event
async def on_ready():
    global ir_client
    print(f"Bot conectado como {bot.user}")
    
    try:
        ir_client = irDataClient(
            username=IR_USERNAME,
            password=IR_PASSWORD,
            use_pydantic=True
        )
        print("Conectado a iRacing Data API ✓")
        
        # Test de conexión simple (endpoint sin parámetros obligatorios)
        try:
            cars = ir_client.get_cars()
            print(f"Test API OK: {len(cars)} coches cargados")
        except Exception as test_e:
            print(f"Test API falló: {test_e}")
            if hasattr(ir_client, 'last_response') and ir_client.last_response:
                print("Respuesta raw (primeros 500 chars):", ir_client.last_response.text[:500])
    except Exception as e:
        print(f"Error al conectar a iRacing: {e}")
        print("Causas comunes: credenciales inválidas, 2FA activado, legacy auth no habilitado o cuenta no aprobada para Password Limited.")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! Bot online.")

@bot.command(name="status")
async def status(ctx):
    status_text = "✅ Conectado a iRacing" if ir_client else "⚠️ Sin conexión a iRacing"
    await ctx.send(f"Bot: {status_text} | Prefijo: {PREFIX}")

@bot.command(name="mystats")
async def my_stats(ctx):
    if ir_client is None:
        await ctx.send("No conectado a iRacing. Revisa logs.")
        return
    
    try:
        profile = ir_client.member_profile()
        cust_id = profile.get("cust_id")
        if cust_id is None:
            raise ValueError("No cust_id en la respuesta del perfil.")
        
        name = profile.get("name", "Tu nombre")
        
        stats = ir_client.member_chart_data(cust_id=cust_id, chart_type=1)
        
        irating = stats.get("irating", [{}])[-1].get("value", "N/A")
        safety_rating = stats.get("safety_rating", [{}])[-1].get("value", "N/A")
        
        embed = discord.Embed(title=f"Tus stats iRacing - {name}", color=0x00ff00)
        embed.add_field(name="iRating", value=irating, inline=True)
        embed.add_field(name="Safety Rating", value=f"{safety_rating:.2f}", inline=True)
        embed.add_field(name="Cust ID", value=cust_id, inline=True)
        embed.set_footer(text="Datos de iRacing API")
        
        await ctx.send(embed=embed)
    except Exception as e:
        error_msg = f"Error al obtener stats: {str(e)} (tipo: {type(e).__name__})"
        await ctx.send(error_msg)
        print(f"Error mystats: {repr(e)}")
        try:
            if hasattr(ir_client, 'last_response') and ir_client.last_response:
                print("Respuesta raw API (500 chars):", ir_client.last_response.text[:500])
        except:
            print("No se pudo obtener respuesta raw")

@bot.command(name="profile")
async def profile(ctx, *, arg: str = None):
    if ir_client is None:
        return await ctx.send("API no disponible.")
    
    if arg is None:
        await ctx.send(f"Uso: {PREFIX}profile <cust_id>  Ej: {PREFIX}profile 123456")
        return
    
    try:
        cust_id = int(arg.strip())
    except ValueError:
        await ctx.send("Cust ID debe ser un número.")
        return
    
    try:
        profile = ir_client.member_profile(cust_id=cust_id)
        name = profile.get("name", "Desconocido")
        
        chart = ir_client.member_chart_data(cust_id=cust_id, chart_type=1)
        ir = chart.get("irating", [{}])[-1].get("value", "N/A")
        sr = chart.get("safety_rating", [{}])[-1].get("value", "N/A")
        
        embed = discord.Embed(title=f"Perfil: {name}", color=0x3498db)
        embed.add_field(name="iRating", value=ir)
        embed.add_field(name="SR", value=f"{sr:.2f}")
        embed.set_footer(text=f"Cust ID: {cust_id}")
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
        print(f"Error profile: {repr(e)}")

bot.run(TOKEN)