#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
use TAP::Parser;
use File::Temp qw(tempdir);
use File::Copy qw(copy);
use Cwd qw(abs_path);
use POSIX qw(setpgid);
sub capture {
    my ($log,@command)=@_;
    my $pid=fork();die $! unless defined $pid;
    if(!$pid) {
        setpgid(0,0);
        open STDOUT,'>',$log or die $!;
        open STDERR,'>&',\*STDOUT or die $!;
        exec {$command[0]} @command;
        die "exec: $!";
    }
    my $status;
    eval {local $SIG{ALRM}=sub {die "compile timeout\n"};alarm 60;waitpid($pid,0);$status=$?;alarm 0;1}
      or do {kill 'KILL',-$pid;waitpid($pid,0);die $@};
    open my $fh,'<',$log or die $!;local $/;return ($status,<$fh>);
}
for my $source(qw(score_vectors physics_test frame_budget integration_test features02_test)) {
    subtest $source => sub {
        my $temp=tempdir(CLEANUP=>1);
        my @compiler=$ENV{JAR} ? ('java','-jar',$ENV{JAR}) : ($ENV{PROG8C}//'prog8c');
        my ($status,$log)=capture("$temp/compile.log",@compiler,'-target','cx16','-srcdirs','src','-srcdirs','t','-out',$temp,"t/$source.p8");
        if($status) {diag($log);BAIL_OUT("native compilation failed")}
        mkdir "$temp/fs" or die $!;
        for my $file(glob 'assets/*') {
            (my $name=$file)=~s{.*/}{};
            copy($file,"$temp/fs/$name") or die $!;
        }
        ($status,$log)=capture("$temp/run.log",$^X,'t/run_x16.pl',"$temp/$source.prg","$temp/fs");
        if($status) {diag($log);BAIL_OUT("native execution failed")}
        my $parser=TAP::Parser->new({tap=>$log});
        while(my $result=$parser->next) {
            if($result->is_test) {ok($result->is_ok,$result->description)}
            elsif($result->is_comment) {diag($result->as_string)}
        }
        ok(!$parser->has_problems,'native TAP plan and process completed');
        done_testing();
    };
}
done_testing();
