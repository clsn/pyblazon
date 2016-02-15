# Introduction to Blazonry #

Blazonry is a stylized jargon for describing coats of arms.  In this site,
we will be dealing with describing shields in particular, but blazonry also
applies to the larger "achievement" of arms, including mottos, supporters,
crests, etc.

The point of blazonry is to provide a description of a shield that is
detailed enough to enable someone to draw a picture of it (maybe not a
perfect one) that does not differ from the original in any "significant"
way.  The nature of "significant" of course relies on the rules of
heraldry.

Blazonry has been compared to a primitive programming language, or maybe a
markup language like HTML or a drawing language like PostScript or SVG
would be closer.  And indeed, that is what this project is all about:
translating blazonry (or a subset thereof) into SVG.

This introduction to blazonry will be focussing on what pyBlazon can do,
and even within that it will not be exhaustive.  You'll have to learn more
blazonry to explore more of the features of pyBlazon; I'm just giving you
an idea so you can express some simple designs and understand some simple
blazons.  The blazonry taught here is specifically what pyBlazon can
understand, but it is also (except for a few obvious features) valid,
ordinary blazonry, so the blazonry skills you learn from these pages _are_
applicable to blazonry you might see and describe to other people. All the
examples shown have been rendered by pyBlazon.

# Tinctures and Treatments #

A shield is always "blazoned" or described starting with the background,
and working up in notional layers as charges are drawn on it and on each
other.  So the first thing in any blazon will be what the background of the
shield looks like.

The simplest background is a solid color.  The colors in blazonry have
special names:

| _Or_ | _Argent_ | _Sable_ | _Gules_ | _Azure_ | _Vert_ | _Purpure_ |
|:-----|:---------|:--------|:--------|:--------|:-------|:----------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/or.png](http://pyblazon.googlecode.com/svn/wiki/img/or.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/argent.png](http://pyblazon.googlecode.com/svn/wiki/img/argent.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/sable.png](http://pyblazon.googlecode.com/svn/wiki/img/sable.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/gules.png](http://pyblazon.googlecode.com/svn/wiki/img/gules.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/azure.png](http://pyblazon.googlecode.com/svn/wiki/img/azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/vert.png](http://pyblazon.googlecode.com/svn/wiki/img/vert.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/purpure.png](http://pyblazon.googlecode.com/svn/wiki/img/purpure.png) |

Real mediæval heraldry uses the first five colors listed above more
frequently _by far_ than the others.  Rarely does a single shield have more
than three colors.  There are some lesser-used tinctures that pyBlazon
understands:

| _Bleu Celeste_ | _Tenne_ | _Sanguine_ | _Murrey_ | _Rose_ | _Copper_ |
|:---------------|:--------|:-----------|:---------|:-------|:---------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/bleuC.png](http://pyblazon.googlecode.com/svn/wiki/img/bleuC.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/tenne.png](http://pyblazon.googlecode.com/svn/wiki/img/tenne.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/sanguine.png](http://pyblazon.googlecode.com/svn/wiki/img/sanguine.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/murrey.png](http://pyblazon.googlecode.com/svn/wiki/img/murrey.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/rose.png](http://pyblazon.googlecode.com/svn/wiki/img/rose.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/copper.png](http://pyblazon.googlecode.com/svn/wiki/img/copper.png) |

**News:** as of pyBlazon release 307 (January 2009), you can also specify a color by using its “html” code, of the form **#xxxxxx** where each **x** is a hexadecimal digit, and the six digits specify the color with two digits each of <font color='red'>red</font>, <font color='green'>green</font>, and <font color='blue'>blue</font> in that order.  So you can get a cyan cross on a magenta field with _#ff00ff a cross #00ffff_.

There is a rule in heraldry that "metals" (_Or_ and _Argent_) should not
touch other metals, and "tinctures" (the other colors) should not touch
other tinctures; _i.e._, metals only touch tinctures and vice-versa.  But
that rule starts to get strange when dealing with furs (see below), and it
was not always observed even in mediæval times, so don't stress too much.
pyBlazon won't care.

## Furs ##

Other "solid" treatments of the field (or charges) are called "furs":

| _Ermine_ | _Ermines_ | _Erminois_ | _Pean_ | _Vair_ |
|:---------|:----------|:-----------|:-------|:-------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/ermine.png](http://pyblazon.googlecode.com/svn/wiki/img/ermine.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/ermines.png](http://pyblazon.googlecode.com/svn/wiki/img/ermines.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/erminois.png](http://pyblazon.googlecode.com/svn/wiki/img/erminois.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/pean.png](http://pyblazon.googlecode.com/svn/wiki/img/pean.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/vair.png](http://pyblazon.googlecode.com/svn/wiki/img/vair.png) |

You can also generalize these patterns by saying things like _Or ermined
gules_ (for ermine-style furs) or _Vairy or and sable_ (for vair-style).
There are also some other variants of vair recognized, and other
alterations you can do to the colors:

| _Or ermined gules_ | _Vairy or and sable_ | _Counter-vair_ | _Vair in pale_ | _Or fretty gules_ | _Or masoned gules_ |
|:-------------------|:---------------------|:---------------|:---------------|:------------------|:-------------------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/or_ermined_gules.png](http://pyblazon.googlecode.com/svn/wiki/img/or_ermined_gules.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/vairy_or_and_sable.png](http://pyblazon.googlecode.com/svn/wiki/img/vairy_or_and_sable.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/counter-vair.png](http://pyblazon.googlecode.com/svn/wiki/img/counter-vair.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/vair_in_pale.png](http://pyblazon.googlecode.com/svn/wiki/img/vair_in_pale.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_fretty_gules.png](http://pyblazon.googlecode.com/svn/wiki/img/or_fretty_gules.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_masoned_gules.png](http://pyblazon.googlecode.com/svn/wiki/img/or_masoned_gules.png) |

See how to combine these on the PartyPer page, or if you don't want to get
more complicated backgrounds but want to see how to place shapes **on** the
background, look at the [Ordinaries](Ordinaries.md) or [Charges](Charges.md) page.

## PartyPer -- for more complex treatments ##
## [Ordinaries](Ordinaries.md) -- for putting big shapes across the shield ##
## [Charges](Charges.md) -- for putting individual shapes and objects on the shield ##