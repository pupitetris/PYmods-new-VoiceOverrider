import imp
import json
import sys

file_path = sys.argv[1]
module = imp.load_source('module.name', file_path)

print json.dumps(module.I18N, indent=4, sort_keys=True, ensure_ascii=False, encoding='utf-8', separators=(',', ': '))
