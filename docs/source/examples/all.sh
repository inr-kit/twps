#!/bin/bash -l

rm -rf *.res.t
rm -rf log.*.t

echo "$ ppp.py" > message.txt
ppp.py >> message.txt

for t in $(ls *.t); do
    echo "---------- $t --------------------------"
    ppp.py $t > log.${t}
done

mv -f param1.res.t param1.res0.t

ppp.py -'a = 5' param1.t > log.param1-.t
ppp.py --'a 5 6' --'b "a" "b"' param2.t > log.param2-.t


