#!/bin/bash

python3 -c "
import json
events = json.load(open('/app/data.json'))
n = sum(1 for e in events if e['status'] == 'error')
open('/app/answer.txt', 'w').write(str(n))
"
