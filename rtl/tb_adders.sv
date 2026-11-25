// tb_adders.sv - self-checking testbench for all 33 adders.
// Reads vectors.mem (made by gen_vectors.py), drives every adder with each
// input pair, and compares each output with the answer golden.py predicted.
`timescale 1ns/1ps
module tb_adders;
    localparam int NVEC = 100000;             // must match NVEC in gen_vectors.py
    localparam int NDUT = 32;                 // designs with their own golden answer
    localparam int W    = 32 + 17 * NDUT;     // bits per line of vectors.mem

    logic [W-1:0]  mem [0:NVEC-1];            // the whole vector file, in memory
    logic [15:0]   a, b;
    wire  [16:0]   got [0:NDUT-1];            // what each design answered
    wire  [16:0]   got_behav;
    logic [16:0]   want;
    logic [15:0]   p;
    int            errors, run, best;
    int            hist [0:16];               // coverage: longest propagate run seen
    int            fd, bit_i;
    string         fname;

    // ---- the designs under test (same index order as gen_vectors.py) ----
    adder_exact u_exact (.a(a), .b(b), .sum(got[0]));
    adder_behav u_behav (.a(a), .b(b), .sum(got_behav));
    genvar g;
    generate
        for (g = 1; g <= 12; g = g + 1) begin : g_trua
            adder_trua #(.K(g)) u (.a(a), .b(b), .sum(got[g]));        // index 1-12
        end
        for (g = 1; g <= 12; g = g + 1) begin : g_loa
            adder_loa #(.K(g)) u (.a(a), .b(b), .sum(got[12 + g]));    // index 13-24
        end
        for (g = 2; g <= 8; g = g + 1) begin : g_esa
            adder_esa #(.S(g)) u (.a(a), .b(b), .sum(got[23 + g]));    // index 25-31
        end
    endgenerate

    initial begin
        // Find the vector file: current folder first, then the Windows copy.
        fname = "vectors.mem";
        fd = $fopen(fname, "r");
        if (fd == 0) begin
            fname = "C:/Users/Public/adder_sim/vectors.mem";
            fd = $fopen(fname, "r");
        end
        if (fd == 0) begin
            $display("ERROR: cannot find vectors.mem. Run gen_vectors.py first.");
            $finish;
        end
        $fclose(fd);
        $readmemh(fname, mem);

        errors = 0;
        for (int h = 0; h <= 16; h++) hist[h] = 0;

        for (int i = 0; i < NVEC; i++) begin
            a = mem[i][W-1  -: 16];
            b = mem[i][W-17 -: 16];
            #1;                                        // let the outputs settle

            for (int d = 0; d < NDUT; d++) begin
                want = mem[i][17*d +: 17];
                if (got[d] !== want) begin
                    errors++;
                    if (errors <= 10)
                        $display("MISMATCH design %0d: a=%h b=%h got=%h want=%h",
                                 d, a, b, got[d], want);
                end
            end
            want = mem[i][0 +: 17];                    // behavioral adder = exact answer
            if (got_behav !== want) begin
                errors++;
                if (errors <= 10)
                    $display("MISMATCH behav: a=%h b=%h got=%h want=%h", a, b, got_behav, want);
            end

            // coverage: longest run of consecutive propagate bits (a XOR b = 1)
            p = a ^ b;  run = 0;  best = 0;
            for (bit_i = 0; bit_i < 16; bit_i++) begin
                if (p[bit_i]) run++; else run = 0;
                if (run > best) best = run;
            end
            hist[best]++;
        end

        $display("---- coverage: longest propagate run in each vector ----");
        for (int h = 0; h <= 16; h++) begin
            if (hist[h] == 0) $display("  run %2d : NEVER TESTED", h);
            else              $display("  run %2d : %6d vectors", h, hist[h]);
        end
        $display("checked %0d vectors x %0d designs", NVEC, NDUT + 1);
        if (errors == 0) $display("RESULT: PASS (0 mismatches)");
        else             $display("RESULT: FAIL (%0d mismatches)", errors);
        $finish;
    end
endmodule
