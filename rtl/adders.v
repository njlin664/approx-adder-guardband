// adders.v - 16-bit accurate and approximate adders (synthesizable Verilog).
// Every adder takes 16-bit a and b and gives a 17-bit sum (bit 16 = carry-out).
// These must behave exactly like golden.py from Day 3.

// ---------- 1-bit full adder (ECE 210): adds a + b + cin ----------
module full_adder (
    input  a,
    input  b,
    input  cin,
    output sum,
    output cout
);
    wire p = a ^ b;                       // "propagate": a carry-in passes through
    assign sum  = p ^ cin;
    assign cout = (a & b) | (p & cin);    // generate a carry, or pass one along
endmodule

// ---------- N-bit ripple-carry adder: N full adders in a chain ----------
module rca #(parameter N = 16) (
    input  [N-1:0] a,
    input  [N-1:0] b,
    input          cin,
    output [N-1:0] sum,
    output         cout
);
`ifdef FAST
    // FAST build (Day 15): let the tool choose the adder structure. Yosys turns "+"
    // into a parallel-prefix adder, which is much faster than a ripple chain.
    assign {cout, sum} = a + b + cin;
`else
    wire [N:0] c;                         // c[i] = carry going INTO bit i
    assign c[0] = cin;
    genvar i;
    generate
        for (i = 0; i < N; i = i + 1) begin : stage
            full_adder fa (.a(a[i]), .b(b[i]), .cin(c[i]),
                           .sum(sum[i]), .cout(c[i+1]));
        end
    endgenerate
    assign cout = c[N];
