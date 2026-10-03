import sys; sys.path.insert(0,'.'); sys.stdout.reconfigure(encoding='utf-8')
import build
r=build.Runner(); r.reset()
for q in sys.argv[1:]:
    print('>>',q[:90]); res=r.run(q)[0]
    if res: print(res[0]); [print(x) for x in res[1][:25]]
r.cur.execute("DROP DATABASE IF EXISTS zz_lecture_build")
