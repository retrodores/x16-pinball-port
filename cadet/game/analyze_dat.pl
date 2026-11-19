#!/usr/bin/env perl
use strict;
use warnings;
use JSON::PP;
use Digest::SHA qw(sha256_hex);
use File::Path qw(make_path);

# PARTOUT(4.0) inventory, based on the documented structures in
# k4zmu2a/SpaceCadetPinball (MIT). No executable code is run.
my ($input, $output) = @ARGV;
die "usage: $0 PINBALL.DAT output-dir\n" unless defined $output;
make_path($output);
open my $fh, '<:raw', $input or die "$input: $!";
local $/;
my $data = <$fh>;
my $offset = 0;
sub take {
    my ($n) = @_;
    die "truncated record at $offset, length $n\n" if $n < 0 || $offset + $n > length $data;
    my $bytes = substr($data, $offset, $n);
    $offset += $n;
    return $bytes;
}
sub cstr { my $s = shift; $s =~ s/\0.*//s; return $s }
my ($sig, $app, $desc, $size, $count, $body, $extra) = unpack 'a21a50a100VvVv', take(183);
die "not a PARTOUT 4.0 resource\n" unless cstr($sig) eq 'PARTOUT(4.0)RESOURCE';
take($extra);
my @fixed = (2, -1, 2, (-1) x 10);
my (@groups, %types, %bytes, @bitmaps, @zmaps);
for my $g (0 .. $count - 1) {
    my $entries = unpack 'C', take(1);
    my $group = { id => $g, name => '', entries => [] };
    for (1 .. $entries) {
        my $type = unpack 'C', take(1);
        die "unknown type $type\n" if $type > 12;
        my $n = $fixed[$type] >= 0 ? $fixed[$type] : unpack 'V', take(4);
        my $start = $offset;
        my $raw = take($n);
        $types{$type}++;
        $bytes{$type} += $n;
        my $entry = { type => $type, offset => $start, bytes => $n };
        if ($type == 3 || $type == 9) {
            $entry->{text} = cstr($raw);
            $group->{name} = $entry->{text} if $type == 3;
        } elsif ($type == 0 || $type == 2 || $type == 10) {
            die "unaligned short array\n" if $n % 2;
            $entry->{values} = [unpack 's<*', $raw];
        } elsif ($type == 11) {
            die "unaligned float array\n" if $n % 4;
            $entry->{values} = [unpack 'f<*', $raw];
        } elsif ($type == 1) {
            die "short bitmap header\n" if $n < 14;
            my ($res,$w,$h,$x,$y,$len,$flags) = unpack 'Cs<s<s<s<VC', $raw;
            die "bitmap payload mismatch\n" if $len + 14 != $n;
            my $bmp = {group=>$g,resolution=>$res,width=>$w,height=>$h,x=>$x,y=>$y,payload=>$len,flags=>$flags,offset=>$start+14};
            push @bitmaps, $bmp;
            $entry->{bitmap} = $bmp;
        } elsif ($type == 12) {
            my ($w,$h,$stride) = unpack 's<s<s<', $raw;
            push @zmaps, {group=>$g,width=>$w,height=>$h,stride=>$stride,bytes=>$n};
        }
        push @{$group->{entries}}, $entry;
    }
    push @groups, $group;
}
die "unexpected trailing bytes: " . (length($data)-$offset) . "\n" unless $offset == length $data;
my $summary = {signature=>cstr($sig),app=>cstr($app),description=>cstr($desc),file_bytes=>length($data),header_file_size=>$size,header_body_size=>$body,sha256=>sha256_hex($data),group_count=>$count,field_counts=>\%types,field_bytes=>\%bytes,bitmaps=>\@bitmaps,zmaps=>\@zmaps,groups=>\@groups,parsed_bytes=>$offset};
open my $out, '>:raw', "$output/inventory.json" or die $!;
print {$out} JSON::PP->new->canonical->pretty->encode($summary);
close $out or die $!;
printf "Parsed %d groups, %d bitmaps, %d depth maps; %d/%d bytes consumed\n", $count, scalar(@bitmaps),scalar(@zmaps),$offset,length($data);
printf "type %2d: %4d fields, %7d bytes\n", $_,$types{$_},$bytes{$_} for sort {$a<=>$b} keys %types;
for my $group (@groups) {
    next unless $group->{name} =~ /^(table|ball|flipper|ramp)/i;
    printf "group %3d %-25s: %d fields\n",$group->{id},$group->{name},scalar @{$group->{entries}};
}
