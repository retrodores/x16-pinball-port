#!/usr/bin/env perl
use strict;
use warnings;
use Math::BigInt;
sub b { Math::BigInt->new($_[0]) }
my $max=b(2)->bpow(128)->bdec;
my @pairs=([0,0],[65535,1],[999999999,1],[2147483647,1],[4294967295,1],['18446744073709551615',1],[b(2)->bpow(127)->bdec->bstr,1],[$max->bstr,0],[$max->bstr,1],[$max->copy->bsub(100)->bstr,100],[$max->copy->bsub(100)->bstr,101]);
for my $n(1..15){push @pairs,[b(2)->bpow(8*$n)->bdec->bstr,1]}
srand 48271;
for(1..12){
 my $a=b(0);my $c=b(0);
 for(1..16){$a->blsft(8)->badd(int rand 256);$c->blsft(8)->badd(int rand 256)}
 push @pairs,[$a->bstr,$c->bstr];
}
sub encoded {
 my $n=b(shift);my $s='';
 for(1..16){$s.=sprintf '\\x%02x',$n->copy->band(255)->numify;$n->brsft(8)}
 return '"'.$s.'"';
}
open my $out,'>','t/score_vectors.p8' or die $!;
print {$out} <<'P8';
%encoding iso
%import score
%import storage
%import syslib
%import strings
%import tap
main {
    sub check(str lhs,str rhs,str expected,str decimal,bool overflow) {
        ubyte i
        bool same=true
        sys.memcopy(lhs,&score.total,16)
        sys.memcopy(rhs,&score.award,16)
        score.saturated=false
        score.add()
        for i in 0 to 15 {
            if score.total[i]!=expected[i] { same=false }
        }
        tap.ok(same and score.saturated==overflow,"128-bit sum and saturation")
        score.format()
        tap.ok(strings.compare(score.text,decimal)==0,"full decimal representation")
    }
    sub start() {
P8
for my $pair(@pairs){
 my ($a,$c)=@$pair;my $sum=b($a)->badd($c);my $overflow=$sum->bcmp($max)>0;
 $sum=$max->copy if $overflow;
 my $dec=$sum->bstr;$dec=('0'x(40-length($dec))).$dec;
 print {$out} '        check('.encoded($a).','.encoded($c).','.encoded($sum->bstr).',"'.$dec.'",'.($overflow?'true':'false').")\n";
}
print {$out} <<'P8';
        score.clear()
        score.add16(65535)
        score.add16(1)
        tap.ok(score.total[2]==1 and score.total[1]==0 and score.total[0]==0,"native add16 promotes past word limit")
        storage.observe()
        storage.save()
        tap.ok(not storage.failed and not storage.changed,"versioned high-score save succeeds")
        score.clear()
        sys.memset(&storage.best,16,0)
        storage.load()
        tap.ok(storage.best[2]==1 and storage.best[0]==0,"high-score load restores above 65535")
        sys.memset(&score.total,16,255)
        storage.observe()
        storage.save()
        sys.memset(&storage.best,16,0)
        storage.load()
        bool full=true
        ubyte i
        for i in 0 to 15 { if storage.best[i]!=255 { full=false } }
        tap.ok(full,"all 128 bits survive save/load")
        score.clear()
        tap.ok(not score.greater(&storage.best),"full-width comparison checks high bytes")
        tap.done()
    }
}
P8
print scalar(@pairs)," score vectors generated\n";
