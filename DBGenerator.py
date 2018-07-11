from tinydb import TinyDB
import pandas as pd
import sys

def generate(df, output="db.json"):
  db = TinyDB(output)
  for location in df.to_dict('records'):
    db.insert(location)
  
  print("完了")

if __name__ == "__main__":
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    try:
      df = pd.read_csv(filename)
    except FileNotFoundError:
      exit()
    
    if len(sys.argv) > 2:
      output = sys.argv[2]
      generate(df, output)
    else:
      generate(df)

  else:
    print("csvファイルを指定してください")