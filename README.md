
    
    Copyright 2018 justworx
    This file is part of the trix project, distributed under
    the terms of the GNU Affero General Public License.
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    


# trix

This is the fourth rough draft. There's always more coming soon and a
lot of long-term plans for the future. I want to publish this now 
because I think some of it might be useful as-is, and because I don't
want to lose it all in a fire or whatever.


#### under construction!

Everything in this trix package should be considered to be "Under 
Construction", subject to change, and potentially buggy.


#### rd4 (or, notes and observations to self)

As I've mentioned, this is the fourth rough draft of the trix package. 
New drafts are always a result of some technical problem I wanted to 
solve by starting over. In this case, I screwed up my local repository
and don't want the hassle of unscewing it. Anyway, several changes
- changes that affect many classes - are needed, so it's a good time 
for it.

The trix package is probably going to look pretty bare for a while,
but I've renamed the old project to trix.rd3 - the last decent
push is there. I'll probably leave it there a while because my irc
bot runs well under it. Eventually, though, after this draft is able
to provide the same or better service, I'll delete rd3.


###### the plan for rd4 (or, more notes to self)

My plan is to get the relatively independent parts added to rd4 asap,
then carefully reconstruct the util/Runner class, which I feel is
causing some deep-rooted problems. I'd also like to change the way
command-line features are run, placing them in an `app` class rather
than having them run in individual processes. This may seem (and may
even be) silly, but I think it is conducive to my ultimate goals for
the project.

The project also craves a really effective test suite.

Finally, there are some recent improvements that have been applied to
newer classes but are not present in older ones - I'm hoping to apply
these new features globally as I reimport the contents of rd3 to the 
current trix (rd4) package. 


#### the `x` subpackage

Everything within the `x` subpackage is experimental, temporary,
under construction, or just being held for spiritual eqanimity. None
of it should be used in a real app because it's probably especially
buggy and otherwise untrustworthy in comparison to the other packages,
which themselves are a normal level of buggy and untrustworthy.

PLEASE READ AND UNDERSTAND THE "trix/x/README-X" FILE BEFORE USING 
ANYTHING WITHIN THE `x` SUBPACKAGE.


#### doc

Documentation is under construction and is (or soon will be) at:
<https://github.com/justworx/trix/wiki>


#### thanks

Thanks to everyone who's helped me out on this project:

 * jotun, for the binary search function for ucd lists.
 * mknod, for the unicode info and advice. WORD!

