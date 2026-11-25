// tb_first.v - first simulation: feed two input pairs to four adders and print the sums.
`timescale 1ns/1ps
module tb_first;
    reg  [15:0] a, b;
    wire [16:0] s_exact, s_trua4, s_loa4, s_esa8, s_trua3, s_loa3;

    adder_exact         u_exact (.a(a), .b(b), .sum(s_exact));
    adder_trua #(.K(4)) u_trua4 (.a(a), .b(b), .sum(s_trua4));
    adder_loa  #(.K(4)) u_loa4  (.a(a), .b(b), .sum(s_loa4));
    adder_esa  #(.S(8)) u_esa8  (.a(a), .b(b), .sum(s_esa8));
    adder_trua #(.K(3)) u_trua3 (.a(a), .b(b), .sum(s_trua3));
    adder_loa  #(.K(3)) u_loa3  (.a(a), .b(b), .sum(s_loa3));

    initial begin
        $dumpfile("first.vcd");          // waveform file (optional viewing)
        $dumpvars(0, tb_first);

        a = 16'hFFFF; b = 16'h0001; #10; // apply inputs, wait 10 ns
        $display("a=%h b=%h  exact=%h  TruA-4=%h  LOA-4=%h  ESA-8=%h",
                 a, b, s_exact, s_trua4, s_loa4, s_esa8);

        a = 16'd183; b = 16'd109; #10;   // the hand example from Day 3
        $display("a=%0d b=%0d  exact=%0d  TruA-3=%0d  LOA-3=%0d",
                 a, b, s_exact, s_trua3, s_loa3);
        $finish;
    end
endmodule
