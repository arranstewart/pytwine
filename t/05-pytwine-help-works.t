use strict;
use warnings;

use Test::More;
use IPC::Open2;
use Data::Dumper;
use File::Temp qw/ tempfile tempdir /;

# use a BEGIN block so we print our plan before any modules loaded
BEGIN { plan tests => 2 }

sub  trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

my @res = `pytwine -h`;

ok( $? == 0, "pytwine -h works");

my $line = $res[0];
my $expected = "Usage: pytwine [options] [sourcefile [outfile]]";

ok( trim($line) eq $expected, "first line of help is as expected");

