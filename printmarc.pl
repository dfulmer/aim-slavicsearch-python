#!/usr/local/bin/perl

use File::Basename;
my $prgname = basename($0);
if ($#ARGV < 0) { die "usage: $prgname filename(s)\n"; }

use MARC::Batch;
use MARC::Lint;
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my $batch = MARC::Batch->new('USMARC',@ARGV);
my $linter = MARC::Lint->new();

my %filereccnt;
my $reccnt=0; my $outcnt=0;
$batch->strict_off();
record: while (my $record = $batch->next() ) {
  my $currentfile = $batch->filename();
  $reccnt++;
  $filereccnt{$currentfile}++;
  if ($#ARGV > 0) { print "$reccnt--$currentfile($filereccnt{$currentfile})\n"; }
  else { 
    print "RECORD $reccnt\n";
    #print stderr "RECORD $reccnt\n";
  }
  printMarc($record,"STDOUT");
  print "\n";

}
  
print STDERR "$prgname--@ARGV\n";
print STDERR "$reccnt records read\n";
print STDERR "\n";

sub printMarc {
  my $record = shift;
  my $filehandle = shift;
  if (!defined($filehandle)) { $filehandle = STDOUT; }
  my @fields = $record->fields();

  ## print out the tag, the indicators and the field contents
  print $filehandle "LDR ",$record->leader(),"\n";
  foreach my $field (@fields) {
    print $filehandle $field->tag(), " ";
    if ($field->tag() lt '010') { print $filehandle "   ",$field->data; }
    else {
      print $filehandle $field->indicator(1), $field->indicator(2), " ";
      my @subfieldlist = $field->subfields();
      foreach $sfl (@subfieldlist) {
        print $filehandle "|".shift(@$sfl).shift(@$sfl);
      }
    }
    print $filehandle "\n";
  }
  return;
}