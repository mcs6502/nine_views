# nine_views

This project is centred around the poem _"Nine Views of Mount Fuji"_ by Mike Keith. The poem is noteworthy because it contains a striking example of the so-called "constrained writing"—its words are carefully chosen to obey a predefined set of rules. Taken as a whole, the poem creates a pattern—in fact, more than one pattern. The poem's text is available on the web [1]. That page includes nine woodblock views forming the basis of the poem, and explains the detailed constraints for composing it.  There is also another page [2], focussing on the poem's anagrammatic nature.

The script `nine_views.py` fetches the text of the poem  from its web page and prints it on standard output. Invoked with the `-d` option, the script analyses the poem's words and outputs the results of this analysis as a bitmap. (Its output is valid code in kdb+/q format.)

The script `print_views.py` can display one or more parallel projection views of the output from the decoding script.

The two can be combined in the following way:
~~~~
python nine_views.py -d https://web.archive.org/web/20090718073218/http://www.farragoswainscot.com/2009/11/nine_views.html | python print_views.py --view "front-180 right+90" --view "top right+90"
~~~~

On the face value, the scripts don't do much; however, they can serve as a quick template for creating scraper-like projects, which need to parse something fetched from the web and then potentially have it processed using a numpy algorithm.

[1]: http://www.farragoswainscot.com/2009/11/nine_views.html
[2]: https://www.anagrammy.com/literary/mkeith/poems-dom19.html

Copyright 2019, mcs6502