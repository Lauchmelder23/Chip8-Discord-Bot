import discord
from instruction import Opcode
from CPU import CPU
import time

client = discord.Client()
cpu = CPU
allowed_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
demos = 6

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Emulator"), status=discord.Status("idle"))
    print("Ready to emulate!")
    # while not cpu.interrupt:
    #    cpu.tick(cpu)


@client.event
async def on_message(message):

    if message.content.lower().startswith("?break"):
        cpu.interrupt = True

    if message.content.lower().startswith("?start"):
        if cpu.interrupt is False:
            await client.send_message(discord.Object(id='485511121407574016'), "CPU already in use")
            return

        if len(message.content) < 8:
            await client.send_message(discord.Object(id='485511121407574016'), "Please choose a valid demo file")
            return

        if not message.content[7:].isdigit():
            await client.send_message(discord.Object(id='485511121407574016'), "Please choose a valid demo file")
            return

        demo = message.content[7:]
        if int(demo) > 6 or int(demo) < 1:
            await client.send_message(discord.Object(id='485511121407574016'), "Please choose a valid demo file")
            return

        timer = time.localtime(time.time())[5]
        cpu.load_rom(cpu, "demo" + demo + ".ch8")
        cpu.interrupt = False
        msg = await client.send_message(discord.Object(id='485511121407574016'), "Awaiting display instructions")
        while not cpu.interrupt:
            cpu.tick(cpu)

            if cpu.drawFlag is True and (time.localtime(time.time())[5] - timer) >= 1:
                screen = ""
                for y in range(0, 31):
                    for x in range(0, 63):
                        screen += cpu.display[y * 64 + x]
                        # print(str(x) + ", " + str(y) + ": " + str(cpu.display[y * 64 + x]))
                    screen += "\n"

                await client.edit_message(msg, "```" + screen + "```")
                cpu.drawFlag = False
                timer = time.localtime(time.time())[5]

        await client.send_message(discord.Object(id='485511121407574016'), "Done!")
        cpu.reset(cpu)

    if message.content.lower().startswith("0x"):
        opc = message.content.upper()[2:6]

        for char in opc:
            if char not in allowed_chars:
                await client.send_message(message.channel, "The character '" + char
                                          + "' is not a valid hexadecimal number!")
                return

        instruction = Opcode(int(opc, 16))
        await client.send_message(message.channel, cpu.execute(cpu, instruction))



client.run(token)