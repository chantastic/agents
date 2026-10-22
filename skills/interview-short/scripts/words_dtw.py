import json,sys
d=json.load(open(sys.argv[1]))
words=[]
for s in d['transcription']:
    for t in s['tokens']:
        tx=t['text']
        if tx.startswith('[_') or tx.startswith('<|'): continue
        td=t.get('t_dtw',-1)
        a=td/100 if td>=0 else t['offsets']['from']/1000
        if tx.startswith(' ') or not words: words.append([a,a,tx.strip()])
        else: words[-1][2]+=tx
for i in range(len(words)-1): words[i][1]=words[i+1][0]
json.dump(words,open(sys.argv[2],'w'))
