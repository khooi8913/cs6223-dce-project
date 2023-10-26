#include <core.p4>
bit<3> max(in bit<3> val, in bit<3> bound) {
    return val < bound ? val : bound;
}
header ethernet_t {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16> eth_type;
}

header RwJPBL {
    bit<4>   BfFn;
    bit<8>   nMdb;
    bit<128> ljIi;
    bit<128> ynLf;
    bit<4>   nvvS;
}

header FlwwUH {
    bit<64> Fpqs;
    bit<32> EbmS;
}

struct LNuSxT {
    bit<64> Ykpi;
}

struct eXWvsv {
    bit<8> OhGU;
}

header MZRHtq {
    bit<16> DmXs;
}

struct Headers {
    ethernet_t eth_hdr;
    FlwwUH     aCNn;
    MZRHtq     cwBK;
}

extern void CvPiMoV();
parser p(packet_in pkt, out Headers hdr) {
    bit<4> VmDFqB = (!!!((251w1901886541806969990905967134675537698051075762013083238608792611523355009773 % 251w1905049113407781947841527145189598694778581195998714200296082503176686870459)[227:102] != -837616430 - -1465253727) ? (bit<4>)4w14 : 4w12);
    bool OJFify = false;
    bit<4> JVMcAX = (3w5 >> (bit<8>)(bit<3>)hdr.aCNn.Fpqs) ++ (bit<1>)hdr.eth_hdr.dst_addr;
    bit<32> NjISaa = hdr.aCNn.EbmS;
    bit<16> igHOBW = 16w39361;
    state start {
        transition parse_hdrs;
    }
    state parse_hdrs {
        pkt.extract(hdr.eth_hdr);
        pkt.extract(hdr.aCNn);
        pkt.extract(hdr.cwBK);
        transition accept;
    }
}

control ingress(inout Headers h) {
    bit<8> JSsIyH = 8w254;
    bit<32> GxmqFC = h.aCNn.EbmS;
    Headers sGJhUt = h;
    bit<64> PQKKLS = 64w8096013252997128812;
    bit<8> XTgAcF = JSsIyH;
    action rSQTV(in bit<4> VNgb, bit<32> lbjD) {
        sGJhUt.aCNn.EbmS = (32w844238795 << (bit<8>)32w3681171815) |+| 48w234805297830075[40:9] | 32w1357188782;
        sGJhUt.eth_hdr.eth_type = 16w33499;
        GxmqFC = ((bit<66>)-1515615021)[33:2];
        bit<16> jBGOyi = 1394121477;
        sGJhUt.aCNn.Fpqs = -1792003072;
        const bit<32> hAJzfl = -32w3600235191;
        bit<32> bAXHbo = hAJzfl;
        sGJhUt.aCNn.Fpqs = 64w4407859815097528802;
        h.aCNn.Fpqs = (true ? ((bit<79>)(79w480162780593943178072368 - 79w602411100412280467826560))[67:4] | 64w5250972434168239058 : h.aCNn.Fpqs);
        XTgAcF = XTgAcF;
        bit<128> MhHbOf = 128w230133696442013971445255241645737001541;
    }
    table xJUENL {
        key = {
            48w215902884470979 | sGJhUt.eth_hdr.dst_addr                  : exact @name("OvOjvt");
            (69w106848631516695496666 |+| 69w366925682138574990206)[54:23]: exact @name("plOvDv");
            (true || !true ? JSsIyH : 8w149)                              : exact @name("TdQQEo");
        }
        actions = {
        }
    }
    apply {
        bit<4> FhhVLn = 4w5;
        if (false) {
            PQKKLS = sGJhUt.aCNn.Fpqs;
        } else {
            XTgAcF = XTgAcF;
        }
        h.eth_hdr.dst_addr = h.eth_hdr.src_addr;
        const bit<8> rlEqiJ = 8w123;
    }
}

parser Parser(packet_in b, out Headers hdr);
control Ingress(inout Headers hdr);
package top(Parser p, Ingress ig);
top(p(), ingress()) main;