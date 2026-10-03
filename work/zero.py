import re,html,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open(sys.argv[1],encoding='utf-8').read()
r=s[s.find('id="review"'):]
for m in re.finditer(r'ผลลัพธ์ \(0 แถว',r):
    pre=r.rfind('<pre class="sql">',0,m.start())
    print('ZERO:',html.unescape(re.sub('<[^>]+>','',r[pre:pre+400])).replace('\n',' ')[:160])
