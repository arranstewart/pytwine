use strict;
use warnings;

use Test::More;
use IPC::Open2;
use Data::Dumper;
use File::Temp qw/ tempfile tempdir /;

# use a BEGIN block so we print our plan before any modules loaded
BEGIN { plan tests => 1 }

ok( 0 == 0, "arithmetic seems to work");


