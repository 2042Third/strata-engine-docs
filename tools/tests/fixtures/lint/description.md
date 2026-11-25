The description is one sentence of at most 160 characters, in double quotes (style.md §6.1).

%%% pass core/time description="What_the_page_teaches."
A page.

%%% fail core/time key:description description="Two_sentences._Here."
A page.

%%% fail core/time key:description description=Unquoted.
A page.
