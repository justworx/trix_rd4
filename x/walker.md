

```python3

from trix.x.walker import *
w = Walker("trix")
w.path
w.pathlist
w.filelist
w.dirlist

```

Here's where I'm getting lost. I need to find a convenient way to 
call the thing - to access complex features on two levels. The 
pathlist, filelist, and dirlist lists have to feed deeper algorithms
so maybe something like this...

```
w.query(w.files, selector_function)
```

...where the selector function is one of a set of classmethods for
querying each directory's files (or directories) and generating a
result.




