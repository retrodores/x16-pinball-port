#!/usr/bin/env perl
use strict;
use warnings;
use Test::More;
my $file=shift // 'direct/build/world-x16-512.tap';
open my $fh,'<',$file or die "$file: $!";
local $/;my $text=<$fh>;
my ($hex)=$text=~/^# MAX_FRAME_CYCLES (\w+)/m;
die "Missing frame measurement\n" unless defined $hex;
cmp_ok(hex($hex),'<=',133333,'native world physics fits the 8 MHz 60 Hz gameplay budget');
diag('This release gate intentionally fails for the unoptimized direct baseline.');
done_testing();
