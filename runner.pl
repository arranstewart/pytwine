#!/usr/bin/env perl

# Execute 1st arg with perl or python, depending on
# extension (.t, .py or .pl).
# Should work perfectly well on non-windows platforms
# as well, but isn't needed there as they can
# use the shebang line.
use strict;
use warnings;
use File::Basename;
use File::Which;
use Carp::Assert;

my $windows=($^O=~/Win/)?1:0;
assert $windows, "running on windows";

my $script = $ARGV[0];
($_,$_,my $suffix) = fileparse($script, qw(t py pl));

my @args;
if ($suffix eq "py") {
  my $python3 = which "python3";
  @args = ($python3, $script);
} elsif ($suffix eq "t" || $suffix eq "pl") {
  my $perl = which "perl";
  shift @ARGV;
  # see perl --help.
  # arguments are `perl [switches] [--] [programfile] [arguments]`
  @args = ($perl, "--", $script, @ARGV);
} else {
  die "unrecognized suffix $suffix for file $script - couldn't work out interpreter";
}
warn "bout to exec @args";
exec { $args[0] } @args;
