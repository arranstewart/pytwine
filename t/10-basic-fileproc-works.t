use strict;
use warnings;

use File::Basename;
use Test::More;
use IPC::Open2;
use Data::Dumper;
use File::Temp qw/ tempfile tempdir /;
use Carp::Assert;

assert( $ARGV[0] eq "--source-dir" );
my $source_dir = $ARGV[1];
my @testfiles = glob "${source_dir}/tests/files/*.pmd";

sub trim { my $s = shift; $s =~ s/^\s+|\s+$//g; return $s };

# Are we running on windows?
my $windows=($^O=~/Win/)?1:0;

my $devnull="/dev/null";
if ($windows) {
  $devnull = "nul";
}

assert( scalar @testfiles >= 1, "should be at least 1 .pmd test file" );

plan tests => scalar @testfiles * 2;

sub slurp {
  my $infile = shift;
  open my $fh, '<', $infile or die "Can't open file $!";
  my $conts = do { local $/; <$fh> };
  return $conts;
}

# each pmd has an .md file w/ expected
# output
sub markdown_filename {
  my $pmd_file = shift;
  my ($name,$path,$suffix) = fileparse($pmd_file,(".pmd"));
  return "${path}/${name}.md";
}

foreach my $testfile (@testfiles) {
  my $test_res = `pytwine $testfile 2>$devnull`;
  if ($testfile =~ /bad/) {
    ok( $? != 0, "script gave error, as expected");
  } else {
    ok( $? == 0, "script ran ok");
  }
  my $md_file = markdown_filename($testfile);
  my $expected = slurp($md_file);
  is($test_res, $expected, "expected result for ${testfile}");
}


