#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
my @files=@ARGV ? @ARGV : ('direct/build/world-x16-512.tap','direct/build/mechanisms-x16-512.tap');
for my $file (@files) {
open my $fh,'<',$file or die "$file: $!";
local $/;my $text=<$fh>;
my ($hex)=$text=~/^# MAX_(?:FRAME|MECHANISMS)_CYCLES (\w+)/m;
die "Missing frame measurement\n" unless defined $hex;
cmp_ok(hex($hex),'<=',133333,"$file fits the 8 MHz 60 Hz gameplay budget");
}
diag('Diagnostic checkpoints may exceed this bound; gameplay releases may not.');
done_testing();
