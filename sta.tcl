# sta.tcl - measure the slowest path through the netlist that synth.ys produced.
# Run with:  sta -no_init -no_splash -exit sta.tcl
read_liberty NangateOpenCellLibrary_typical.lib
read_verilog netlist.v
link_design adder_trua

# The adder has no clock, so define a pretend ("virtual") 10 ns clock to time against.
create_clock -name vclk -period 10
set_input_delay  0 -clock vclk [all_inputs]
set_output_delay 0 -clock vclk [all_outputs]
set_driving_cell -lib_cell BUF_X1 [all_inputs]   ;# inputs come from a real buffer
set_load 3.0 [all_outputs]                       ;# each output drives 3 fF (about two gate inputs)

report_checks -path_delay max -digits 4          ;# print the slowest path
