import slqite3 as sql


# +79631403588
# SlavaAlekseev228_

# https://github.com/rootint/jumoreski_api

# keywords : string -> words to search
# contains_img : int -> 0 - no image,
#                       1 - need image,
#                       2 - may need image
# search_type : string -> random / new / best
#                         (best => max by: views // (likes + reposts))
# likes : int -> at least this many likes
# reposts : int -> at least this many reposts
# safe : int -> 0 - with cussing,
#               1 - no cussing,
#               2 - censored cussing
# max_words : int -> maximum words
# fetch : int -> fetch this many
