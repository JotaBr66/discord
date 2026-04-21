import discord
from openai import OpenAI
import os
import asyncio
import random
from dotenv import load_dotenv

load_dotenv()

cliente = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
bot = discord.Client(intents=intents)

EMOJIS = ["👍", "👎", "😂", "😭", "🔥", "💀", "✨", "🎉", "🤔", "😎", "❤️", "💯", "🗿", "🐢", "🍷"]

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.lower() == '!t':
        
        if not message.reference:
            msg_temp = await message.channel.send("❌ Responde a un mensaje y escribe `!t`")
            await borrar_mensaje_temporal(msg_temp, 5)
            return
        
        async with message.channel.typing():
            try:
                mensaje_referenciado = await message.channel.fetch_message(message.reference.message_id)
                texto_a_traducir = mensaje_referenciado.content
                
                if not texto_a_traducir:
                    msg_temp = await message.channel.send("❌ El mensaje no tiene texto.")
                    await borrar_mensaje_temporal(msg_temp, 5)
                    return
                
                # System prompt personalizado con jerga latina
                system_prompt = """
Actúa como un traductor experto en jerga de internet, videojuegos y redes sociales, incluyendo slang de Estados Unidos y Latinoamérica (México, Puerto Rico, República Dominicana, Perú, etc.).

Traduce el texto que te daré al español, pero NO de forma literal. Interpreta el significado real como lo haría un joven en chats, juegos o redes sociales.

Reglas:

- Expande abreviaturas comunes (ej: "rn", "b4", "idk", "stfu", "brb", "gg", "wtf").
- Interpreta slang moderno (ej: "fr", "ong", "lmao", "npc", "cringe", "based").
- Reconoce y adapta jerga latina (ej: "wey", "mano", "klk", "causa", "broder", "chamo", "pana", "flaco", etc.).
- Traduce insultos y lenguaje ofensivo manteniendo la intención (enojo, broma, sarcasmo, toxicidad), pero usando equivalentes naturales en español.
- Si el texto mezcla idiomas (Spanglish), adáptalo de forma fluida.
- Mantén el tono original (amigable, burlón, tóxico, sarcástico, competitivo, etc.).
- Si una palabra o abreviatura es ambigua (ej: "sybau"), interpreta según contexto o agrega una breve aclaración entre paréntesis.
- Evita traducciones robóticas; haz que suene como chat real.
- Adapta ligeramente al estilo latino neutro o juvenil si no se especifica país.

Solo devuelve la traducción, sin explicaciones adicionales.
"""
                
                respuesta = cliente.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Texto a traducir: \"{texto_a_traducir}\""}
                    ],
                    temperature=0.6,
                    max_tokens=500
                )
                
                traduccion = respuesta.choices[0].message.content
                autor = mensaje_referenciado.author.display_name
                
                mensaje_traduccion = await message.channel.send(f"📝 **Traducción** (de {autor}):\n{traduccion}")
                
                await gestionar_mensaje_con_reacciones(mensaje_traduccion)
                
                # Borrar mensaje del usuario (ignorar errores)
                try:
                    await message.delete()
                except:
                    pass
                
            except discord.NotFound:
                msg_temp = await message.channel.send("❌ No se encontró el mensaje.")
                await borrar_mensaje_temporal(msg_temp, 5)
            except Exception as e:
                print(f"Error (ignorado): {e}")
    
    elif message.content.lower() == '!help':
        ayuda = await message.channel.send("""
**🤖 Bot Traductor de Jerga (Latinoamérica)**
**Comando:** `!t`

**Qué traduce:**
- 🇺🇸 Jerga de internet y gaming (lmao, fr, ong, npc, cringe)
- 🇲🇽 Jerga mexicana (wey, no mames)
- 🇵🇪 Jerga peruana (causa, mano, flaco)
- 🇵🇷 Jerga puertorriqueña (broder, chacho, boricua)
- 🇩🇴 Jerga dominicana (klk, dímelo, pana)
- 🇻🇪 Jerga venezolana (chamo, pana, marico)

**Cómo usar:**
1. Responde a un mensaje en inglés
2. Escribe `!t` y envía
        """)
        await gestionar_mensaje_con_reacciones(ayuda)

async def gestionar_mensaje_con_reacciones(mensaje):
    """Añade reacción del bot y espera SEGUNDA reacción para borrar"""
    
    emoji_random = random.choice(EMOJIS)
    
    try:
        await mensaje.add_reaction(emoji_random)
    except:
        return
    
    def check(reaction, user):
        return (reaction.message.id == mensaje.id and 
                str(reaction.emoji) == emoji_random and
                user != bot.user)
    
    try:
        await bot.wait_for('reaction_add', timeout=10.0, check=check)
        
        try:
            await mensaje.delete()
        except:
            pass
            
    except asyncio.TimeoutError:
        pass

async def borrar_mensaje_temporal(mensaje, segundos):
    await asyncio.sleep(segundos)
    try:
        await mensaje.delete()
    except:
        pass

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ Error: No se encontró DISCORD_BOT_TOKEN")
    else:
        bot.run(token)
