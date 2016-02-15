# Hacks #

You can mis-/ab-use pyBlazon's features—and bugs—to get results that ordinary blazonry can't get you...

# Examples #

  * **proper**: Blazoning something as "proper" really means not to fill it in with anything.  For external raster images, this is often the Right Thing to do, and means what it should in a blazonry context: use the colors you're given.  But for ordinary charges, it winds up making them invisible; their "fill" is set to none.  This can be handy for making groups of charges.  See below...

  * **area**: There is an unofficial charge called an "area" ("field" already was being used in the grammar for something else), which is basically a huge rectangle (about the size of the entire field).  Use this with "proper" as described above, and you can do things like _or three areas proper each charged with three shakeforks sable_ to get the shakeforks in little groups.  Insert more iterations of areas proper for greater and greater fractal effect.  This is now outdated by the use of "groups", which accomplishes the same thing (even using "area" charges internally): _or three groups of three shakeforks sable_ and so on.  You can also use this for making complex semy fields, using "groups" too: _argent semy of groups of four roundels gules 1 2 and 1_.

  * **0**: The number-word "zero" is not understood, but you can specify the digit 0 as a number.  This can be convenient for messing with the sizes and placements of arrangements of charges, as in _sable seven plates 0 1 2 0 1 and 3_.

  * **_Treatment Abuse_**: The parser is pretty free about what you can provide as the "field treatments" composing a party per pale/fess/etc , or barry/paly/bendy, etc.  So you can say things like _per pale barry or and azure and barry azure and or_ to get a barry shield that's countercharged per pale.  Or you can use the `lp` and `rp` special tokens that act like parentheses and say _barry of six lp barry of twelve or and azure rp and lp barry of twelve argent and gules rp_ to get a barry treatment of four colors.  You can use this hack to  get you things like "per pale and per chevron" or "per cross per fess indented" or other tricks which the grammar does not support.