`endif
endmodule

// ---------- Accurate adder: one 16-bit ripple-carry chain ----------
module adder_exact (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    rca #(.N(16)) u (.a(a), .b(b), .cin(1'b0), .sum(sum[15:0]), .cout(sum[16]));
endmodule

// ---------- Accurate adder, written the short way (the tool picks the gates) ----------
module adder_behav (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    assign sum = a + b;
endmodule

// ---------- TruA-K: ignore the low K bits, add the rest (K = 1 to 15) ----------
module adder_trua #(parameter K = 4) (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    assign sum[K-1:0] = {K{1'b0}};        // low K outputs are always 0
    rca #(.N(16-K)) u (.a(a[15:K]), .b(b[15:K]), .cin(1'b0),
                       .sum(sum[15:K]), .cout(sum[16]));
endmodule

// ---------- LOA-K: OR the low K bits, add the rest (K = 1 to 15) ----------
module adder_loa #(parameter K = 4) (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    assign sum[K-1:0] = a[K-1:0] | b[K-1:0];   // no carries in the low part
    wire cin = a[K-1] & b[K-1];                // one guessed carry into the high part
    rca #(.N(16-K)) u (.a(a[15:K]), .b(b[15:K]), .cin(cin),
                       .sum(sum[15:K]), .cout(sum[16]));
endmodule

// ---------- ESA-S: separate S-bit adders, carries between them dropped ----------
// Segments start at bit 0. If S does not divide 16 the TOP segment is shorter.
// The top segment keeps its carry-out as sum[16].
module adder_esa #(parameter S = 8) (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    localparam NSEG = (16 + S - 1) / S;        // number of segments (rounded up)
    genvar g;
    generate
        for (g = 0; g < NSEG; g = g + 1) begin : seg
            localparam LO = g * S;                           // lowest bit of segment
            localparam W  = (LO + S <= 16) ? S : (16 - LO);  // its width
            wire co;
            rca #(.N(W)) u (.a(a[LO+W-1:LO]), .b(b[LO+W-1:LO]), .cin(1'b0),
                            .sum(sum[LO+W-1:LO]), .cout(co));
            if (g == NSEG - 1) begin : top
                assign sum[16] = co;           // only the top carry is kept
            end
        end
    endgenerate
endmodule

// ---------- Carry-lookahead adder (CLA), built from ECE 210 generate/propagate logic ----------
// Each bit: g = a & b (this bit MAKES a carry), p = a ^ b (this bit PASSES a carry on).
// A ripple adder waits for each carry in turn. A CLA writes every carry as a formula of the
// g's, p's and the carry-in, so all carries are computed side by side instead of one by one.

// 4-bit CLA block: its own 4 carries come straight from the formulas (no rippling inside),
// and it reports a group generate G and group propagate P for the next level up.
module cla4 (
    input  [3:0] a,
    input  [3:0] b,
    input        cin,
    output [3:0] sum,
    output       G,                       // this block makes a carry out by itself
    output       P                        // this block passes a carry-in straight through
);
    wire [3:0] g = a & b;
    wire [3:0] p = a ^ b;
    wire c1 = g[0] | (p[0] & cin);
    wire c2 = g[1] | (p[1] & g[0]) | (p[1] & p[0] & cin);
    wire c3 = g[2] | (p[2] & g[1]) | (p[2] & p[1] & g[0]) | (p[2] & p[1] & p[0] & cin);
    assign sum = p ^ {c3, c2, c1, cin};
    assign G = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1]) | (p[3] & p[2] & p[1] & g[0]);
    assign P = &p;                        // all four bits propagate
endmodule

// 16-bit two-level CLA: four 4-bit blocks, plus a lookahead carry unit that computes the
// carry into every block at once from the blocks' G and P signals.
module adder_cla (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    wire [3:0] G, P;
    wire c4, c8, c12;
    assign c4  = G[0];
    assign c8  = G[1] | (P[1] & G[0]);
    assign c12 = G[2] | (P[2] & G[1]) | (P[2] & P[1] & G[0]);
    assign sum[16] = G[3] | (P[3] & G[2]) | (P[3] & P[2] & G[1]) | (P[3] & P[2] & P[1] & G[0]);
    cla4 b0 (.a(a[3:0]),   .b(b[3:0]),   .cin(1'b0), .sum(sum[3:0]),   .G(G[0]), .P(P[0]));
    cla4 b1 (.a(a[7:4]),   .b(b[7:4]),   .cin(c4),   .sum(sum[7:4]),   .G(G[1]), .P(P[1]));
    cla4 b2 (.a(a[11:8]),  .b(b[11:8]),  .cin(c8),   .sum(sum[11:8]),  .G(G[2]), .P(P[2]));
    cla4 b3 (.a(a[15:12]), .b(b[15:12]), .cin(c12),  .sum(sum[15:12]), .G(G[3]), .P(P[3]));
endmodule

// ---------- ETAII-K: error-tolerant adder type II (Day 19) ----------
// K-bit blocks lined up with the TOP of the adder; if K does not divide 16 the BOTTOM
// block is the short one. Each block adds on its own. Its carry-in comes from a small
// "carry generator": the block below added again with NO carry-in, keeping only its
// carry-out. So no carry ever travels more than two blocks, and the slowest path is
// about 2K bits long instead of 16.
module adder_etaii #(parameter K = 6) (
    input  [15:0] a,
    input  [15:0] b,
    output [16:0] sum
);
    localparam NB = (16 + K - 1) / K;                  // number of blocks (rounded up)
    genvar j;
    generate
        for (j = 0; j < NB; j = j + 1) begin : blk     // j = 0 is the lowest block
            localparam HI = 16 - (NB - 1 - j) * K;     // one above this block's top bit
            localparam LO = (HI > K) ? HI - K : 0;
            localparam W  = HI - LO;
            wire cin, co;
            if (j == 0) begin : first
                assign cin = 1'b0;                     // nothing below the lowest block
            end else begin : predicted
                localparam PLO = (LO > K) ? LO - K : 0;       // the block below
                localparam PW  = LO - PLO;
                wire [PW-1:0] unused;
                rca #(.N(PW)) gen (.a(a[LO-1:PLO]), .b(b[LO-1:PLO]), .cin(1'b0),
                                   .sum(unused), .cout(cin));  // carry generator
            end
            rca #(.N(W)) u (.a(a[HI-1:LO]), .b(b[HI-1:LO]), .cin(cin),
                            .sum(sum[HI-1:LO]), .cout(co));    // sum generator
            if (j == NB - 1) begin : top
                assign sum[16] = co;                   // only the top block keeps its carry
            end
        end
    endgenerate
endmodule
