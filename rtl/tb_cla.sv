// tb_cla.sv - checks the carry-lookahead adder against the simulator's own "+".
// Run with:  iverilog -g2012 -o tb_cla.vvp rtl/adders.v rtl/tb_cla.sv  &&  vvp tb_cla.vvp
`timescale 1ns/1ps
module tb_cla;
    logic [15:0] a, b;
    wire  [16:0] got;
    logic [16:0] want;
    int errors = 0, checks = 0;
    logic [15:0] corners [0:10];

    adder_cla dut (.a(a), .b(b), .sum(got));

    task automatic check();
        #1;
        want = a + b;                      // the reference: the simulator's own adder
        checks++;
        if (got !== want) begin
            errors++;
            if (errors <= 10) $display("MISMATCH a=%h b=%h got=%h want=%h", a, b, got, want);
        end
    endtask

    initial begin
        corners[0] = 16'h0000;  corners[1] = 16'h0001;  corners[2]  = 16'h00FF;  corners[3] = 16'h0100;
        corners[4] = 16'h5555;  corners[5] = 16'h7FFF;  corners[6]  = 16'h8000;  corners[7] = 16'hAAAA;
        corners[8] = 16'hFF00;  corners[9] = 16'hFFFE;  corners[10] = 16'hFFFF;
        // 1. every pair of corner values
        for (int i = 0; i < 11; i++)
            for (int j = 0; j < 11; j++) begin a = corners[i]; b = corners[j]; check(); end
        // 2. a full-length carry chain from every starting bit: a has 1s from bit s up, b = 1 << s
        for (int s = 0; s < 16; s++) begin a = 16'hFFFF << s; b = 16'h1 << s; check(); end
        // 3. every value of a against its complement plus one (the sum always carries out)
        for (int i = 0; i < 65536; i++) begin a = i; b = ~a + 16'd1; check(); end
        // 4. one million random pairs
        for (int i = 0; i < 1000000; i++) begin a = $urandom; b = $urandom; check(); end
        $display("checked %0d input pairs", checks);
        if (errors == 0) $display("RESULT: PASS (0 mismatches)");
        else             $display("RESULT: FAIL (%0d mismatches)", errors);
        $finish;
    end
endmodule
