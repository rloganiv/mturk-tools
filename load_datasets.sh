DIR=${HOME}/projects/nonevent/data
mtools-cli load-dataset -e right $DIR/shuffled_sents_articles_1s.jsonl
# mtools-cli load-dataset -e right $DIR/tfidf_articles.jsonl
mtools-cli load-dataset -e no_context $DIR/switch_srl_manual.jsonl
mtools-cli load-dataset -e right $DIR/atomic_shuf.jsonl
mtools-cli load-dataset -e right $DIR/noun_compounds.jsonl
mtools-cli load-dataset -e left $DIR/story_cloze_2018_val.jsonl
