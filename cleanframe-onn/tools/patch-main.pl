#!/usr/bin/env perl
# The port's edits to upstream's main.js: lift the nine-app Home limit, let
# HOME return to the home stage, and relabel "Samsung Home" as Google TV.
#
# This is the one place the port edits upstream's main.js instead of using it
# verbatim. Upstream caps Home at 9 because the "Apps on Home" editor draws the
# Home column as a fixed, non-scrolling list that holds exactly nine rows. The
# dock and the list layout already scroll at any length. So this raises the cap
# and teaches the editor's Home column to scroll with the focused row.
#
# Every replacement must match exactly once. If upstream changes any of these
# lines the script dies, and sync-upstream.sh fails, rather than shipping a
# half-patched UI.
#
# Usage:  tools/patch-main.pl path/to/main.js
use strict;
use warnings;

my $HOME_CAP = 24;

my $path = shift or die "usage: patch-main.pl path/to/main.js\n";
open(my $in, '<:raw', $path) or die "cannot read $path: $!\n";
my $src = do { local $/; <$in> };
close($in);

sub swap {
    my ($what, $old, $new) = @_;
    my $count = () = $src =~ /\Q$old\E/g;
    die "patch-main: '$what' matched $count times, expected 1. Upstream changed; review before patching.\n"
        unless $count == 1;
    $src =~ s/\Q$old\E/$new/;
}

swap('cap',
    q{var CAP = 9, SCRIM_Y},
    qq{var CAP = $HOME_CAP, SCRIM_Y});

swap('full message',
    q{var FULL = 'Home holds nine apps. Remove one first.'},
    q{var FULL = 'Home holds ' + CAP + ' apps. Remove one first.'});

# Scroll offset for the editor's Home column, kept on the view state as hTop.
swap('editor break',
    q{el['break'].className = 'ed-order-break' + (H.length > editorCut() ? ' is-on' : '');},
    q{var hTop = t.hTop || 0, hY = editorHomeY(clamp(f.i, 0, Math.max(0, H.length - 1)));}
    . q{ if (f.zone === 'home' || t.lifted) { if (hY < hTop) hTop = hY - (f.i === editorCut() ? 24 : 0); if (hY + 72 > hTop + ED_VIEW) hTop = hY + 72 - ED_VIEW; }}
    . q{ hTop = clamp(hTop, 0, Math.max(0, editorHomeY(H.length - 1) + 72 - ED_VIEW)); t.hTop = hTop;}
    . q{ el['break'].className = 'ed-order-break' + (H.length > editorCut() && editorCut() * ED_ROW >= hTop ? ' is-on' : '');});

swap('editor break top',
    q{el['break'].style.top = (264 + editorCut() * ED_ROW) + 'px';},
    q{el['break'].style.top = (264 + editorCut() * ED_ROW - hTop) + 'px';});

swap('editor row position',
    q{row.style.transform = 'translate3d(' + (lifted ? 16 : 0) + 'px,' + editorHomeY(i) + 'px,0)';},
    q{row.style.transform = 'translate3d(' + (lifted ? 16 : 0) + 'px,' + (editorHomeY(i) - hTop) + 'px,0)';}
    . q{ row.style.visibility = editorHomeY(i) >= hTop && editorHomeY(i) + 72 <= hTop + ED_VIEW ? 'visible' : 'hidden';});

swap('editor origin marker',
    q{(264 + editorHomeY(t.lifted.from) + 16) + 'px,0)';},
    q{(264 + editorHomeY(t.lifted.from) - hTop + 16) + 'px,0)';});

# HOME must return to the home stage from anywhere, silently. Upstream only
# has BACK, which at the top level asks "Leave Home?". goScene() already does
# the reset; expose it so device.js can call it for the HOME key.
swap('expose goScene',
    'function fit() {',
    'window.__cleanframeScene = goScene; function fit() {');

# Upstream's labels name the Samsung home screen. Here that control opens the
# Google TV home screen, so say so. Display strings only; ids are lowercase
# 'samsung' and are left alone.
sub relabel {
    my ($old, $new) = @_;
    my $count = () = $src =~ /\Q$old\E/g;
    die "patch-main: label '$old' not found. Upstream changed; review before patching.\n"
        unless $count >= 1;
    $src =~ s/\Q$old\E/$new/g;
}
relabel(q{Samsung Home}, q{Google TV Home});
relabel("Samsung\xe2\x80\x99s Home screen", "the Google TV Home screen");
relabel(q{'Samsung'}, q{'Google TV'});

open(my $out, '>:raw', $path) or die "cannot write $path: $!\n";
print $out $src;
close($out);
print "patch-main: Home cap $HOME_CAP, editor scrolls, HOME hook exposed, labels say Google TV\n";
