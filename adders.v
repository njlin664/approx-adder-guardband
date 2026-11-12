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
