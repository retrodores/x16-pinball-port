#!/usr/bin/env perl
use strict;
use warnings;
use File::Temp qw(tempdir);
use File::Spec;
use POSIX qw(setpgid);
my ($prg,$fs)=@ARGV;
die "usage: $0 file.prg [filesystem]\n" unless $prg;
my $temp=tempdir(CLEANUP=>1);
$fs //= "$temp/fs";
mkdir $fs unless -d $fs;
open my $in,'<:raw',$prg or die "$prg: $!";
local $/; my $bytes=<$in>;
my $base=unpack('v',substr($bytes,0,2));
my ($entry)=$bytes=~/\x9e\s*(\d+)/;
die "invalid PRG launcher\n" unless $entry && $base==0x801 && length($bytes)+$base-2 < 0x9f00;
open my $cmd,'>',"$temp/commands" or die $!;
for my $i(2..length($bytes)-1) { printf {$cmd} "STM %04X %02X\n",$base+$i-2,ord(substr($bytes,$i,1)) }
printf {$cmd} "RUN %04X\n",$entry;
close $cmd;
my $pid=fork();die $! unless defined $pid;
if(!$pid) {
 setpgid(0,0);
 open STDIN,'<',"$temp/commands" or die $!;
 open STDOUT,'>',"$temp/output" or die $!;
 open STDERR,'>&',\*STDOUT or die $!;
 $ENV{SDL_VIDEODRIVER}='dummy';$ENV{SDL_AUDIODRIVER}='dummy';
 my @args=($ENV{X16EMU}//'/opt/x16emu-r49/x16emu','-rom',$ENV{X16ROM}//'/opt/x16emu-r49/rom.bin','-testbench','-echo','raw','-sound','none','-warp','-mhz','8','-fsroot',File::Spec->rel2abs($fs),'-ram',$ENV{X16_RAM_KB}//512);
 exec {$args[0]} @args;die "exec: $!";
}
my $status;
eval {
 local $SIG{ALRM}=sub {die "emulator timeout\n"};alarm 45;
 waitpid($pid,0);$status=$?;alarm 0;1
} or do {kill 'KILL',-$pid;waitpid($pid,0);die $@};
open my $out,'<',"$temp/output" or die $!;my $output=<$out>;
$output=~s/\r\n?/\n/g;
my ($tap)=$output=~/# TAP BEGIN\n(.*)/s;
unless(defined $tap) {print $output;die "no native TAP marker\n"}
$tap=~s/^RDY\n//mg;
for my $line(split /\n/,$tap) {
 print "$line\n" if $line =~ /^(?:(?:not )?ok\b|1\.\.\d+|#|Bail out!)/;
}
die "native test process failed\n" if $status || $tap!~/^1\.\.\d+$/m;
