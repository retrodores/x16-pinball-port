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
run('direct/build/check-build.log','sh','direct/build.sh');
for my $ram (512,2048) {
 local $ENV{X16_RAM_KB}=$ram;
 for my $probe (qw(math world)) {
  my $log="direct/build/$probe-x16-$ram.tap";
  run($log,$^X,'t/run_x16.pl',"direct/build/$probe.prg",'direct/build');
  my $native=contents($log);
  ok($native!~/^not ok/m && $native=~/^1\.\./m,"$probe completes on $ram KB");
  if($probe eq 'math'){
   my @host=contents('direct/build/math-host.tap')=~/^# RESULT (.+)$/mg;
   my @target=$native=~/^# RESULT (.+)$/mg;
   is(scalar @target,256,"256 original-math comparison cases on $ram KB");
   for my $i(0..$#host){
    my @h=split / /,$host[$i];my @t=split / /,$target[$i]//'';
    my $ok=@h==@t && shift(@h) eq shift(@t);
    for my $v(@h){
     my $a=unpack('f>',pack('H*',$v));my $b=unpack('f>',pack('H*',shift(@t)//'7fc00000'));
     $ok=0 unless abs($a-$b)<=2e-5*(1+abs($a));
    }
    ok($ok,"original method result $i on $ram KB");
   }
  } else {
   my @rows=$native=~/^# WORLD (.+)$/mg;
   is(scalar @rows,30,"four-second world trace on $ram KB");
   my @last=split / /,$rows[20]//'';
   my $x=unpack('f>',pack('H*',$last[1]//'7fc00000'));
   my $y=unpack('f>',pack('H*',$last[2]//'7fc00000'));
   ok($x>4 && $y> -8 && $y< -5,"launch clears chute and reaches table on $ram KB");
   my ($cycles)=$native=~/^# MAX_FRAME_CYCLES (\w+)/m;
   diag("maximum diagnostic physics frame: ".hex($cycles)." cycles; gameplay budget remains 133333");
   if($ram==2048){
    my @small=contents('direct/build/world-x16-512.tap')=~/^# WORLD (.+)$/mg;
    is_deeply(\@rows,\@small,'world trajectory identical across RAM sizes');
   }
  }
 }
}
done_testing();
