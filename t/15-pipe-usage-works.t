#!/usr/bin/env perl

use strict;
use warnings;

use File::Basename;
use Test::More;
use IPC::Open2;
use Data::Dumper;
use File::Temp qw/ tempfile tempdir /;
use Carp::Assert;

use constant DEBUG => 0;

assert( $ARGV[0] eq "--source-dir", "argv[0] has been passed" );
my $source_dir = $ARGV[1];
my @testfiles = glob "${source_dir}/tests/files/*.pmd";

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

# Are we running on windows?
my $windows=($^O=~/Win/)?1:0;

my $devnull="/dev/null";
if ($windows) {
  $devnull = "nul";
}

sub slurp {
  my $infile = shift;
  open my $fh, '<', $infile or die "Can't open file $!";
  my $conts = do { local $/; <$fh> };
  return $conts;
}

# args: filepath, string
sub dump_to_file {
  my $outpath = shift;
  my $contents = shift;
  open(my $fh, ">", "$outpath")
             or die "Can't open > output.txt: $!";
  print $fh $contents;
  close($fh);
}



# args: one filename to be tested for standard-in-ness
sub twine_from_stdinlike {
  my $filename  = shift;
  my $dir       = tempdir("pytwine-tmp-XXXXXXXXXX", CLEANUP => 1, TMPDIR => 1 );
  my $input     = "foo";

  # run twine
  my $cmd = "|pytwine $filename >$dir/output.txt";
  DEBUG and print STDERR "running cmd: '$cmd'\n";
  open ToTemp, "$cmd"
          or die "run twine: $!";
  print ToTemp $input;
  close ToTemp;

  assert( -f "$dir/output.txt", "output file $dir/output.txt should now exist");

  my $actual_output = slurp("$dir/output.txt");

  is($actual_output, $input, "should get out == in w/ cli args: input file '$filename'");
}

# args: one filename to be tested for standard-out-ness
sub twine_to_stdoutlike {
  my $outpath   = shift;
  my $dir       = tempdir("pytwine-tmp-XXXXXXXXXX", CLEANUP => 1, TMPDIR => 1 );
  my $input     = "foo";

  # run twine
  my $cmd = "|pytwine - $outpath > $dir/output.txt";
  DEBUG and print STDERR "running cmd: '$cmd'\n";
  open ToTemp, "$cmd"
          or die "run twine: $!";
  print ToTemp $input;
  close ToTemp;

  assert( -f "$dir/output.txt", "output file $dir/output.txt should now exist");
  my $actual_output = slurp("$dir/output.txt");

  is($actual_output, $input, "should get out == in w/ cli args: output file '$outpath'");
}

# args: a normal infile path and outfile path
sub twine_inout_filenames {
  my $inpath    = shift;
  my $outpath   = shift;
  my $dir       = tempdir("pytwine-tmp-XXXXXXXXXX", CLEANUP => 1, TMPDIR => 1 );
  my $input_txt = "foo";

  # run twine
  dump_to_file("$dir/$inpath", $input_txt);
  my @args = ("pytwine", "$dir/$inpath", "$dir/$outpath");
  DEBUG and print STDERR "running cmd '@args'\n";
  my $res = system (@args);
  $res == 0
    or die "system @args failed: $?";

  assert( -f "$dir/$outpath", "output file $dir/$outpath should now exist");
  my $actual_output = slurp("$dir/$outpath");

  is($actual_output, $input_txt, "should get out == in w/ cli args infile $inpath, outfile '$outpath'");
}

# args: a normal infile path and outfile path using --output twine_output_option
sub twine_output_option {
  my $inpath    = shift;
  my $outpath   = shift;
  my $dir       = tempdir("pytwine-tmp-XXXXXXXXXX", CLEANUP => 1, TMPDIR => 1 );
  my $input_txt = "foo";

  # run twine
  dump_to_file("$dir/$inpath", $input_txt);
  my @args = ("pytwine", "--output", "$dir/$outpath", "$dir/$inpath");
  DEBUG and print STDERR "running cmd '@args'\n";
  my $res = system (@args);
  $res == 0
    or die "system @args failed: $?";

  assert( -f "$dir/$outpath", "output file $dir/$outpath should now exist");
  my $actual_output = slurp("$dir/$outpath");

  is($actual_output, $input_txt, "should get out == in w/ cli args infile $inpath, --output '$outpath'");
}

my @infiles = ("", "''", "-", "/dev/stdin");
my @outfiles = ("", "''", "-", "/dev/stdout");

plan tests => scalar @infiles + scalar @outfiles + 2;

foreach my $infile (@infiles) {
  twine_from_stdinlike($infile);
}

foreach my $outfile (@outfiles) {
  twine_to_stdoutlike($outfile);
}

# and one usage where we specify both input _and_ output
twine_inout_filenames("someinfile.txt", "someoutfile.txt");
twine_output_option("someinfile.txt", "someoutfile.txt");

