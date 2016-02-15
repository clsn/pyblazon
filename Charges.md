# Charges #

Charges, broadly speaking, are the pictures and shapes and whatever that go
on a shield.  On one hand, this is a very broad category and the myriad
pictures that are charges are what give shields their distinctive
character.  On the other hand, from a computing point of view, one charge
is a lot like another, and trying to deal with lots of them is more of a
headache than an enlightening programming challenge.

pyBlazon understands some simple geometric charges, and has various ways to
use pictures from anywhere else on the web as charges too, without changing
the syntax of the blazon (much).  Here are some typical charges:

| _Roundel_ | _Annulet_ | _Lozenge_ | _Billet_ | _Crescent_ |
|:----------|:----------|:----------|:---------|:-----------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/or_a_roundel_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_a_roundel_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_an_annulet_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_an_annulet_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_a_lozenge_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_a_lozenge_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_a_billet_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_a_billet_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_a_crescent_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_a_crescent_azure.png) |

Charges are blazoned like we saw with [Ordinaries](Ordinaries.md).  The shields above were
blazoned _Or a roundel azure_, and so forth.  The color **follows** the
charge (in general, adjectives in blazonry tend to **follow** the nouns, and
not precede them as in normal English).  And the charge can be colored in
more complicated ways, as in the examples in PartyPer.

Charges are often found in groups of more than one charge (of the same kind):

| _2 roundels_ | _5 annulets_ | _3 escutcheons_ | _6 billets_ | _7 mascles_ |
|:-------------|:-------------|:----------------|:------------|:------------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/or_2_roundels_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_2_roundels_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_5_annulets_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_5_annulets_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_3_escutcheons_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_3_escutcheons_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_6_billets_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_6_billets_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_7_mascles_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_7_mascles_azure.png) |

As you can see, the charges are arranged in some fashion when there is more
than one of them.  There is a default arrangement, at least for fairly
small numbers of charges (less than ten, say); the examples here show some
of them.  You can also specify other arrangements, either by shape or by
number per row:

| _Or 3 triangles in pale azure_ | _Or 4 escutcheons in bend azure_ | _Or 5 annulets in cross azure_ | _Or 5 billets in fess azure_ |
|:-------------------------------|:---------------------------------|:-------------------------------|:-----------------------------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/or_3_triangles_in_pale_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_3_triangles_in_pale_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_4_escutcheons_in_bend_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_4_escutcheons_in_bend_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_5_annulets_in_cross_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_5_annulets_in_cross_azure.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_5_billets_in_fess_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_5_billets_in_fess_azure.png) |
| _Or 7 mullets azure 1 4 and 2_ | _Or 6 fleurs-de-lis azure 2 2 and 2_ | _Or 5 roundels azure 1 1 and 3_ | _Or 4 annulets azure 3 and 1_ |
| ![http://pyblazon.googlecode.com/svn/wiki/img/or_7_mullets_azure_1_4_and_2.png](http://pyblazon.googlecode.com/svn/wiki/img/or_7_mullets_azure_1_4_and_2.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_6_fleurs-de-lis_azure_2_2_and_2.png](http://pyblazon.googlecode.com/svn/wiki/img/or_6_fleurs-de-lis_azure_2_2_and_2.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_5_roundels_azure_1_1_and_3.png](http://pyblazon.googlecode.com/svn/wiki/img/or_5_roundels_azure_1_1_and_3.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_4_annulets_azure_3_and_1.png](http://pyblazon.googlecode.com/svn/wiki/img/or_4_annulets_azure_3_and_1.png) |

See how it works?

(Just a quick word about _mullets_: by default, a mullet is a five-pointed
star.  But you can also say _mullet of six points_, or _mullet of seven
points_ and so on, for any number from three through twelve.)


---


## Image Charges ##

You can use any image on the web (GIF, PNG, JPG, etc) as a charge and
pyBlazon will do its level best.  The image will be scaled to the size a
charge would be (so, smaller when there are many charges, larger when only
one or two, etc), placed in position, and an attempt will be made to color
it according to the treatment you specify.  Note that all these operations
are fraught with potential problems and errors, so adjust your expectations
accordingly.

When it comes to scaling the pictures, remember that pyBlazon produces SVG
files, "Scalable Vector Graphics."  As the name implies, these pictures are
intended to be scaled up and down.  And because they specify the picture in
terms of lines and curves and colors, and not in terms of an array of
pixels, you can scale them as large as you want and they will remain sharp,
and not get fuzzy like ordinary images do when you make them very large.
But if you include an ordinary image as a charge, that image will be
subject to normal fuzzing if it is scaled up big.  This might not be a
problem if the source picture is big to start with, and/or if the size you
show the shield is small, but you should be aware of it.

Another thing to remember is that web images are rectangular, but most
charges are not.  pyBlazon can't generally tell that you want only some of
your picture shown, so you might wind up with backgrounds behind your
images.  There is a way to avoid this, though.  You have to make sure the
images you are including have their backgrounds **transparent**.  This can be
done with GIF and PNG files, though JPG files cannot be made transparent.
If a picture has transparent parts, those parts will be properly treated as
"missing" and not colored in by pyBlazon when it colors the charge.

Speaking of coloring the charge, this is done by coloring an area with the
treatment you specify (color, fur, complex multicolor treatment, whatever)
and masking it with the image.  So the image's own colors still have an
effect; only where the image is white is the color you specify shown
through unaltered.  Usually this is what you want, but just realize that is
what's going on.  To indicate that an image charge should be shown with no
change to its natural color, blazon its color as "proper", as in _Or a_
<`http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif`> _proper_.  Technically,
you can get the same result by using _argent_, but that relies on some
coincidences that might not always be there.

To use an external image as a charge, enclose the URL with <> signs.

| _Ermine a_ <`http://us.i1.yimg.com/us.yimg.com/i/ww/beta/y3.gif`> _proper_ | _Azure six_ <`http://quality.mozilla.org/files/qmo_firefox_logo.png`> _proper_ | _Or two_ <`http://www.kli.org/pics/KLIlogo.gif`> _per saltire gules and azure_ |
|:---------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|
| ![http://pyblazon.googlecode.com/svn/wiki/img/ermine_a_Yahoo_proper.png](http://pyblazon.googlecode.com/svn/wiki/img/ermine_a_Yahoo_proper.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/azure_6_FF_proper.png](http://pyblazon.googlecode.com/svn/wiki/img/azure_6_FF_proper.png) | ![http://pyblazon.googlecode.com/svn/wiki/img/or_2_KLI_per_saltire_gules_and_azure.png](http://pyblazon.googlecode.com/svn/wiki/img/or_2_KLI_per_saltire_gules_and_azure.png) |

## On to [Charges on Charges and Ordinaries](ChargesOnCharges.md) ##