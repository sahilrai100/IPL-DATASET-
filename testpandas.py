import pandas as pd

print("Testing Pandas...")
df = pd.read_csv('matches.csv')

print(f"✅ Total rows: {len(df)}")
print(f"✅ Columns: {list(df.columns)[:5]}...")
print("\n✅ First 3 rows:")
print(df.head(3))

mi_matches = df[df['team1'] == 'Mumbai Indians']
print(f"\n✅ Mumbai Indians matches: {len(mi_matches)}")

print("\n🎉 PANDAS TEST PASSED!")