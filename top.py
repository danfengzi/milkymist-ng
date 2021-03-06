from migen.fhdl.structure import *
from migen.fhdl import tools, verilog, autofragment
from migen.bus import wishbone, csr, wishbone2csr

from milkymist import m1reset, clkfx, lm32, norflash, uart, sram
import constraints

def get():
	MHz = 1000000
	clk_freq = 80*MHz
	sram_size = 4096 # in kilobytes
	
	clkfx_sys = clkfx.ClkFX(50*MHz, clk_freq)
	reset0 = m1reset.M1Reset()
	
	cpu0 = lm32.LM32()
	norflash0 = norflash.NorFlash(25, 12)
	sram0 = sram.SRAM(sram_size//4)
	wishbone2csr0 = wishbone2csr.WB2CSR()
	wishbonecon0 = wishbone.InterconnectShared(
		[cpu0.ibus, cpu0.dbus],
		[(0, norflash0.bus), (1, sram0.bus), (3, wishbone2csr0.wishbone)],
		register=True,
		offset=1)
	uart0 = uart.UART(0, clk_freq, baud=115200)
	csrcon0 = csr.Interconnect(wishbone2csr0.csr, [uart0.bank.interface])
	
	frag = autofragment.from_local()
	src_verilog, vns = verilog.convert(frag,
		{clkfx_sys.clkin, reset0.trigger_reset},
		name="soc",
		clk_signal=clkfx_sys.clkout,
		rst_signal=reset0.sys_rst,
		return_ns=True)
	src_ucf = constraints.get(vns, clkfx_sys, reset0, norflash0, uart0)
	return (src_verilog, src_ucf)
