#!/usr/bin/env perl

# tests whether we can use `pip install` to install from
# a github branch.

# takes one arg, a branch to use (else uses "master" as default)

# if it finds the variable PERSONAL_TOKEN defined, it uses that as a token
# to get to github; else if looks for a file TOKEN in the working dir;
# else it does no authentication.

use strict;
use warnings;
use File::Temp "tempdir";

sub slurp {
  my $infile = shift;
  open my $fh, '<', $infile or die "Can't open file $!";
  my $conts = do { local $/; <$fh> };
  return $conts;
}

# get auth header to use with curl from either:
#   environment var PERSONAL_TOKEN,
# or
#   contents of a file in current dir called "TOKEN"
# else returns an empty string.
sub get_curl_auth_header {
  if (exists $ENV{"PERSONAL_TOKEN"} && $ENV{"PERSONAL_TOKEN"} ne "") {
    my $token=$ENV{"PERSONAL_TOKEN"};
    print STDERR "using personal token from \$PERSONAL_TOKEN\n";
    return "Authorization: Bearer $token";
  } elsif (-f "TOKEN") {
    my $token=slurp("TOKEN");
    print STDERR "using token file\n";
    return "Authorization: token $token";
  } else {
    print STDERR "no token found\n";
    return "";
  }
}


# first arg is a string message, rest are args for `system`
sub verbose_system_or_die {
  my $message = shift;
  my @args = @_;
  print STDERR "running '@args'\n";
  system(@args) == 0
    or die "$message: $?";
}

sub dir_conts {
  my $dir = shift;
  opendir DIR,$dir;
  my @dir = readdir(DIR);
  close DIR;
  my @results = ();
  foreach my $entry (@dir){
    push @results, $entry;
  }
  return @results;
}

my $numargs = scalar @ARGV;

if ($numargs > 1) {
  die 'expected 0 or 1 args (branch name), got $numargs';
}

my $branch="master";
if ($numargs == 1) {
  $branch=$ARGV[0];
}

my $repo    = "https://github.com/arranstewart/pytwine";
my $path    = "archive/refs/heads/${branch}.zip";
my $url     = "${repo}/${path}";
my $auth_header = get_curl_auth_header();
my $tmpdir  = tempdir("pytwine-zip-install-tmp-XXXXXXXXXX", CLEANUP => 1, TMPDIR => 1);
my $zipfile = "$tmpdir/pytwine.zip";

my @curl_args=(qw(curl --silent --show-error --fail -L -o), $zipfile, $url);
if ("$auth_header") {
  push(@curl_args, ("-H", "$auth_header"));
}

verbose_system_or_die
  "couldn't download pytwine.zip with 'curl'",
  @curl_args;

verbose_system_or_die
  "downloaded pytwine.zip doesn't look like a zipfile",
  qw(unzip -q -t), $zipfile;

# just to ensure we don't pick up anything in local dir
chdir $tmpdir;

verbose_system_or_die
  "couldn't install zip file with 'pip'",
  qw(python3 -m pip install), "file://$tmpdir/pytwine.zip";

verbose_system_or_die
  "couldn't invoke installed 'pytwine' script",
  qw(pytwine --help);

