import os 
import nextcord
from nextcord.ext import commands
import wavelink

from nextcord.abc import GuildChannel 
from nextcord import Interaction, SlashOption, ChannelType

intents = nextcord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents) 


@bot.event 
async def on_ready():
  print('rodando onii-chan *-*')
  bot.loop.create_task(node_connect())
  if len(bot.voice_clients) > 1: bot.__setattr__('current_player', bot.voice_clients[0])

async def node_connect():
  await bot.wait_until_ready()
  await wavelink.NodePool.create_node(bot=bot, host='lava.link', port=80, password='dismusic')

@bot.event 
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f'node {node.identifier} is ready')

@bot.event 
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.YouTubeMusicTrack, reason):
  if player.queue.is_empty:
    return await player.disconnect()

  next_song: wavelink.YouTubeTrack = player.queue.get()
  interaction: Interaction = player.__getattribute__('interaction')
  await interaction.send(f'pronto... agora vou tocar {next_song.title} uwu')
  await player.play(next_song)

@bot.slash_command(name='sair', description='desculpa... eu vou sair', guild_ids=[51375732631496294, 970430050614792203])
async def sair(interaction: Interaction):
  await interaction.send('desculpa onii-chan...')
  interaction.guild.voice_client.queue.clear()
  await interaction.guild.voice_client.disconnect()

@bot.slash_command(name='skip', description='você não tá gostando da música...?', guild_ids=[513757326314962949, 970430050614792203])
async def skip(interaction: Interaction):
  player: wavelink.Player = bot.__getattribute__('current_player')
  print(player)
  next_song: wavelink.YouTubeTrack = await player.queue.get_wait()
  
  await interaction.send(f'agora vou tocar {next_song.title} ;-;')
  await player.play(next_song)
    
@bot.slash_command(name='pause', description='vou parar a música pra voce', guild_ids=[513757326314962949, 970430050614792203])
async def pause(interaction: Interaction):
  player: wavelink.Player = bot.__getattribute__('current_player')
  await interaction.send('pausei... 😖')
  await player.set_pause(True)

@bot.slash_command(name='continuar', description='vou voltar a música pra voce', guild_ids=[513757326314962949, 970430050614792203])
async def resume(interaction: Interaction):
  player: wavelink.Player = bot.__getattribute__('current_player')

  if not player.is_playing():
    return await interaction.send('ainda não tem nenhuma música tocando onii-chan')

  if not player.is_paused():
    return await interaction.send('não tem nenhuma música pausada baka 😝')

  await interaction.send('pronto...')
  await player.resume()

@bot.slash_command(name='cantar', description='vou cantar pro senpai :3', guild_ids=[970430050614792203, 513757326314962949])
async def cantar(interaction: Interaction, channel: GuildChannel = SlashOption(channel_types=[ChannelType.voice]), musica: str = SlashOption(description="nome da música pra eu cantar")):

  musica = await wavelink.YouTubeTrack.search(query=musica, return_first=True)

  if not interaction.guild.voice_client: 
    player: wavelink.Player = await channel.connect(cls=wavelink.Player)
  else:
    player: wavelink.Player = interaction.guild.voice_client


  if player.queue.is_empty and not player.is_playing():
    await interaction.send(f'ok 👉👈, vou tocar {musica.title} :3 !')
    await player.play(musica)
  else:
    await interaction.send(f'você vai ter que esperar 😖... vou colocar {musica.title} na fila pra você onii-chan ;-;')
    await player.queue.put_wait(musica)

  player.__setattr__('interaction', interaction)
  bot.__setattr__('current_player', player)  

@bot.event 
async def on_disconnect():
  for player in bot.voice_clients:
    player.queue.clear()

bot.run(os.getenv('TOKEN'))