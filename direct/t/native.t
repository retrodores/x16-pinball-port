#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
sub contents {open my $fh,'<',$_[0] or die "$_[0]: $!";local $/;return <$fh>}
sub run {
 my ($log,@cmd)=@_;
 my $pid=fork();die $! unless defined $pid;
 if(!$pid){open STDOUT,'>',$log or die $!;open STDERR,'>&',\*STDOUT or die $!;exec {$cmd[0]} @cmd;die $!}
 local $SIG{ALRM}=sub{kill 'TERM',$pid;die "process timed out\n"};alarm 120;
 waitpid($pid,0);alarm 0;my $status=$?;
 if($status){diag(contents($log));BAIL_OUT("command failed")}
}
sub compare_rows {
 my ($probe,$kind,$native,$ram,$count)=@_;
 my @host=contents("direct/build/$probe-host.tap")=~/^# \Q$kind\E (.+)$/mg;
 my @target=$native=~/^# \Q$kind\E (.+)$/mg;
 is(scalar @target,$count,"$count $probe comparison cases on $ram KB");
 for my $i(0..$#host){
  my @h=split / /,$host[$i];my @t=split / /,$target[$i]//'';
  my $ok=@h==@t && shift(@h) eq shift(@t);
  for my $v(@h){
   my $a=unpack('f>',pack('H*',$v));my $b=unpack('f>',pack('H*',shift(@t)//'7fc00000'));
   $ok=0 unless abs($a-$b)<=2e-5*(1+abs($a));
  }
  ok($ok,"original $probe result $i on $ram KB");
  diag("host $host[$i]\nnative ".($target[$i]//'')) unless $ok;
 }
}
run('direct/build/check-build.log','sh','direct/build.sh');
for my $ram (512,2048) {
 local $ENV{X16_RAM_KB}=$ram;
 for my $probe (qw(math world reference flipper mechanisms plunger)) {
  my $log="direct/build/$probe-x16-$ram.tap";
  run($log,$^X,'t/run_x16.pl',"direct/build/$probe.prg",'direct/build');
  my $native=contents($log);
  ok($native!~/^not ok/m && $native=~/^1\.\./m,"$probe completes on $ram KB");
  diag($native) if $native=~/^not ok/m;
  if($probe eq 'math'){compare_rows($probe,'RESULT',$native,$ram,256)}
  elsif($probe eq 'flipper'){
   compare_rows($probe,'FLIPPER',$native,$ram,96);
   like($native,qr/^# CONTACTS 00000028$/m,"40 flipper contacts, including 16 stationary-ball strikes, on $ram KB");
  } elsif($probe eq 'world') {
   my @rows=$native=~/^# WORLD (.+)$/mg;
   is(scalar @rows,240,"every frame of four-second world trace on $ram KB");
   my @last=split / /,$rows[160]//'';
   my $x=unpack('f>',pack('H*',$last[1]//'7fc00000'));
   my $y=unpack('f>',pack('H*',$last[2]//'7fc00000'));
   ok($x>4 && $y> -8 && $y< -5,"launch clears chute and reaches table on $ram KB");
   my ($cycles)=$native=~/^# MAX_FRAME_CYCLES (\w+)/m;
   diag("maximum baseline-world diagnostic frame: ".hex($cycles)." cycles; gameplay budget remains 133333");
  } elsif($probe eq 'reference') {
   my @reference=$native=~/^# WORLD (.+)$/mg;
   my @optimized=contents("direct/build/world-x16-$ram.tap")=~/^# WORLD (.+)$/mg;
   is_deeply(\@optimized,\@reference,"optimized world bit-identical to retained baseline at every frame on $ram KB");
   my ($old)=$native=~/^# MAX_FRAME_CYCLES (\w+)/m;
   my ($new)=contents("direct/build/world-x16-$ram.tap")=~/^# MAX_FRAME_CYCLES (\w+)/m;
   cmp_ok(hex($new),'<',hex($old)/2,"collision filtering more than halves measured worst frame on $ram KB");
  } elsif($probe eq 'mechanisms') {
   my ($cycles)=$native=~/^# MAX_MECHANISMS_CYCLES (\w+)/m;
   diag("maximum integrated-mechanisms diagnostic frame: ".hex($cycles)." cycles; gameplay budget remains 133333");
  }
  if($ram==2048){
   my @small=contents("direct/build/$probe-x16-512.tap")=~/^# (?:WORLD|RESULT|FLIPPER|MECHANISMS) (.+)$/mg;
   my @large=$native=~/^# (?:WORLD|RESULT|FLIPPER|MECHANISMS) (.+)$/mg;
   is_deeply(\@large,\@small,"$probe results identical across RAM sizes");
  }
 }
}
done_testing();
