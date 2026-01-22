import os
import discord
from discord.ext import commands
from iracingdataapi.client import irDataClient
from dotenv import load_dotenv

load_dotenv()

# Configuración
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
IR_USERNAME = os.getenv("IRACING_USERNAME")
IR_PASSWORD = os.getenv("IRACING_PASSWORD")
IR_CLIENT_ID = os.getenv("IRACING_CLIENT_ID")
IR_CLIENT_SECRET = os.getenv("IRACING_CLIENT_SECRET")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Cliente iRacing (se autentica al iniciar)
ir_client = None

@bot.event
async def on_ready():
    global ir_client
    print(f"Bot conectado como {bot.user}")
    
    try:
        ir_client = irDataClient(
            username=IR_USERNAME,
            password=IR_PASSWORD,
            # Si ya tienes access_token guardado, puedes pasarlo aquí en vez de user/pass
            # oauth_access_token="..."
        )
        print("Conectado a iRacing Data API ✓")
    except Exception as e:
        print(f"Error al conectar a iRacing: {e}")

@bot.command(name="mystats")
async def my_stats(ctx):
    if ir_client is None:
        await ctx.send("No conectado a iRacing. Intenta más tarde.")
        return
    
    try:
        # Obtiene tu cust_id automáticamente (del usuario autenticado)
        profile = ir_client.member_profile()
        cust_id = profile.get("cust_id")
        
        # Stats detalladas
        stats = ir_client.member_chart_data(cust_id=cust_id, chart_type=1)  # 1 = iRating/SR
        
        irating = stats.get("irating", [{}])[-1].get("value", "N/A")
        safety_rating = stats.get("safety_rating", [{}])[-1].get("value", "N/A")
        
        embed = discord.Embed(title="Tus stats iRacing", color=0x00ff00)
        embed.add_field(name="iRating", value=irating, inline=True)
        embed.add_field(name="Safety Rating", value=f"{safety_rating:.2f}", inline=True)
        embed.add_field(name="Cust ID", value=cust_id, inline=True)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name="profile")
async def profile(ctx, member: discord.Member = None):
    if ir_client is None:
        return await ctx.send("API no disponible.")
    
    try:
        # Si mencionas a alguien, usa su nick como búsqueda (o guarda cust_id por usuario)
        # Para simplicidad: pedimos cust_id manual
        await ctx.send("Dime el cust_id del piloto (o usa !mystats si es tuyo):")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        msg = await bot.wait_for("message", check=check, timeout=60)
        cust_id = int(msg.content.strip())
        
        profile = ir_client.member_profile(cust_id=cust_id)
        name = profile.get("name", "Desconocido")
        
        # Stats básicas
        chart = ir_client.member_chart_data(cust_id=cust_id, chart_type=1)
        ir = chart.get("irating", [{}])[-1].get("value", "N/A")
        sr = chart.get("safety_rating", [{}])[-1].get("value", "N/A")
        
        embed = discord.Embed(title=f"Perfil: {name}", color=0x3498db)
        embed.add_field(name="iRating", value=ir)
        embed.add_field(name="SR", value=f"{sr:.2f}")
        embed.set_footer(text=f"Cust ID: {cust_id}")
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error al obtener perfil: {e}")

@bot.command(name="series")
async def series_list(ctx):
    if ir_client is None:
        return
    
    try:
        seasons = ir_client.season_list()
        active = [s for s in seasons if s.get("active")]
        
        embed = discord.Embed(title="Series Activas", color=0xe67e22)
        for s in active[:10]:  # limita a 10 para no spamear
            name = s.get("series_name", "N/A")
            embed.add_field(name=name, value=f"ID: {s.get('season_id')}", inline=False)
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run(TOKEN)