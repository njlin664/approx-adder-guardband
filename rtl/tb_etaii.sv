// tb_etaii.sv - Day 19: self-checking testbench for ETAII-2 to ETAII-8.
// Run with:  python3 src/gen_etaii_vectors.py
//            iverilog -g2012 -o tb_etaii.vvp rtl/adders.v rtl/tb_etaii.sv  &&  vvp tb_etaii.vvp
`timescale 1ns/1ps
module tb_etaii;
    localparam int NVEC = 100000;             // must match NVEC in gen_etaii_vectors.py
    localparam int NDUT = 7;                  // ETAII-2 to ETAII-8
    localparam int W    = 32 + 17 * NDUT;     // bits per line of etaii_vectors.mem

    logic [W-1:0] mem [0:NVEC-1];
    logic [15:0]  a, b;
    wire  [16:0]  got [0:NDUT-1];
    logic [16:0]  want;
    int           errors = 0;

    genvar g;
    generate
        for (g = 0; g < NDUT; g = g + 1) begin : dut
            adder_etaii #(.K(g + 2)) u (.a(a), .b(b), .sum(got[g]));   // index 0 = ETAII-2
        end
    endgenerate

    initial begin
        $readmemh("etaii_vectors.mem", mem);
        for (int i = 0; i < NVEC; i++) begin
            a = mem[i][W-1  -: 16];
            b = mem[i][W-17 -: 16];
            #1;
            for (int d = 0; d < NDUT; d++) begin
                want = mem[i][17*d +: 17];
                if (got[d] !== want) begin
                    errors++;
                    if (errors <= 10)
                        $display("MISMATCH ETAII-%0d: a=%h b=%h got=%h want=%h", d + 2, a, b, got[d], want);
                end
            end
        end
        $display("checked %0d vectors x %0d designs", NVEC, NDUT);
        if (errors == 0) $display("RESULT: PASS (0 mismatches)");
        else             $display("RESULT: FAIL (%0d mismatches)", errors);
        $finish;
    end
endmodule
