import re,html,sys
sys.stdout.reconfigure(encoding='utf-8')
t=open(sys.argv[1],encoding='utf-8').read()
for m in re.finditer(r'class="(run-msg|run-err|result-t)">(.*?)</div>',t): print(m.group(1), html.unescape(re.sub('<[^>]+>','',m.group(2)))[:140])
